# LiquicityMobile - Project Documentation

## Project Overview
LiquicityMobile is a React Native app that integrates with Bridge API for KYC (Know Your Customer) onboarding. The app provides authentication via Auth0 and implements a complete KYC flow using Bridge's sandbox environment.

## Current Architecture

### Tech Stack
- **React Native** - Mobile app framework
- **Auth0** - Authentication provider
- **Bridge API** - KYC/onboarding service
- **TypeScript** - Type safety
- **React Navigation** - Navigation between screens
- **react-native-config** - Environment variable management

### Key Dependencies
- `react-native-auth0` - Auth0 integration
- `react-native-webview` - WebView for TOS display
- `axios` - HTTP client for API calls
- `uuid` - Idempotency key generation
- `react-native-vector-icons` - UI icons

## Environment Configuration

### .env File (Create this in LiquicityMobile root)
```
BRIDGE_API_URL=https://api.sandbox.bridge.xyz/v0
BRIDGE_API_KEY=sk-test-b68d29ce02c83ffb0353d9dfa6f84530
USE_MOCKS=false
```

### Environment Variables
- `BRIDGE_API_URL` - Bridge API base URL (sandbox)
- `BRIDGE_API_KEY` - Bridge API authentication key
- `USE_MOCKS` - Toggle between mock and real API

## Current App Flow

### 1. Authentication Flow
1. **Home Screen** (`src/components/Home.tsx`)
   - Displays login/signup options
   - Google OAuth integration
   - Email-based authentication
   - "Test KYC Flow" button for development

2. **Auth0 Integration**
   - Universal login with email/password
   - Google OAuth connection
   - Session management
   - Automatic user state handling

### 2. KYC Flow
1. **Terms of Service Screen** (`src/components/TermsOfServiceScreen.tsx`)
   - Requests TOS link from Bridge API
   - Displays TOS in WebView
   - Handles TOS acceptance redirect
   - Extracts `signed_agreement_id` from redirect URL

2. **KYC Start Screen** (`src/components/KYCStart.tsx`)
   - Receives `signed_agreement_id` from TOS
   - Country selection interface
   - Customer creation process

### 3. Main App (After Authentication)
- **Dashboard** - Main app interface
- **Wallet** - Wallet management
- **Send** - Send transactions
- **Receive** - Receive transactions
- **Activity** - Transaction history

## Key Files and Their Functions

### Core Files
- `App.tsx` - Main app component with navigation setup
- `src/RootStackParamList.ts` - TypeScript navigation types
- `src/auth0-configuration.ts` - Auth0 configuration

### API Integration
- `src/lib/bridgeClient.ts` - Bridge API client
  - Generic `bridgeRequest()` function for all API calls
  - Automatic idempotency key generation for POST requests
  - Mock mode support
  - Environment variable handling

### Components
- `src/components/Home.tsx` - Authentication screen
- `src/components/TermsOfServiceScreen.tsx` - TOS display and acceptance
- `src/components/KYCStart.tsx` - KYC onboarding
- `src/components/Dashboard.tsx` - Main dashboard
- `src/components/Wallet.tsx` - Wallet interface
- `src/components/Send.tsx` - Send functionality
- `src/components/Receive.tsx` - Receive functionality
- `src/components/Activity.tsx` - Activity history

### Utilities
- `src/utils/kyc.ts` - KYC status checking
- `src/utils/bridgeApi.ts` - Alternative Bridge API implementation

## Bridge API Integration

### Current Endpoints Used
1. **POST /customers/tos_links** - Request TOS link
   - Returns: `{ url: string }`
   - Used in: `requestTosLink()` function

### API Headers
- `Api-Key` - Bridge API authentication
- `Content-Type: application/json`
- `Idempotency-Key` - UUID for POST requests

### Mock Mode
- When `USE_MOCKS=true`, uses local mock server
- Mock server runs on `http://192.168.86.26:3000`
- Uses `db.json` and `routes.json` for mock data

## Current Working Features

### ✅ Implemented and Working
1. **Authentication**
   - Auth0 integration with Google OAuth
   - Email-based login/signup
   - Session management
   - Automatic user state handling

2. **KYC Flow**
   - TOS link request from Bridge API
   - WebView display of TOS
   - TOS acceptance handling
   - `signed_agreement_id` extraction
   - Navigation to KYC start screen

3. **Navigation**
   - Bottom tab navigation for main app
   - Stack navigation for auth/KYC flow
   - Proper screen transitions

4. **API Integration**
   - Bridge API client with proper headers
   - Environment variable support
   - Mock mode toggle
   - Error handling

### 🔄 In Progress
1. **KYC Completion**
   - Country selection implementation
   - Customer creation with Bridge API
   - KYC status checking

### 📋 TODO
1. **Complete KYC Flow**
   - Document upload
   - Identity verification
   - KYC approval handling

2. **Wallet Features**
   - Actual wallet integration
   - Transaction functionality
   - Balance display

## Development Setup

### Prerequisites
- Node.js and npm
- React Native CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)
- Watchman (for file watching)

### Installation Steps
1. Install dependencies: `npm install`
2. iOS: `cd ios && pod install && cd ..`
3. Create `.env` file with Bridge API credentials
4. Start Metro: `npx react-native start --reset-cache`
5. Run app: `ENVFILE=.env npx react-native run-ios`

### Environment Setup
- Ensure `.env` file exists in project root
- Verify Bridge API key is valid
- Test both mock and real API modes

## Error Handling

### Common Issues
1. **401 Unauthorized** - Check Bridge API key validity
2. **Network errors** - Verify API URL and connectivity
3. **Environment variables undefined** - Rebuild app after `.env` changes
4. **Navigation errors** - Check TypeScript navigation types

### Debugging
- Console logs in `bridgeClient.ts` show API key and URL
- Metro bundler logs show environment variable injection
- Bridge API responses logged for debugging

## Testing

### Current Test Flow
1. Launch app
2. Use "Test KYC Flow" button on Home screen
3. Accept TOS in WebView
4. Verify navigation to KYC start screen
5. Check console logs for API calls

### Mock Testing
- Set `USE_MOCKS=true` in `.env`
- Ensure mock server is running
- Test with mock data in `db.json`

## Security Considerations

### API Key Management
- API keys stored in `.env` file (not committed to git)
- Fallback to test key for development
- Production keys should be managed securely

### Data Handling
- Sensitive data not logged in production
- Proper error handling without exposing internals
- Secure session management via Auth0

## Next Steps

### Immediate Priorities
1. Complete KYC flow implementation
2. Add proper error handling and user feedback
3. Implement wallet functionality
4. Add loading states and better UX

### Future Enhancements
1. Push notifications
2. Offline support
3. Advanced security features
4. Multi-language support

## Notes for New Chat
- All environment variables are handled via `react-native-config`
- Bridge API integration is complete and tested
- Authentication flow is fully functional
- KYC flow is partially implemented (TOS working, rest in progress)
- Mock mode available for development/testing
- TypeScript types are properly defined
- Navigation structure is established
- Error handling patterns are in place

This documentation should provide complete context for continuing development without needing to re-learn the project structure or current implementation state.

## Bridge ToS and KYC Flow (2024-06 Update)

### Key Learnings and Implementation (from recent dev session)

#### 1. Requesting the Bridge ToS Link
- Use the Bridge API endpoint `/customers/tos_links` to get a hosted ToS URL.
- Always append a `redirect_uri` to the URL. **For iOS WebView compatibility, use an HTTPS URL (e.g., `https://myapp.local/kyc`) instead of a custom scheme.**
- Example helper:
  ```js
  function appendRedirectUri(url, redirectUri) {
    return url.includes('?')
      ? `${url}&redirect_uri=${encodeURIComponent(redirectUri)}`
      : `${url}?redirect_uri=${encodeURIComponent(redirectUri)}`;
  }
  ```

#### 2. Displaying the ToS in a WebView
- Show the ToS URL in a React Native WebView inside a modal.
- Use `originWhitelist={['*']}` if needed.
- Intercept the redirect after ToS acceptance using both `onShouldStartLoadWithRequest` and `onNavigationStateChange` for maximum compatibility.
- Intercept URLs starting with your HTTPS redirect URI (e.g., `https://myapp.local/kyc`).
- Extract the `signed_agreement_id` from the URL query string.
- Example:
  ```js
  onShouldStartLoadWithRequest={event => {
    const url = event.url || event.mainDocumentURL;
    if (url && url.startsWith('https://myapp.local/kyc')) {
      const match = url.match(/signed_agreement_id=([^&]+)/);
      if (match) {
        setTosModalVisible(false);
        setTimeout(() => navigation.navigate('KYCStart', { signed_agreement_id: match[1] }), 300);
      }
      return false;
    }
    return true;
  }}
  onNavigationStateChange={navState => {
    if (navState.url && navState.url.startsWith('https://myapp.local/kyc')) {
      const match = navState.url.match(/signed_agreement_id=([^&]+)/);
      if (match) {
        setTosModalVisible(false);
        setTimeout(() => navigation.navigate('KYCStart', { signed_agreement_id: match[1] }), 300);
      }
      return;
    }
    setCanGoBackBridgeTos(navState.canGoBack);
  }}
  ```

#### 3. Navigating to KYCStart
- After extracting `signed_agreement_id`, navigate to the KYCStart screen and pass it as a param.
- KYCStart should expect `route.params.signed_agreement_id`.

#### 4. Creating a Customer
- Add a `createCustomer` function to your Bridge API client:
  ```js
  export async function createCustomer(data) {
    return bridgeRequest('POST', '/customers', data);
  }
  ```
- In KYCStart, after the user selects a country (and later, after collecting all required info), call `createCustomer` with the required fields and the `signed_agreement_id`.
- Example:
  ```js
  const resp = await createCustomer({
    signed_agreement_id,
    country,
    // ...other required fields
  });
  ```

#### 5. Next Steps for KYC
- Expand the KYCStart screen to collect all required Bridge fields:
  - First and last name
  - Country
  - Street address, city, postal code, province/state
  - Date of birth
  - Email
  - National identity number (non-USA) or SSN (USA)
  - ID verification, proof of address, etc. as needed
- Pass all collected fields to `createCustomer`.
- Handle the response and guide the user through the rest of the KYC flow (document upload, status checks, etc.).

#### 6. Troubleshooting & Best Practices
- Always use an HTTPS redirect URI for iOS WebView compatibility.
- Intercept the redirect in both WebView handlers for maximum reliability.
- Log the ToS URL before rendering the WebView to verify correct parameters.
- If Bridge does not redirect, double-check the ToS URL and `redirect_uri`.

---

**This section summarizes all the key implementation details and lessons learned for the Bridge ToS and KYC flow. Future development should build on this foundation without repeating these steps.**
