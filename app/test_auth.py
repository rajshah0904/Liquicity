import os
import requests
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Get Auth0 configuration from environment variables with fallbacks
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'liquicity.us.auth0.com')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'https://api.liquicity.com')

def test_auth0_connection():
    """Test connection to Auth0 JWKS endpoint"""
    print("\n=== Auth0 Connection Test ===")
    print(f"Using AUTH0_DOMAIN: {AUTH0_DOMAIN}")
    print(f"Using API_AUDIENCE: {API_AUDIENCE}")
    
    # Create .env.development if not exists with development values
    if not os.path.exists('.env.development'):
        print("\nCreating .env.development file for fallback values...")
        with open('.env.development', 'w') as f:
            f.write(f"AUTH0_DOMAIN={AUTH0_DOMAIN}\n")
            f.write(f"API_AUDIENCE={API_AUDIENCE}\n")
            f.write("ENVIRONMENT=development\n")
            f.write("BYPASS_AUTH=1\n")
    
    try:
        # Test connection to Auth0 JWKS URL
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        print(f"\nTesting connection to: {jwks_url}")
        
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        
        # Get JWKS and print key count
        jwks = response.json()
        keys = jwks.get('keys', [])
        
        print(f"✓ Connection successful! Found {len(keys)} keys.")
        
        if keys:
            print(f"Key IDs: {[key.get('kid') for key in keys]}")
        
        print("\n=== Environment variables are correctly set! ===")
        return True
    except Exception as e:
        print(f"\n✕ Connection failed: {str(e)}")
        print("\n=== Action Required ===")
        print("1. Check your Auth0 configuration in .env file")
        print("2. Ensure AUTH0_DOMAIN is correctly set to your Auth0 tenant domain")
        print("3. Make sure your internet connection is working")
        print("\nFor development mode, you can set ENVIRONMENT=development in your .env file")
        print("This will allow bypassing Auth0 verification during development")
        return False

if __name__ == "__main__":
    # Run the test
    test_auth0_connection() 