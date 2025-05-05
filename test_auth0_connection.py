import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_auth0_connection():
    # Get Auth0 configuration from environment variables with fallbacks
    auth0_domain = os.getenv('AUTH0_DOMAIN', 'liquicity.us.auth0.com')
    
    print("=== Auth0 Connection Test ===")
    print(f"Using Auth0 domain: {auth0_domain}")
    
    try:
        # Test connection to JWKS endpoint
        jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
        print(f"Testing connection to: {jwks_url}")
        
        response = requests.get(jwks_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Print JWKS keys (safely - just count and kids)
        jwks = response.json()
        keys = jwks.get('keys', [])
        
        print(f"Connection successful! Found {len(keys)} keys in JWKS.")
        if keys:
            print(f"Key IDs: {[key.get('kid') for key in keys]}")
        
        return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_auth0_connection() 