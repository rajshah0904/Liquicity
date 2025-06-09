# Build stage
FROM rust:1.70 as builder

WORKDIR /app

# Copy the Cargo.toml and Cargo.lock files
COPY Cargo.toml Cargo.lock ./

# Copy the source code
COPY src ./src

# Build the application
RUN cargo build --release

# Final stage
FROM debian:bullseye-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the built binary from the builder stage
COPY --from=builder /app/target/release/security-service ./security-service

# Copy environment files
COPY .env ./

# Expose ports
EXPOSE 8080

# Start command
CMD ["./security-service"] 