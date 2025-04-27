# TerraFlow GitHub Codespaces Setup Guide

This guide explains how to use GitHub Codespaces for developing the TerraFlow application.

## Getting Started with Codespaces

GitHub Codespaces provides a complete, configured development environment in the cloud that opens directly in your browser. Follow these steps to get started:

### 1. Creating a Codespace

1. Navigate to the [TerraFlow repository](https://github.com/yourusername/terraflow) on GitHub
2. Click the "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on main"

This will create a new Codespace with all the necessary tools and dependencies pre-configured. The setup might take a few minutes the first time.

### 2. Exploring Your Codespace

Once your Codespace is ready, you'll see:

- A VS Code interface in your browser
- A terminal at the bottom
- The project files in the explorer on the left

The Codespace comes pre-configured with:
- Python 3.9
- Node.js 16
- PostgreSQL
- All required extensions for development

### 3. Accessing the Application

When the Codespace starts, the initialization scripts will:
1. Set up the PostgreSQL database
2. Create test users automatically
3. Install dependencies for both backend and frontend

To run the application:

**Backend:**
```bash
cd /workspace
python -m app.main
```

**Frontend:**
```bash
cd /workspace/frontend
npm start
```

You can access:
- Backend API: https://[your-codespace-name]-8000.app.github.dev
- Frontend: https://[your-codespace-name]-3000.app.github.dev
- API Docs: https://[your-codespace-name]-8000.app.github.dev/docs

### 4. Database Access

The PostgreSQL database is running in the Codespace and can be accessed:

- **From VS Code:** Use the PostgreSQL extension (installed by default)
- **From terminal:**
  ```bash
  psql -U postgres -d terraflow
  ```
- **Connection details:**
  - Host: localhost
  - Port: 5432
  - Username: postgres
  - Password: postgres
  - Database: terraflow

### 5. Managing Environment Variables

Environment variables are pre-configured for development, but you can add or modify sensitive values:

1. In GitHub, go to your repository
2. Navigate to Settings > Secrets and variables > Codespaces
3. Add your secrets (like API keys)

For local Codespace-only variables, you can also edit the `.env` file directly.

## Workflow Tips

### Committing Changes

You can commit and push changes directly from the Codespace:

1. Make your changes
2. Open the Source Control panel (Ctrl+Shift+G)
3. Stage, commit, and push your changes

### Working with Multiple Developers

Codespaces makes it easy to collaborate:

- **Share your Codespace:** Click the share button in the bottom-left corner
- **Codespace Portability:** Stop your Codespace and resume it from any computer
- **Simultaneous Access:** Multiple team members can each have their own Codespace for the same repository

### Port Forwarding

Your Codespace automatically forwards ports for the application:
- Backend (8000)
- Frontend (3000)
- PostgreSQL (5432)

You can access these from the "PORTS" tab in the terminal area.

## Troubleshooting

### Database Issues

If you encounter database connection issues:

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -U postgres

# Reset the database if needed
cd /workspace
python reset_database.py
```

### Environment Setup Issues

For environment issues:

```bash
# Check environment variables
env | grep DATABASE_URL

# Manually rerun initialization
sudo bash /workspace/.devcontainer/init-scripts/init-db.sh
```

### Application Errors

If you encounter application errors:

1. Check the terminal output for error messages
2. Verify database connection
3. Ensure all required environment variables are set

## Need Help?

If you encounter any issues with your Codespace that you can't resolve, please contact the project maintainer or open an issue in the GitHub repository. 