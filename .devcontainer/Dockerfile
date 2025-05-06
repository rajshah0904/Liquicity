FROM mcr.microsoft.com/devcontainers/python:3.10

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs \
 && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install PostgreSQL client
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-client \
 && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspaces/Liquicity

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Install tooling
RUN pip3 install uvicorn pytest black pylint \
 && npm install -g npm@latest

# Mark that we're in a devcontainer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=development \
    DEVCONTAINER=1

# Configure ZSH for the 'vscode' user
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
 && echo 'export PATH=$PATH:/workspaces/Liquicity/node_modules/.bin' >> /home/vscode/.zshrc \
 && echo 'alias uvicorn-dev="uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"' >> /home/vscode/.zshrc

# Setup entrypoint
COPY .devcontainer/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
