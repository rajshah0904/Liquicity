# Liquicity

A modern platform for liquidity and transactions built with FastAPI and React.

## Quick Setup

### Option 1: GitHub Codespaces (Recommended)

The easiest way to run Liquicity is using GitHub Codespaces:

1. Click the green "Code" button on the repository
2. Select the "Codespaces" tab
3. Click "Create codespace on main"
4. Once loaded, run in terminal:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. In a second terminal, run:
   ```bash
   npm run dev
   ```

For detailed Codespaces setup, see [CODESPACES_SETUP.md](CODESPACES_SETUP.md).

### Option 2: Local Docker

To run locally with Docker:

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/liquicity.git
   cd liquicity
   ```

2. Start the application using Docker Compose
   ```bash
   docker compose up
   ```

3. Access the application:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Option 3: Local Development Setup

To run locally without Docker:

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/liquicity.git
   cd liquicity
   ```

2. Set up a Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL
   - Create a database named `liquicity`
   - Set environment variable: `export DATABASE_URL=postgresql://user:password@localhost:5432/liquicity`

4. Run the backend
   ```bash
   uvicorn app.main:app --reload
   ```

5. Install frontend dependencies
   ```bash
   npm install
   ```

6. Run the frontend
   ```bash
   npm run dev
   ```

7. Access the application:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000

## Project Structure

- `app/` - FastAPI backend
  - `main.py` - Application entry point
  - `routers/` - API route handlers
  - `models.py` - SQLAlchemy models
  - `database.py` - Database connection

- `frontend/` - React frontend
  - `src/` - Source code
  - `public/` - Static assets

- `.devcontainer/` - GitHub Codespaces configuration
  - `devcontainer.json` - Dev container configuration
  - `Dockerfile` - Development container setup

## API Documentation

When the backend is running, access interactive API documentation at:
- OpenAPI UI: http://localhost:8000/docs
- ReDoc UI: http://localhost:8000/redoc

## Key Commands

- Start backend: `uvicorn app.main:app --reload`
- Start frontend: `npm run dev`
- Run tests: `pytest`
- Reset database: `python reset_database.py`

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