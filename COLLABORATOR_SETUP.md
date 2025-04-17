# TerraFlow Collaborator Setup Guide

Welcome to the TerraFlow project! This guide will help you set up the necessary database and test users to start contributing to the project.

## Quick Setup (Recommended)

We've created an automated setup script that will handle the PostgreSQL database setup, table creation, and test user creation for you:

```bash
# Install required packages
pip install psycopg2-binary bcrypt

# Run the setup script
python setup_postgres.py
```

This script will:
1. Check if PostgreSQL is installed
2. Create the database and user
3. Set up all necessary tables
4. Create a test user with the following credentials:
   - Username: testuser
   - Password: test123
   - Initial balance: $10,000 USD and 5,000 USDT
5. Update your .env file with the correct database connection string

If you prefer to set up the database manually, follow the instructions below.

## Manual Database Setup

TerraFlow uses PostgreSQL as its database. Follow these steps to set up the database:

### 1. Install PostgreSQL

If you haven't already, install PostgreSQL:

- **Mac**: `brew install postgresql`
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 2. Create the Database

```bash
# Start PostgreSQL service
# Mac
brew services start postgresql

# Linux
sudo service postgresql start

# Windows
# Start from Services application

# Connect to PostgreSQL
psql -U postgres

# Inside psql, create the database
CREATE DATABASE terraflow;
CREATE USER raj WITH ENCRYPTED PASSWORD 'Rajshah11';
GRANT ALL PRIVILEGES ON DATABASE terraflow TO raj;
\q
```

### 3. Configure the Database URL

Create or update the `.env` file in the project root:

```
DATABASE_URL=postgresql://raj:Rajshah11@localhost:5432/terraflow
APP_URL=http://localhost:3000
```

## Create Test Users

We have scripts to quickly create test users with wallets and balances:

```bash
# Activate the virtual environment
source my_env/bin/activate  # On Windows: my_env\Scripts\activate

# Run the test user creation script
python create_test_user.py
```

This will create a test user with:
- Username: testuser
- Password: test123
- Email: test@example.com
- Role: admin
- Initial balance: $10,000 USD and 5,000 USDT

You can also create a second test user with:

```bash
python create_second_test_user.py
```

## Alternative: SQLite for Development

If you prefer using SQLite for development (simpler setup), modify your `.env` file:

```
DATABASE_URL=sqlite:///./terraflow.db
```

Then run the setup scripts which will use SQLite instead of PostgreSQL.

## Starting the Application

Once your database is set up:

```bash
# Start the backend
source my_env/bin/activate  # On Windows: my_env\Scripts\activate
python -m app.main

# In a separate terminal, start the frontend
cd frontend
npm install
npm start
```

The application should now be running with:
- Backend at http://localhost:8000
- Frontend at http://localhost:3000

## Troubleshooting

If you encounter the "Failed to load resource: the server responded with a status of 500 (Internal Server Error)" message:

1. Check the terminal running the backend for error messages
2. Ensure the database is properly set up and accessible
3. Verify your .env file has the correct DATABASE_URL

For further questions, please contact the project maintainer. 