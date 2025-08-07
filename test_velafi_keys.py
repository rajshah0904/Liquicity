
import asyncio
import os

from dotenv import load_dotenv

from VelaFi.velafi_client import VelafiClient, VelafiError

# Load environment variables from .env file
load_dotenv()


async def test_velafi_api_key():
    """Quickly verify that the VelaFi sandbox API key is valid.

    Calls the documented `GET /v1/account` endpoint which returns the
    authenticated account profile. It is side-effect free and works even in an
    empty sandbox.
    """

    api_key = os.getenv("VELAFI_API_KEY")
    base_url = os.getenv("VELAFI_BASE_URL", "https://sandbox.velafi.com/api")

    if not api_key:
        print("Error: VELAFI_API_KEY environment variable not set.")
        return

    print(f"Testing VelaFi API key against base URL: {base_url}")

    try:
        async with VelafiClient(api_key=api_key, base_url=base_url) as client:
            print("Fetching account details…")
            account = await client.get_account()
            print("Success! Your sandbox API key is valid.")
            print("Account ID:", account.get("id"))
            print("Merchant ID:", account.get("merchant_id"))
            print("Status:", account.get("status"))

    except VelafiError as e:
        print("VelaFi API error:", e)
        if e.status == 401:
            print("Authentication failed – check API key or IP whitelist.")
        elif e.status == 403:
            print("Forbidden – this IP may not be whitelisted in the sandbox.")
    except Exception as exc:
        print("Unexpected error:", exc)


if __name__ == "__main__":
    asyncio.run(test_velafi_api_key())