import os

import os

# Secret key for JWT encoding/decoding
SECRET_KEY = os.environ.get("SECRET_KEY", "lucho123")

# Algorithm used for JWT
ALGORITHM = "HS256"

# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30
