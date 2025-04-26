#!/usr/bin/env python3
import os, sys, asyncio
# Add project root to Python path so `import app` resolves correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.payments.services.orchestrator import transfer_cross_border

# 1) load your sandbox creds & test account envvars
os.environ.update({
    "MODERN_TREASURY_API_KEY": "publishable-test-NDVhMWYwM2YtOTUyYS00YmMzLTgzZmYtNTAzMzgxZDNlODMxOnlvcXNnUm1hUjVyVnlXNzQxaGFMdWNueDl3dExpU1h6ZE1yakExbUhjQ2t2aFhkSkJZRlg2ZmFGYnZqMXFrRlE=",
    "RAPYD_ACCESS_KEY": "rak_95040615209167CA9297",
    "RAPYD_SECRET_KEY": "rsk_dffd97e4179e945abc5f52ef368b4851dde60e44d82e007e0a2782c84e53c4c29814627057395788",
    "CIRCLE_API_KEY": "TEST_API_KEY:056c5becea4d525de0ae5ebbfeb3726f:af986b987a2bbd404602e060b9ccf9e4",
    "TEST_US_ACCOUNT": "00000000",
    "TEST_US_ROUTING": "021000021",
    "TEST_CA_ACCOUNT": "12345678",
    "TEST_CA_ROUTING": "0010001",
})
async def main():
    result = await transfer_cross_border(
        user_id="cli_user",
        amount=0.01,
        src_cc="US",
        dst_cc="CA",
        currency="USD",
        chain="polygon",
        metadata={"note": "e2e smoke test"}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())