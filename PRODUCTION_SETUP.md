# Production Database Setup Guide

## 🚀 Production Deployment Options

### Option 1: Direct Connection (Recommended)

For production, connect directly to Google Cloud PostgreSQL:

```bash
# Production DATABASE_URL
DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity
```

**Benefits:**
- ✅ No Cloud SQL Proxy needed
- ✅ Better performance
- ✅ Simpler deployment
- ✅ Works with any hosting platform

**Requirements:**
- SSL certificates configured
- IP whitelist for your production servers

### Option 2: Cloud SQL Proxy (Alternative)

Keep using Cloud SQL Proxy in production:

```bash
# Same as development
DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@localhost/liquicity
```

**Benefits:**
- ✅ Same setup as development
- ✅ Automatic SSL handling
- ✅ Works behind firewalls

**Requirements:**
- Cloud SQL Proxy running on production server
- Google Cloud authentication configured

## 🔧 Production Configuration

### Environment Variables

```bash
# Production Database
DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100
ENVIRONMENT=production

# Security
SECRET_KEY=your-production-secret-key
BRIDGE_API_KEY=your-production-bridge-api-key
AUTH0_DOMAIN=your-production-auth0-domain
AUTH0_API_AUDIENCE=your-production-auth0-audience
```

### SSL Configuration

For direct connection, update `clean_backend/database.py`:

```python
# SSL configuration for Google Cloud SQL
connect_args={
    "sslmode": "require",  # Require SSL for production
    "sslcert": "/path/to/liquicity-client.crt",
    "sslkey": "/path/to/liquicity-client.key",
    "sslrootcert": "/path/to/server-ca.crt"
}
```

## 🌐 Deployment Platforms

### Heroku
```bash
heroku config:set DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity
```

### Google Cloud Run
```bash
gcloud run deploy --set-env-vars DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity
```

### Docker
```dockerfile
ENV DATABASE_URL=postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity
```

### Kubernetes
```yaml
env:
- name: DATABASE_URL
  value: "postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity"
```

## 🔒 Security Considerations

1. **SSL Certificates**: Always use SSL in production
2. **IP Whitelisting**: Restrict access to production servers
3. **Strong Passwords**: Use complex database passwords
4. **Environment Variables**: Never commit secrets to code
5. **Connection Pooling**: Configure appropriate pool sizes

## 📊 Monitoring

### Google Cloud Console
- Monitor database performance
- Set up alerts for high CPU/memory usage
- Track connection counts

### Application Monitoring
- Monitor query performance
- Track connection pool usage
- Set up error alerts

## 🔄 Migration Strategy

1. **Development**: Use Cloud SQL Proxy (localhost)
2. **Staging**: Use direct connection with SSL
3. **Production**: Use direct connection with SSL + monitoring

## 🆘 Troubleshooting

### Connection Issues
```bash
# Test direct connection
psql "postgresql://liquicity_user:Liquicity2024!@34.46.189.225/liquicity"

# Check SSL certificates
openssl s_client -connect 34.46.189.225:5432 -starttls postgres
```

### Performance Issues
- Increase connection pool size
- Monitor slow queries
- Consider read replicas for heavy read workloads 