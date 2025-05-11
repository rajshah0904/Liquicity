# Setting Up Liquicity in GitHub Codespaces

This guide provides instructions for running the Liquicity application in GitHub Codespaces.

## Quick Start

1. Click the green "Code" button on your GitHub repository
2. Select the "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for the codespace to be created and initialized
5. Once the environment is ready, open a terminal and run:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. In a new terminal, run the frontend:
   ```bash
   npm run dev
   ```
7. Access your application via the forwarded ports:
   - Backend API: Port 8000
   - Frontend: Port 3000

## Environment Configuration

The Codespace is pre-configured with:

- Python 3.10
- Node.js 18
- PostgreSQL client
- VSCode extensions for development
- Environment variables for database connection

## Database Setup

A PostgreSQL database container is automatically created as part of the Codespace. The database credentials are:

- Host: `db`
- Port: `5432`
- User: `raj`
- Password: `Rajshah11`
- Database: `liquicity`

You can connect to the database using:

```bash
psql postgresql://raj:Rajshah11@db:5432/liquicity
```

## Available Commands

The development environment includes several helpful commands:

- `uvicorn-dev`: Start the FastAPI backend with auto-reload
```bash
  uvicorn-dev
  ```

- Build and run the entire stack:
  ```bash
  docker-compose up
  ```

## Development Workflow

1. The API server runs on port 8000
2. The frontend dev server runs on port 3000
3. Use the VS Code UI to edit files, commit changes, and push to GitHub
4. API changes will auto-reload with uvicorn-dev
5. Frontend changes will auto-reload with npm run dev

## Troubleshooting

If you encounter any issues:

1. Check the terminal output for errors
2. Ensure the database is running:
```bash
   docker ps
   ```
3. Verify database connection:
```bash
   psql postgresql://raj:Rajshah11@db:5432/liquicity -c "SELECT 1"
   ```
4. Restart the application servers if needed

## Custom Configuration

You can customize your environment by modifying:

- `.devcontainer/devcontainer.json`: VS Code settings and extensions
- `.devcontainer/Dockerfile`: Development environment setup
- `.devcontainer/docker-compose.yml`: Container configuration 