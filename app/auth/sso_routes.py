from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
from app.database.connection import get_db
from app.auth.sso import sso_manager
from app.schemas.user import Token
from pydantic import BaseModel

router = APIRouter(prefix="/auth/sso", tags=["sso-authentication"])

class SSOCallbackRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None

@router.get("/providers")
def get_available_sso_providers():
    """Get list of available SSO providers"""
    providers = sso_manager.get_available_providers()
    return {
        "providers": providers,
        "count": len(providers)
    }

@router.get("/{provider}/login")
def initiate_sso_login(provider: str):
    """Initiate SSO login for the specified provider"""
    sso_provider = sso_manager.get_provider(provider)
    if not sso_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO provider '{provider}' not configured"
        )
    
    # Get authorization URL
    auth_url = sso_provider.get_authorization_url()
    
    return {
        "provider": provider,
        "authorization_url": auth_url,
        "message": f"Redirect to {provider} for authentication"
    }

@router.get("/{provider}/authorize")
def redirect_to_sso_provider(provider: str):
    """Redirect user to SSO provider for authentication"""
    sso_provider = sso_manager.get_provider(provider)
    if not sso_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO provider '{provider}' not configured"
        )
    
    # Get authorization URL and redirect
    auth_url = sso_provider.get_authorization_url()
    return RedirectResponse(url=auth_url)

@router.get("/{provider}/callback")
async def sso_callback(
    provider: str,
    code: str = Query(..., description="Authorization code from SSO provider"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from SSO provider"),
    db: Session = Depends(get_db)
):
    """Handle SSO callback and redirect to frontend callback route"""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Always redirect to the frontend callback route with all parameters
    # The frontend will handle the authentication logic
    callback_url = f"{frontend_url}/auth/callback/{provider}"
    
    # Preserve all query parameters for the frontend to process
    params = []
    if code:
        params.append(f"code={code}")
    if error:
        params.append(f"error={error}")
    if state:
        params.append(f"state={state}")
    
    if params:
        callback_url += "?" + "&".join(params)
    
    return RedirectResponse(url=callback_url)

@router.post("/{provider}/callback")
async def sso_callback_post(
    provider: str,
    request_data: SSOCallbackRequest,
    db: Session = Depends(get_db)
):
    """Handle SSO callback via POST from frontend"""
    print(f"🔍 POST callback - Provider: {provider}, Code: {request_data.code[:10]}...")
    try:
        code = request_data.code
        if not code:
            print("❌ No authorization code provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )
        
        print(f"🔐 Attempting authentication with code: {code[:10]}...")
        token_data = await sso_manager.authenticate_user(provider, code, db)
        print(f"✅ Authentication successful for user: {token_data['user']['username']}")
        return {
            "token": token_data['access_token'],
            "user": token_data['user']
        }
    except HTTPException as he:
        print(f"❌ HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        print(f"❌ General Exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SSO authentication failed: {str(e)}"
        )

@router.post("/{provider}/authenticate", response_model=Token)
async def authenticate_with_sso(
    provider: str,
    code: str,
    db: Session = Depends(get_db)
):
    """Authenticate user with SSO provider using authorization code"""
    try:
        token_data = await sso_manager.authenticate_user(provider, code, db)
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SSO authentication failed: {str(e)}"
        )
