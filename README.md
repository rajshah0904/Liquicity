# Liquicity Payment Stack

This is the Liquicity payment stack for processing payments in various currencies. This version focuses on cross-border fiat payments using the Stargate bridge functionality.

## Recent Changes

### Functionality Updates
- Removed blockchain wallet and stablecoin balance functionality
- Removed AI/LLM integration
- Kept cross-border functionality with Stargate
- Focused on core payment processing using Modern Treasury

### How to Run the Migration

The codebase has been updated to remove the blockchain wallet, AI, and stablecoin balance-related functionality. To migrate your database schema, run:

```bash
python run_migration.py
```

This will:
1. Remove the `stablecoin_balance` and `blockchain_address` columns from the `wallets` table
2. Drop blockchain-related tables (`blockchain_transactions`, `blockchain_wallets`)
3. Drop AI-related tables (`ai_messages`, `ai_actions`, `ai_conversations`, `ai_agents`)
4. Drop data analytics tables (`data_pipeline_runs`, `data_pipelines`, `data_queries`)

### Running the Application

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
cd frontend && npm install
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Start the frontend (in a separate terminal):

```bash
cd frontend && npm start
```

## Core Features

- Cross-border payments integration using Stargate
- Domestic payment processing with Modern Treasury
- User authentication and wallet management
- Currency conversion
- Payment tracking

## Features

- **Multi-Currency Wallet Management**: Create and manage wallets in various currencies
- **Fast Cross-Border Payments**: Send money globally with minimal fees
- **AI-Native Infrastructure**: Natural language interface for financial operations
- **Analytics & Reporting**: Gain insights into your financial activities
- **Secure Transactions**: All transactions are encrypted and secure

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework for Python
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migration tool
- **JWT**: Authentication mechanism
- **OpenAI/LangChain**: For AI capabilities

### Frontend
- **React**: UI library for building dynamic interfaces
- **Material-UI**: Component library for consistent design
- **Axios**: HTTP client for API requests
- **React Router**: Client-side routing
- **Web3.js**: For blockchain interactions (optional)

### Database
- **PostgreSQL**: Primary relational database
- **Redis**: Caching and session management

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/liquicity.git
cd liquicity
```

2. Set up the backend:
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

3. Set up the frontend:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

4. Navigate to http://localhost:3000 in your browser

## Project Structure

```
liquicity/
├── app/                 # Backend application
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality and configuration
│   ├── db/              # Database models and connection
│   ├── routers/         # API routers
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic schemas
│   └── main.py          # Application entry point
├── frontend/            # Frontend application
│   ├── public/          # Static files
│   ├── src/             # Source code
│   │   ├── components/  # Reusable components
│   │   ├── context/     # React context providers
│   │   ├── pages/       # Page components
│   │   ├── utils/       # Utility functions
│   │   ├── App.js       # Main component
│   │   └── index.js     # Entry point
├── migrations/          # Database migrations
├── tests/               # Test suite
├── .env                 # Environment variables
└── README.md            # This file
```

## API Documentation

When the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/) 