# WalletConnect QR Code Test Frontend

A simple React app to test your WalletConnect v2 backend integration. This frontend allows you to:

- Create WalletConnect sessions
- Generate QR codes for wallet scanning
- Monitor session status in real-time
- Test different chain types (EVM and Solana)

## Quick Start

### 1. Install Dependencies

```bash
cd wc-qr-test
npm install
```

### 2. Start the Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

## Testing Your Backend

### Prerequisites

1. **Backend Running**: Make sure your FastAPI backend is running (typically on `http://localhost:8000`)

2. **Authentication**: Your backend requires Auth0 JWT authentication. For testing, you'll need to:
   - Either temporarily disable auth for the `/api/crypto/wallet/connect` endpoint
   - Or add a valid Auth0 JWT token to the request headers

### Testing Flow

1. **Configure**: Set your backend URL and test parameters
2. **Create Session**: Click "Create WalletConnect Session"
3. **Scan QR**: Use any WalletConnect v2 compatible wallet to scan the QR code
4. **Monitor**: Watch the session status update in real-time
5. **Verify**: Check that the wallet connects successfully

## Supported Wallets

Any WalletConnect v2 compatible wallet will work:

- **Mobile**: MetaMask Mobile, Rainbow, Trust Wallet, etc.
- **Desktop**: MetaMask, WalletConnect Desktop, etc.
- **Hardware**: Ledger Live, etc.

## Backend Endpoints Used

- `POST /api/crypto/wallet/connect` - Create new session
- `GET /api/crypto/wallet/session/{session_id}` - Get session status
- `DELETE /api/crypto/wallet/session/{session_id}` - Disconnect session

## Troubleshooting

### Authentication Error (401)
- Your backend requires Auth0 JWT authentication
- For testing, you can temporarily modify your backend to skip auth for this endpoint
- Or add a valid JWT token to the request headers

### CORS Error
- Make sure your backend has CORS configured to allow requests from `http://localhost:3000`
- Check your backend's CORS settings in `main.py`

### Connection Issues
- Verify your backend is running and accessible
- Check the backend URL in the configuration
- Ensure your wallet supports WalletConnect v2

### QR Code Not Working
- Verify the WalletConnect URI format is correct
- Make sure your wallet app supports WalletConnect v2
- Try copying the URI manually if QR scanning fails

## Development

### Project Structure
```
wc-qr-test/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # Main component
│   ├── index.js        # React entry point
│   └── index.css       # Styles
├── package.json
└── README.md
```

### Customization

You can easily modify the app to:
- Add more chain options
- Customize the UI styling
- Add additional testing features
- Integrate with your authentication system

## Production Notes

This is a **test-only frontend**. For production use:

1. **Authentication**: Implement proper Auth0 integration
2. **Security**: Add proper error handling and validation
3. **Styling**: Customize the UI to match your brand
4. **Error Handling**: Add comprehensive error handling
5. **Logging**: Add proper logging and monitoring

## Backend Integration

Your backend should have these endpoints implemented:

```python
# POST /api/crypto/wallet/connect
{
  "user_id": "string",
  "wallet_address": "string", 
  "chain_type": "evm" | "solana",
  "chain_id": "string"
}

# Response
{
  "success": true,
  "data": {
    "session_id": "string",
    "qr_code_url": "string",
    "uri": "string", 
    "status": "string",
    "expires_at": "string"
  }
}
```

The frontend will automatically poll for session status updates and display the connection state in real-time. 