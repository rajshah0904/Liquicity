FROM mcr.microsoft.com/devcontainers/python:3.9

# Install additional packages needed for the app
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    curl \
    jq \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
    black \
    pylint \
    pytest \
    alembic \
    uvicorn \
    psycopg2-binary \
    bcrypt \
    python-jose

# Set up a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set the working directory
WORKDIR /workspace

# [Optional] Set the default user
USER $USERNAME 