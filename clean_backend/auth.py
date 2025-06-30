# Simplified Auth0 integration using the official SDK
import os
from fastapi_auth0 import Auth0

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "liquicity.us.auth0.com")
API_AUDIENCE = os.getenv("API_AUDIENCE", "https://api.liquicity.com")

auth0 = Auth0(domain=AUTH0_DOMAIN, api_audience=API_AUDIENCE)

# FastAPI dependency that returns the decoded JWT payload
get_current_user = auth0.get_user 