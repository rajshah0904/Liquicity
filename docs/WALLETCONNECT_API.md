# WalletConnect & Transaction Management API

This document describes the comprehensive WalletConnect integration and transaction management system implemented in the clean_backend.

## Overview

The system provides:
- **WalletConnect v2 Integration**: Real-time wallet connection and transaction signing
- **Transaction Management**: Complete transaction lifecycle with blockchain confirmation
- **Risk Assessment**: Automated risk scoring and compliance reporting
- **Dispute Management**: User dispute creation and admin resolution
- **Admin Controls**: Blacklist management and compliance reporting

## Authentication

All endpoints require authentication via Auth0 JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## WalletConnect Endpoints

### Session Management

#### Create WalletConnect Session
```http
POST /api/v1/walletconnect/session
```

**Request Body:**
```json
{
  "user_id": "string",
  "wallet_address": "string",
  "chain_type": "solana|evm",
  "chain_id": "string"
}
```

**Response:**
```json
{
  "session_id": "string",
  "qr_code": "data:image/png;base64,...",
  "uri": "wc:topic@relay?chainId=...",
  "status": "pending",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

#### Get Session Status
```http
GET /api/v1/walletconnect/session/{session_id}
```

#### Disconnect Session
```http
DELETE /api/v1/walletconnect/session/{session_id}
```

#### Get Active Sessions
```http
GET /api/v1/walletconnect/sessions/active
```

#### Get Session Events
```http
GET /api/v1/walletconnect/session/{session_id}/events
```

#### Get Connection Status
```http
GET /api/v1/walletconnect/session/{session_id}/connection
```

#### Refresh Session Connection
```http
POST /api/v1/walletconnect/session/{session_id}/refresh
```

### Transaction Management

#### Create Transaction Request
```http
POST /api/v1/walletconnect/transaction
```

**Request Body:**
```json
{
  "session_id": "string",
  "to_address": "string",
  "amount": "1.5",
  "currency": "usdc",
  "gas_estimate": {
    "gas_limit": "21000",
    "gas_price": "20000000000"
  }
}
```

**Features:**
- ✅ On-chain balance validation
- ✅ Blacklist address checking
- ✅ Risk assessment and scoring
- ✅ Compliance reporting for high-risk transactions
- ✅ Transaction logging in database

#### Get Transaction Request Status
```http
GET /api/v1/walletconnect/transaction/{request_id}/status
```

#### Get Transaction Status (with blockchain confirmation)
```http
GET /api/v1/walletconnect/transaction/{request_id}
```

### Service Health

#### Get Service Health
```http
GET /api/v1/walletconnect/health
```

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "pending_transactions": 2,
  "total_sessions": 10,
  "websocket_connected": true
}
```

## Transaction Management Endpoints

### Transaction History

#### Get User Transaction History
```http
GET /transactions/history?page=1&per_page=20&status=pending&chain_type=solana
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (pending, confirmed, failed)
- `chain_type` (string, optional): Filter by chain type (solana, evm)

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "from_wallet": "string",
      "to_wallet": "string",
      "amount": 1.5,
      "currency": "usdc",
      "chain_type": "solana",
      "status": "confirmed",
      "tx_hash": "string",
      "risk_score": 25.0,
      "flagged": false,
      "notes": "Risk flags: new_wallet",
      "created_at": "2024-01-01T12:00:00Z",
      "confirmed_at": "2024-01-01T12:05:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

#### Get Transaction Status (with blockchain polling)
```http
GET /transactions/{transaction_id}/status
```

**Features:**
- ✅ Real-time blockchain confirmation checking
- ✅ Automatic status updates (pending → confirmed/failed)
- ✅ Timeout handling (1 hour)

### Dispute Management

#### Create Dispute
```http
POST /transactions/dispute
```

**Request Body:**
```json
{
  "transaction_id": "uuid",
  "reason": "I didn't authorize this transaction"
}
```

#### Get User Disputes
```http
GET /transactions/disputes
```

## Admin Endpoints

### Transaction Management

#### Get All Transactions (Admin)
```http
GET /transactions/admin/all?status=flagged&flagged=true
```

**Query Parameters:**
- `status` (string, optional): Filter by status
- `flagged` (boolean, optional): Filter by flagged status

### Dispute Management

#### Get All Disputes (Admin)
```http
GET /transactions/admin/disputes?status=open
```

#### Resolve Dispute (Admin)
```http
PUT /transactions/admin/disputes/{dispute_id}/resolve?resolution=resolved
```

**Query Parameters:**
- `resolution` (string): "resolved" or "rejected"

### Blacklist Management

#### Add Blacklisted Address (Admin)
```http
POST /transactions/admin/blacklist
```

**Request Body:**
```json
{
  "address": "string",
  "chain_type": "solana",
  "reason": "Suspicious activity detected"
}
```

#### Get Blacklisted Addresses (Admin)
```http
GET /transactions/admin/blacklist?active_only=true
```

#### Deactivate Blacklisted Address (Admin)
```http
PUT /transactions/admin/blacklist/{address_id}/deactivate
```

### Compliance Reporting

#### Get Compliance Reports (Admin)
```http
GET /transactions/admin/compliance?report_type=SAR&reviewed=false
```

**Query Parameters:**
- `report_type` (string, optional): Filter by report type (SAR, CTR, manual_review)
- `reviewed` (boolean, optional): Filter by review status

#### Review Compliance Report (Admin)
```http
PUT /transactions/admin/compliance/{report_id}/review
```

## Risk Assessment Features

### Automatic Risk Scoring

The system automatically assesses transaction risk based on:

1. **Blacklist Check**: +100 points if destination is blacklisted
2. **High Value**: +50 points for transactions > $10,000 (SAR threshold)
3. **High Frequency**: +30 points for >10 transactions in 24 hours (CTR threshold)
4. **New Wallet**: +20 points for first transaction from wallet

### Risk Levels

- **Low Risk**: 0-49 points
- **Medium Risk**: 50-79 points (CTR report generated)
- **High Risk**: 80-100 points (SAR report generated)

### Compliance Reports

- **CTR (Currency Transaction Report)**: Generated for medium-risk transactions
- **SAR (Suspicious Activity Report)**: Generated for high-risk transactions
- **Manual Review**: Available for admin review and resolution

## Real-Time Features

### WebSocket Integration

- **Real-time session events**: Session approval, rejection, disconnection
- **Transaction status updates**: Real-time transaction signing status
- **Connection monitoring**: WebSocket connection health checks
- **Automatic reconnection**: Session refresh capabilities

### Background Monitoring

- **Transaction confirmation polling**: Automatic blockchain status checking
- **Timeout handling**: Automatic failure marking for stuck transactions
- **Session cleanup**: Automatic cleanup of expired sessions

## Error Handling

### Common Error Codes

- `INVALID_WALLET_ADDRESS`: Invalid or blacklisted address
- `INSUFFICIENT_BALANCE`: Insufficient wallet balance
- `SESSION_EXPIRED`: WalletConnect session expired
- `WEBSOCKET_ERROR`: WebSocket connection issues
- `TRANSACTION_ERROR`: Transaction processing errors

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Security Features

### Address Validation

- **Solana**: Base58 validation with 32-byte length check
- **EVM**: Hexadecimal format validation (0x + 40 chars)

### Transaction Security

- **Balance validation**: On-chain balance checking before transaction
- **Blacklist enforcement**: Automatic blocking of blacklisted addresses
- **Risk assessment**: Real-time risk scoring and flagging
- **Audit logging**: Complete transaction audit trail

### Admin Security

- **Role-based access**: Admin-only endpoints for sensitive operations
- **Audit trails**: Complete logging of admin actions
- **Compliance reporting**: Automated SAR/CTR generation

## Database Models

### Core Models

- **Transaction**: Complete transaction records with risk assessment
- **BlacklistedAddress**: Address blacklist management
- **Dispute**: User dispute tracking and resolution
- **ComplianceReport**: SAR/CTR and compliance reporting

### Key Fields

- **Risk scoring**: 0-100 risk assessment
- **Flagging**: Boolean flag for high-risk transactions
- **Audit trails**: Complete timestamps and user tracking
- **Status tracking**: Pending → Confirmed/Failed lifecycle

## Usage Examples

### Complete Transaction Flow

1. **Create Session**: `POST /api/v1/walletconnect/session`
2. **Generate QR Code**: Display QR code to user
3. **Wait for Approval**: Poll `GET /api/v1/walletconnect/session/{session_id}`
4. **Create Transaction**: `POST /api/v1/walletconnect/transaction`
5. **Monitor Status**: Poll `GET /transactions/{transaction_id}/status`
6. **Handle Confirmation**: Transaction automatically confirmed on blockchain

### Admin Workflow

1. **Monitor Transactions**: `GET /transactions/admin/all?flagged=true`
2. **Review Compliance**: `GET /transactions/admin/compliance?reviewed=false`
3. **Manage Blacklist**: `POST /transactions/admin/blacklist`
4. **Resolve Disputes**: `PUT /transactions/admin/disputes/{id}/resolve`

## Production Considerations

### Performance

- **Connection pooling**: Efficient WebSocket connection management
- **Background monitoring**: Asynchronous transaction status updates
- **Pagination**: Efficient large dataset handling
- **Caching**: Session and transaction status caching

### Scalability

- **Stateless design**: Session state management
- **Database optimization**: Indexed queries for performance
- **Rate limiting**: API rate limiting for abuse prevention
- **Load balancing**: Horizontal scaling support

### Monitoring

- **Health checks**: Service health monitoring
- **Metrics collection**: Transaction volume and success rates
- **Error tracking**: Comprehensive error logging
- **Performance monitoring**: Response time tracking 