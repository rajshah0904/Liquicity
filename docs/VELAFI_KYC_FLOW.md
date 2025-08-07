# VelaFi KYC Flow Documentation

## Overview

The VelaFi KYC system provides a complete end-to-end Know Your Customer (KYC) solution for LATAM users, separate from the Bridge KYC system used for US/EU users. This document outlines the architecture, API endpoints, and integration flow.

## Architecture

### Regional KYC System

The system uses a **regional KYC router** that determines which KYC provider to use based on the user's country:

- **US/EU Countries**: Bridge KYC (hosted link flow)
- **LATAM Countries**: VelaFi KYC (direct API integration)

### VelaFi KYC Components

1. **VelaFi Client** (`VelaFi/velafi_client.py`): API client for VelaFi KYC endpoints
2. **VelaFi KYC Service** (`VelaFi/services/velafi_kyc_service.py`): Business logic layer
3. **VelaFi KYC Router** (`clean_backend/routers/velafi_kyc.py`): API endpoints
4. **Regional KYC Service** (`VelaFi/services/regional_kyc_service.py`): Country-based routing
5. **Regional KYC Router** (`clean_backend/routers/regional_kyc.py`): Unified KYC interface
6. **Database Models** (`VelaFi/models.py`): VelaFi customer and document storage

## API Endpoints

### Regional KYC Router (`/kyc/*`)

#### Get KYC Requirements
```http
GET /kyc/requirements/{country_code}
```

**Response:**
```json
{
  "system": "velafi",
  "type": "direct_api",
  "required_fields": ["first_name", "last_name", "email", "date_of_birth", "phone", "address"],
  "required_documents": ["national_id", "proof_of_address"],
  "description": "VelaFi direct KYC for LATAM compliance",
  "country_specific": {
    "MX": {"id_type": "INE", "tax_id": "RFC"},
    "BR": {"id_type": "CPF", "tax_id": "CPF"}
  }
}
```

#### Get KYC Status
```http
GET /kyc/status?country_code=MX
```

#### Check KYC Approval
```http
GET /kyc/approved?country_code=MX
```

#### Get Supported Countries
```http
GET /kyc/supported-countries
```

### VelaFi KYC Router (`/velafi/kyc/*`)

#### Create Customer
```http
POST /velafi/kyc/customer
```

**Request Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan.perez@example.com",
  "date_of_birth": "1990-01-01",
  "country": "MX",
  "phone": "+525512345678",
  "address": "Av. Reforma 123",
  "city": "Ciudad de México",
  "state": "CDMX",
  "postal_code": "06000"
}
```

#### Get Customer
```http
GET /velafi/kyc/customer
```

#### Upload Document
```http
POST /velafi/kyc/documents
Content-Type: multipart/form-data

document_type: national_id
file: [binary file data]
```

#### Check KYC Approval
```http
GET /velafi/kyc/approved
```

## Database Schema

### velafi_customers Table
```sql
CREATE TABLE velafi_customers (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users_v2(id),
    velafi_customer_id VARCHAR(64) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(10) NOT NULL,
    country VARCHAR(2) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    kyc_status VARCHAR(20) DEFAULT 'pending',
    kyc_submitted_at TIMESTAMP,
    kyc_verified_at TIMESTAMP,
    rejection_reasons TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### velafi_kyc_documents Table
```sql
CREATE TABLE velafi_kyc_documents (
    id UUID PRIMARY KEY,
    velafi_customer_id UUID REFERENCES velafi_customers(id),
    velafi_document_id VARCHAR(64) UNIQUE NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'uploaded',
    uploaded_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP,
    rejection_reason TEXT
);
```

## KYC Status Values

- `pending`: Customer created, no documents uploaded
- `submitted`: Documents uploaded, under review
- `approved`: KYC verification completed successfully
- `rejected`: KYC verification failed
- `under_review`: Manual review in progress

## Integration with On-Ramp

The VelaFi KYC system integrates with the on-ramp flow:

1. **Pre-flight Check**: Before creating payment methods or orders, the system checks if the user has completed VelaFi KYC
2. **KYC Requirement**: Users must have `kyc_status = "approved"` to proceed with on-ramp operations
3. **Error Handling**: Returns 403 Forbidden if KYC is not completed

## Event Bus Integration

The VelaFi KYC system publishes events for monitoring and integration:

- `velafi.customer.created`: New customer created
- `velafi.customer.updated`: Customer information updated
- `velafi.kyc.session.created`: KYC session initiated
- `velafi.document.uploaded`: Document uploaded
- `velafi.document.deleted`: Document deleted

## Security Considerations

1. **File Upload Validation**: Only JPEG, PNG, and PDF files up to 10MB
2. **Authentication**: All endpoints require valid JWT token
3. **Idempotency**: API calls use idempotency keys to prevent duplicates
4. **Data Encryption**: Sensitive data encrypted in transit and at rest
5. **Audit Trail**: All operations logged with timestamps and user IDs

## Frontend Integration

### Country Selection
The frontend should:
1. Allow users to select their country
2. Query `/kyc/requirements/{country_code}` to get KYC requirements
3. Show appropriate form fields based on the response
4. Route to the correct KYC system (Bridge or VelaFi)

### VelaFi KYC Flow
1. **Customer Creation**: Submit customer data to `/velafi/kyc/customer`
2. **Document Upload**: Upload required documents to `/velafi/kyc/documents`
3. **Status Monitoring**: Poll `/velafi/kyc/approved` for approval status
4. **Proceed to On-Ramp**: Once approved, user can access on-ramp features

## Testing

### Test Scenarios
1. **Customer Creation**: Create customer with valid data
2. **Document Upload**: Upload various document types
3. **Status Updates**: Verify status changes through the flow
4. **Error Handling**: Test with invalid data and missing fields
5. **Regional Routing**: Test country-based KYC system selection

### Test Data
```json
{
  "test_customer": {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "date_of_birth": "1990-01-01",
    "country": "MX",
    "phone": "+525512345678",
    "address": "Test Address 123",
    "city": "Test City",
    "state": "Test State",
    "postal_code": "12345"
  }
}
```

## Migration Guide

### Database Migration
```bash
# Run the VelaFi KYC migration
alembic upgrade head
```

### Environment Variables
```bash
# VelaFi API configuration
VELAFI_API_KEY=your_api_key
VELAFI_BASE_URL=https://sandbox-api.velafi.com/v1
```

## Monitoring and Analytics

### Key Metrics
- KYC completion rate by country
- Document upload success rate
- Average KYC processing time
- Rejection reasons and frequency

### Logging
- All KYC operations logged with structured data
- Error tracking for failed operations
- Performance monitoring for API calls

## Support and Troubleshooting

### Common Issues
1. **Document Upload Failures**: Check file size and format
2. **KYC Status Not Updating**: Verify webhook configuration
3. **Regional Routing Errors**: Check country code format

### Debug Endpoints
- `/kyc/system/{country_code}`: Check KYC system for country
- `/velafi/kyc/customer`: Get customer details
- `/kyc/status`: Check current KYC status

## Future Enhancements

1. **Additional Document Types**: Support for more document formats
2. **Automated Verification**: AI-powered document verification
3. **Multi-language Support**: Localized KYC forms
4. **Mobile SDK**: Native mobile KYC integration
5. **Compliance Reporting**: Automated regulatory reporting 