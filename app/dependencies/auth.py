from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
if not AUTH0_DOMAIN or AUTH0_DOMAIN == 'none':
    AUTH0_DOMAIN = 'liquicity.us.auth0.com'  # Set a default domain if not provided
    print(f"⚠️ Using default Auth0 domain: {AUTH0_DOMAIN}")
API_AUDIENCE = os.getenv('API_AUDIENCE')
if not API_AUDIENCE:
    API_AUDIENCE = 'https://api.liquicity.com'  # Set a default audience if not provided
    print(f"⚠️ Using default API audience: {API_AUDIENCE}")
ALGORITHMS = ['RS256']

# Print configuration for debugging
print(f"🔑 AUTH0_DOMAIN = {AUTH0_DOMAIN}")
print(f"🎯 API_AUDIENCE = {API_AUDIENCE}")

# JWKS cache
_jwks_cache = None

def get_jwks():
    """Fetch JWKS from Auth0 with caching and error handling"""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
            logger.info(f"Fetching JWKS from {jwks_url}")
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
            logger.info("JWKS fetched successfully")
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}")
            # Provide empty JWKS structure instead of failing completely
            _jwks_cache = {"keys": []}
            print(f"⚠️ Failed to fetch JWKS from Auth0: {e}")
    return _jwks_cache

# Use HTTPBearer for Auth0-issued JWTs
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    jwks = get_jwks()
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
        logger.info(f"Successfully validated token for {payload.get('email', 'unknown user')}")
        # For KYC operations, we need just the email
        return payload.get('email', payload.get('sub'))
    except JWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation error: {str(e)}")

    