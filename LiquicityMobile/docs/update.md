LiquicityMobile Project Structure & KYC Flow Context
Top-Level Structure
Liquicity/
└── LiquicityMobile/
    ├── ios/                   # iOS native project (Xcode, Info.plist, Pods)
    ├── android/               # Android native project (if present)
    ├── mock/                  # Mock server for local API simulation
    ├── src/                   # Main React Native app source code
    ├── .env                   # Environment variables (USE_MOCKS, API keys, etc.)
    ├── package.json           # Project dependencies and scripts
    └── ...                    # Other config files (e.g., .gitignore, .cursorignore)

Key Folders & Files for Mobile App and KYC
1. src/ — Main App Source
Purpose: All React Native code for the mobile app.
Relevant for KYC:
components/: UI screens and components.
Home.tsx: Main login/landing screen, includes the “Test KYC Flow” button.
KYCStart.tsx: Country selection and start of KYC flow.
Other screens: Dashboard.tsx, Wallet.tsx, etc.
lib/: API clients and helpers.
bridgeClient.ts: Handles all Bridge API/mock server requests, including KYC endpoints. Switches between mock and real API based on env.
utils/: Utility functions.
bridgeApi.ts: (May be legacy/alternate API client.)
kyc.ts: Functions for fetching KYC status, etc.
2. mock/ — Local Mock Server
Purpose: Simulates Bridge API for local development/testing (no real API key needed).
Files:
db.json: Mock data (e.g., TOS links, customers, KYC status).
routes.json: Custom route mappings (e.g., /customers/tos_links → /tos_links).
How it’s used:
Run with json-server to provide local API endpoints for the app in mock mode.
3. ios/ — iOS Native Project
Purpose: Native iOS configuration and build files.
Relevant for KYC:
Info.plist: Must include App Transport Security (ATS) exceptions to allow HTTP requests to your local mock server.
4. .env — Environment Variables
Purpose: Controls whether the app uses the mock server or real Bridge API.
Key variables:
USE_MOCKS=true (enables mock mode)
BRIDGE_API_URL, BRIDGE_API_KEY (for real/sandbox Bridge API)
How the KYC Flow Works in This Setup
App Launches:
Reads .env to determine if mock mode is enabled.
If USE_MOCKS=true, all Bridge API requests go to the mock server.
User Taps “Test KYC Flow”:
Calls requestTosLink() in bridgeClient.ts.
In mock mode, this now makes a GET request to /tos_links on the mock server.
The mock server returns a static TOS link from db.json.
TOS Link Opens in WebView:
The app displays the TOS link in a modal WebView.
On acceptance, the app navigates to the KYC country selection screen (KYCStart.tsx).
Country Selection and Next Steps:
User selects their country.
The app will (in future steps) build out dynamic KYC forms and status polling, using the same mock/real API switching logic.
Summary Table
| Folder/File | Purpose/Contents |
|----------------------------|----------------------------------------------------------------------------------|
| src/components/ | React Native screens (Home, KYCStart, etc.) |
| src/lib/bridgeClient.ts | API client for Bridge/mock server, handles KYC requests, switches by env |
| src/utils/ | Utility functions (KYC status, etc.) |
| mock/db.json | Mock API data (TOS links, customers, etc.) |
| mock/routes.json | Custom route mapping for json-server |
| ios/Info.plist | iOS config, must allow HTTP to local mock server |
| .env | Environment variables (USE_MOCKS, API keys, etc.) |
How to Continue the KYC Flow
Build out dynamic KYC forms in KYCStart.tsx or a new component.
Add endpoints and mock data to db.json as needed for new KYC steps.
Update bridgeClient.ts to handle new KYC API calls, using GET in mock mode and POST in real mode.
Test everything in mock mode before switching to the real Bridge API.
This summary gives you (or any new AI/chat) a full context of the project structure, the KYC flow, and where to pick up next.
