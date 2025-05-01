from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import AppConfig

# Auth0 configuration
import os, requests
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('API_AUDIENCE') or os.getenv('AUTH0_AUDIENCE')
ALGORITHMS = ['RS256']

# Fetch JWKS from Auth0
jwks = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").json()
# Use HTTPBearer for Auth0-issued JWTs
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Identify the signing key
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")
    rsa_key = {}
    for key in jwks.get('keys', []):
        if key['kid'] == unverified_header.get('kid'):
            rsa_key = {k: key[k] for k in ('kty','kid','use','n','e')}
            break
    if not rsa_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find appropriate key")
    # Decode and validate claims
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation error: {str(e)}")
    # At this point, 'payload' contains the user data
    return payload
    
