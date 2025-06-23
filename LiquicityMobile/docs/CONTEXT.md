# Liquicity Mobile App - Context and Architecture Overview

## Objective

The goal of the Liquicity mobile app is to extend the functionality of the existing web app ([https://github.com/rajshah0904/Liquicity/tree/main](https://github.com/rajshah0904/Liquicity/tree/main)) to mobile platforms, enabling users to manage wallets, send/receive money, and access user-specific financial data on the go.

Liquicity is a digital wallet that allows users to exchange money internationally using stablecoins and cryptocurrency. It provides a modern solution for cross-border transactions by leveraging blockchain-based payments for speed, cost-efficiency, and reliability.

## Web App Summary (Base)

* **Frontend**: React.js with Auth0 for authentication
* **Backend**: FastAPI (Python) REST API
* **Database**: PostgreSQL
* **Authentication**: Auth0 (email/password and Google OAuth)
* **Deployment**: Docker + Compose (locally), potential Firebase hosting (mobile only)

## Mobile App Stack

* **Framework**: React Native (recommended with Expo for simplicity)
* **Backend**: Reuse existing FastAPI backend from web
* **Database**: PostgreSQL (via FastAPI backend)
* **Authentication**: Auth0 (with React Native SDK and Universal Login)
* **Hosting**: Firebase (for app deployment and possible auth token storage if needed)

## Current Gaps in Web App

* `/settings` page is not yet implemented
* `/receive` page is incomplete (missing UI and/or logic)

## Core Features to Implement

### 1. Authentication & User Management
- Auth0 integration with email/password and Google OAuth
- User profile management
- KYC verification flow
- Email verification process

### 2. Dashboard
- Display wallet balances (main wallet, stablecoin, fiat)
- Recent transactions list
- Quick action buttons for send/receive
- Balance visibility toggle
- Animated balance counters

### 3. Wallet Management
- Multiple wallet support
- Balance display for each wallet
- Transaction history per wallet
- QR code generation for receiving funds
- Copy wallet address functionality

### 4. Send Money
- Recipient selection/input
- Amount input with currency selection
- Transaction confirmation
- Transaction status tracking
- Fee calculation and display

### 5. Transactions
- Transaction history list
- Transaction details view
- Filtering and sorting options
- Transaction status indicators
- Date and time formatting

### 6. UI/UX Guidelines
- Dark theme by default
- Modern, minimalist design
- Smooth animations and transitions
- Responsive layouts
- Loading states and error handling

## Technical Implementation Details

### API Integration
- Base URL: `API_URL` from environment variables
- Authentication: Bearer token from Auth0
- Key endpoints:
  - `/api/wallets` - Wallet management
  - `/api/transactions` - Transaction history
  - `/api/users` - User profile
  - `/api/payments` - Payment processing

### State Management
- User authentication state
- Wallet balances and transactions
- Transaction processing status
- UI state (loading, errors, etc.)

### Navigation Structure
```
app/
├── (auth)/
│   ├── login.tsx
│   ├── signup.tsx
│   └── verify-email.tsx
├── (app)/
│   ├── dashboard.tsx
│   ├── wallet.tsx
│   ├── send.tsx
│   ├── transactions.tsx
│   └── profile.tsx
└── _layout.tsx
```

### Required Dependencies
- `@auth0/auth0-react-native` - Authentication
- `@react-navigation/native` - Navigation
- `axios` - API calls
- `react-native-reanimated` - Animations
- `react-native-qrcode-svg` - QR code generation
- `date-fns` - Date formatting
- `@react-native-async-storage/async-storage` - Local storage

## Development Priorities

1. **Phase 1: Core Authentication**
   - Auth0 setup and integration
   - Login/Signup flows
   - Email verification

2. **Phase 2: Dashboard & Wallet**
   - Dashboard layout and components
   - Wallet balance display
   - Transaction list

3. **Phase 3: Send Money**
   - Recipient selection
   - Amount input
   - Transaction processing

4. **Phase 4: Transactions & Profile**
   - Transaction history
   - Transaction details
   - Profile management

## Notes
- Settings and Receive Money features will be implemented after web app completion
- Focus on maintaining consistent UX with web app
- Implement proper error handling and loading states
- Ensure secure storage of sensitive data
- Follow mobile-specific best practices for performance

## Optimal Folder Structure (Web & Mobile)

```
LiquicityMobile/
│
├── Liquicity/                # Existing web app (React)
│   ├── frontend/             # React web frontend
│   └── ...                   # Backend, scripts, etc.
│
├── LiquicityMobileApp/       # NEW: React Native mobile app
│   ├── src/
│   ├── assets/
│   ├── app.json / app.config.js
│   ├── package.json
│   └── ...
│
├── shared/                   # (Optional) Shared logic between web and mobile
│   ├── api/
│   ├── utils/
│   └── ...
│
├── docs/                     # Documentation, changelogs, etc.
│   ├── CONTEXT.md            # Context and architecture overview
│   ├── CHANGELOG.md          # Changelog for all code changes
│   └── ...
│
└── README.md                 # Project overview
```

- Both `CONTEXT.md` and `CHANGELOG.md` are now in the `docs/` folder for easy access and organization.
- The folder structure is designed for clarity, scalability, and code sharing between web and mobile apps.

## Development Setup Plan (Step-by-Step)

1. **Initialize mobile project**

```bash
npx create-expo-app@latest -e with-router LiquicityMobile
cd LiquicityMobile
```

2. **Set up project structure** as described above.
3. **Create `.env`** file in `frontend/`:

```
REACT_APP_AUTH0_DOMAIN=...
REACT_APP_AUTH0_CLIENT_ID=...
REACT_APP_AUTH0_AUDIENCE=...
```

Use the same values as your working web app environment.
4\. **Install dependencies** (Axios, Auth0, etc.)
5\. **Copy reusable components and context** from the web app where applicable.
6\. **Skip building pages that are not yet implemented on web**:

* Do not work on `/settings` or `/receive` until backend and web versions are complete.

7. **Run the mobile app**

```bash
npx expo start
```

8. **Test Login and Dashboard features** using Auth0 and FastAPI backend.

## Future Enhancements

* Push notifications
* QR code-based wallet transfers
* Biometric login (Touch ID / Face ID)
* Caching / Offline mode

## Action Items

* Set up new `frontend/` React Native project under `LiquicityMobile`
* Add `.env` with `AUTH0_DOMAIN`, `CLIENT_ID`, and `AUDIENCE`
* Use Axios or Fetch to interact with FastAPI backend
* Test auth flow, wallet fetch, and transfers

Let me know if you want a full frontend mobile starter template as next step.
