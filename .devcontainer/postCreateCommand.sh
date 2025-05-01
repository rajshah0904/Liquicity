#!/bin/bash
set -e

# Display banner
echo "========================================================"
echo "   Setting up Liquicity development environment...   "
echo "========================================================"

# Create .env file if it doesn't exist
if [ ! -f "/workspace/.env" ]; then
  echo "Creating .env file from example..."
  cp /workspace/.env.example /workspace/.env
fi

# Make the database initialization script executable
chmod +x /workspace/.devcontainer/init-scripts/init-db.sh

# Run database initialization script
echo "Initializing database..."
sudo -u vscode bash /workspace/.devcontainer/init-scripts/init-db.sh

# Install Python requirements
echo "Installing Python dependencies..."
cd /workspace
pip install --user -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd /workspace/frontend
npm install

echo "========================================================"
echo "   Liquicity environment setup complete!   "
echo ""
echo "   To start the backend:   "
echo "   $ cd /workspace && python -m app.main   "
echo ""
echo "   To start the frontend:   "
echo "   $ cd /workspace/frontend && npm start   "
echo "========================================================" 