# Liquicity Crypto Payment API

Production-level WalletConnect v2 + USDC crypto payment gateway for users without bank accounts.

## 🚀 Features

- **WalletConnect v2 Integration**: Secure wallet connections with QR codes
- **USDC Cross-Chain Payments**: Support for Ethereum, Polygon, Base, and Solana
- **Bridge API Integration**: On/off-ramp capabilities for fiat conversion
- **Gas Optimization**: Automatic gas estimation and cost optimization
- **Multi-Chain Support**: Choose the best network for cost/speed
- **Security**: JWT authentication, rate limiting, risk scoring
- **Production Ready**: Docker, monitoring, logging, health checks

## 📊 Cost Savings

| Payment Method | Cost | Speed | Security |
|----------------|------|-------|----------|
| Traditional (Stripe/PayPal) | 4.5% + $0.50 | 2-5 days | High |
| **Crypto (Polygon)** | **$0.01-0.10** | **15 seconds** | **High** |
| **Crypto (Solana)** | **$0.00025** | **1 second** | **High** |

**Savings: 95%+ compared to traditional payment processors**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Python Backend    │    │   Node.js MS    │
│   (React/Next)  │◄──►│   (FastAPI)         │◄──►│   (WalletConnect)│
└─────────────────┘    └─────────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Bridge API    │
                       │   (On/Off-ramp) │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **WalletConnect**: Node.js microservice
- **Database**: PostgreSQL + Redis
- **Blockchain**: Web3.py, Solana.py
- **Security**: JWT, bcrypt, rate limiting
- **Deployment**: Docker, Docker Compose
- **Monitoring**: Prometheus + Grafana

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL
- Redis

### 1. Clone and Setup

```bash
git clone <repository>
cd python_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://liquicity:password@localhost:5432/liquicity
REDIS_URL=redis://localhost:6379

# WalletConnect
WALLETCONNECT_PROJECT_ID=your_project_id_here
WALLETCONNECT_RELAY_URL=wss://relay.walletconnect.com

# Bridge API
BRIDGE_API_KEY=your_bridge_api_key
BRIDGE_API_URL=https://api.bridge.com

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server
HOST=0.0.0.0
PORT=8000
```

### 3. Start Services

#### Option A: Docker Compose (Recommended)

```bash
cd docker_setup
docker-compose up -d
```

#### Option B: Manual Start

```bash
# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_DB=liquicity \
  -e POSTGRES_USER=liquicity \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Start Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Start WalletConnect microservice
cd walletconnect_microservice
npm install
npm start

# Start Python backend
cd ..
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## 📚 API Documentation

### Authentication

All API endpoints require JWT authentication:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/wallet/connect
```

### 1. Connect Wallet

```bash
curl -X POST http://localhost:8000/api/v1/wallet/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": "user123",
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "chain_type": "evm",
    "chain_id": "polygon"
  }'
```

Response:
```json
{
  "session_id": "session-uuid",
  "qr_code_url": "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=wc:...",
  "uri": "wc:project_id@2?relay-protocol=irn&chainId=polygon&session_id=...",
  "status": "pending",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

### 2. Create USDC Transfer

```bash
curl -X POST http://localhost:8000/api/v1/payments/usdc/transfer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "session_id": "session-uuid",
    "to_address": "0x8ba1f109551bD432803012645Hac136c772c3",
    "amount": "100.00",
    "currency": "usdc"
  }'
```

Response:
```json
{
  "transfer_id": "transfer-uuid",
  "session_id": "session-uuid",
  "amount": "100.00",
  "to_address": "0x8ba1f109551bD432803012645Hac136c772c3",
  "chain_type": "evm",
  "chain_id": "polygon",
  "gas_estimate": {
    "gas_limit": 65000,
    "gas_price": "30000000000",
    "total_cost": "0.00195"
  },
  "status": "pending",
  "expires_at": "2024-01-01T12:30:00Z"
}
```

### 3. Sign Transaction

```bash
curl -X POST http://localhost:8000/api/v1/payments/usdc/sign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "transfer_id": "transfer-uuid",
    "signed_transaction": "0x..."
  }'
```

Response:
```json
{
  "transfer_id": "transfer-uuid",
  "transaction_hash": "0x1234...",
  "status": "confirmed",
  "confirmation_time": "2024-01-01T12:15:00Z"
}
```

### 4. Get Cost Savings

```bash
curl -X POST http://localhost:8000/api/v1/cost-savings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "amount": "100.00"
  }'
```

Response:
```json
{
  "traditional_cost": "4.50",
  "crypto_cost": "0.00195",
  "savings": "4.49805",
  "savings_percentage": 99.96,
  "gas_estimate": "0.00195",
  "recommended_network": "polygon"
}
```

## 🔧 Configuration

### Supported Networks

| Network | Chain ID | Gas Cost | Speed | USDC Contract |
|---------|----------|----------|-------|---------------|
| Polygon | 137 | $0.01-0.10 | 15s | 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 |
| Base | 8453 | $0.005-0.05 | 30s | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 |
| Solana | mainnet | $0.00025 | 1s | EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v |
| Ethereum | 1 | $2-50 | 2-3m | 0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8C |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `WALLETCONNECT_PROJECT_ID` | WalletConnect project ID | - |
| `BRIDGE_API_KEY` | Bridge API key | - |
| `JWT_SECRET_KEY` | JWT signing key | - |
| `CORS_ORIGINS` | Allowed CORS origins | - |

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_walletconnect.py -v
```

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# WalletConnect microservice health
curl http://localhost:3001/health

# Database health
docker exec liquicity-postgres pg_isready -U liquicity
```

### Metrics

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Logs

```bash
# Backend logs
docker logs liquicity-python-backend

# WalletConnect logs
docker logs liquicity-walletconnect-ms

# Database logs
docker logs liquicity-postgres
```

## 🔒 Security

### Authentication

- JWT tokens with configurable expiration
- Secure password hashing with bcrypt
- Rate limiting per user/IP

### Authorization

- Role-based access control
- Permission-based endpoints
- Risk scoring for transactions

### Data Protection

- Encrypted sensitive data
- Secure session management
- Input validation and sanitization

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Configure load balancing
- [ ] Set up logging aggregation

### Docker Production

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale python-backend=3
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n liquicity
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@liquicity.com

## 🔗 Related Projects

- [Frontend React App](../new_website/)
- [Rust Backend](../rust_backend/)
- [Solana Integration](../liquicity-solana-integration/) 