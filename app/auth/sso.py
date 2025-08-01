import os
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.utils.security import create_access_token
from datetime import timedelta
from app.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES

class SSOProvider:
    """Base class for SSO providers"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """Get user information from SSO provider"""
        raise NotImplementedError
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        raise NotImplementedError

class GoogleSSO(SSOProvider):
    """Google SSO implementation"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = response.json()
            return token_data.get("access_token")
    
    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """Get user information from Google"""
        access_token = await self.get_access_token(code)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            
            return response.json()

class MicrosoftSSO(SSOProvider):
    """Microsoft Azure AD SSO implementation"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant_id: str = "common"):
        super().__init__(client_id, client_secret, redirect_uri)
        self.tenant_id = tenant_id
        self.auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.user_info_url = "https://graph.microsoft.com/v1.0/me"
    
    def get_authorization_url(self) -> str:
        """Get Microsoft OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile User.Read",
            "response_type": "code"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = response.json()
            return token_data.get("access_token")
    
    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph"""
        access_token = await self.get_access_token(code)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Microsoft"
                )
            
            return response.json()

class GitHubSSO(SSOProvider):
    """GitHub SSO implementation"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_info_url = "https://api.github.com/user"
    
    def get_authorization_url(self) -> str:
        """Get GitHub OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = response.json()
            return token_data.get("access_token")
    
    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """Get user information from GitHub"""
        access_token = await self.get_access_token(code)
        
        async with httpx.AsyncClient() as client:
            # Get basic user info
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"token {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from GitHub"
                )
            
            user_data = response.json()
            
            # Get user email (might be private)
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {access_token}"}
            )
            
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next((email["email"] for email in emails if email["primary"]), None)
                if primary_email:
                    user_data["email"] = primary_email
            
            return user_data

class SSOManager:
    """Manager for SSO providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize SSO providers from environment variables"""
        # Google SSO
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/sso/google/callback")
        
        if google_client_id and google_client_secret:
            self.providers["google"] = GoogleSSO(google_client_id, google_client_secret, google_redirect_uri)
        
        # Microsoft SSO
        microsoft_client_id = os.getenv("MICROSOFT_CLIENT_ID")
        microsoft_client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        microsoft_redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/sso/microsoft/callback")
        microsoft_tenant_id = os.getenv("MICROSOFT_TENANT_ID", "common")
        
        if microsoft_client_id and microsoft_client_secret:
            self.providers["microsoft"] = MicrosoftSSO(
                microsoft_client_id, microsoft_client_secret, microsoft_redirect_uri, microsoft_tenant_id
            )
        
        # GitHub SSO
        github_client_id = os.getenv("GITHUB_CLIENT_ID")
        github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/sso/github/callback")
        
        if github_client_id and github_client_secret:
            self.providers["github"] = GitHubSSO(github_client_id, github_client_secret, github_redirect_uri)
    
    def get_provider(self, provider_name: str) -> Optional[SSOProvider]:
        """Get SSO provider by name"""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> list:
        """Get list of available SSO providers"""
        return list(self.providers.keys())
    
    async def authenticate_user(self, provider_name: str, code: str, db: Session) -> Dict[str, Any]:
        """Authenticate user via SSO provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SSO provider '{provider_name}' not configured"
            )
        
        # Get user info from SSO provider
        user_info = await provider.get_user_info(code)
        
        # Normalize user data based on provider
        email = self._extract_email(user_info, provider_name)
        username = self._extract_username(user_info, provider_name)
        full_name = self._extract_full_name(user_info, provider_name)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by SSO provider"
            )
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Update existing user
            user = existing_user
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is deactivated"
                )
        else:
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=UserRole.USER,  # Default role for SSO users
                is_active=True,
                sso_provider=provider_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "sso_provider": user.sso_provider,
                "created_at": user.created_at
            }
        }
    
    def _extract_email(self, user_info: Dict[str, Any], provider: str) -> Optional[str]:
        """Extract email from user info based on provider"""
        if provider == "google":
            return user_info.get("email")
        elif provider == "microsoft":
            return user_info.get("mail") or user_info.get("userPrincipalName")
        elif provider == "github":
            return user_info.get("email")
        return None
    
    def _extract_username(self, user_info: Dict[str, Any], provider: str) -> str:
        """Extract username from user info based on provider"""
        if provider == "google":
            return user_info.get("email", "").split("@")[0]
        elif provider == "microsoft":
            return user_info.get("userPrincipalName", "").split("@")[0]
        elif provider == "github":
            return user_info.get("login", "")
        return f"user_{user_info.get('id', 'unknown')}"
    
    def _extract_full_name(self, user_info: Dict[str, Any], provider: str) -> Optional[str]:
        """Extract full name from user info based on provider"""
        if provider == "google":
            return user_info.get("name")
        elif provider == "microsoft":
            return user_info.get("displayName")
        elif provider == "github":
            return user_info.get("name")
        return None

# Global SSO manager instance
sso_manager = SSOManager()
