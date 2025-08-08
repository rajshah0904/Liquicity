## Relevant Files

- `clean_backend/models/velafi_order.py` – SQLAlchemy model for Velafi orders.
- `clean_backend/models/__init__.py` – Export new model.
- `clean_backend/alembic/versions/<timestamp>_velafi_order.py` – Migration script.
- `clean_backend/schemas.py` – Pydantic schema additions (`VelafiOrderSchema`, `LatamKycStatus`).
- `VelaFi/services/velafi_service.py` – HTTP client wrapper for all VelaFi APIs.
- `clean_backend/services/velafi_monitor.py` – Polling job for pending orders.
- `clean_backend/routers/velafi_kyc.py` – FastAPI routes for KYC start/upload/status.
- `clean_backend/routers/velafi_payment_method.py` – FastAPI routes for order creation (BUY/SELL).
- `clean_backend/routers/webhooks.py` – Add VelaFi webhook handlers.
- `clean_backend/services/regional_kyc_service.py` – Route LATAM countries to VelaFi.
- `pages/wallet/deposit.tsx` – Add LATAM-specific deposit flow.
- `pages/wallet/withdraw.tsx` – Add LATAM-specific withdraw flow.
- `components/RailInstructions.tsx` – New UI component showing Pix/SPEI info.
- `public/config/disclaimer.json` – Country-specific disclaimers.
- `tests/backend/test_velafi_service.py` – Unit tests for service layer.
- `tests/backend/test_velafi_webhooks.py` – Webhook handler tests.
- `tests/frontend/depositLatam.test.tsx` – Jest tests for LATAM deposit UI.

### Notes

- Unit tests are placed alongside or under `tests/` mirroring the directory structure.
- Use `pytest` for backend, `jest` + `react-testing-library` for frontend.

## Tasks

*(Added 6.0 to harden existing models based on best practices.)*

- [ ] 1.0 Database & Schema Migration
  - [ ] 1.1 Create `velafi_order` SQLAlchemy model (`clean_backend/models/velafi_order.py`).
  - [x] 1.2 Export model in `models/__init__.py`.
  - [x] 1.3 Generate Alembic revision for `velafi_order` table and `user_profile` columns.
  - [x] 1.4 Add corresponding Pydantic schema in `clean_backend/schemas.py`.
  - [ ] 1.5 Write migration unit test to ensure table creation.

- [ ] 2.0 Backend Service Layer (VelafiService)
  - [ ] 2.1 Scaffold `VelaFi/services/velafi_service.py` with async HTTPX client.
  - [ ] 2.2 Implement API wrappers: `create_customer`, `upload_documents`, `get_quote`, `create_order`, `poll_order`.
  - [ ] 2.3 Add exponential back-off & idempotency logic.
  - [ ] 2.4 Integrate service into `RegionalKycService.get_kyc_system_for_country`.
  - [ ] 2.5 Implement over-/under-payment tolerance logic & refund/partial-credit policy.
  - [ ] 2.6 Unit tests with mocked HTTP responses (`tests/backend/test_velafi_service.py`).

- [ ] 3.0 API Routers & Webhook Handlers
  - [ ] 3.1 Implement `clean_backend/routers/velafi_kyc.py` (POST `/kyc/start`, `/kyc/documents`, GET `/kyc/status`).
  - [ ] 3.2 Implement `clean_backend/routers/velafi_payment_method.py` (POST `/orders`).
  - [ ] 3.3 Extend `routers/webhooks.py` with handlers for `velafi.kyc.status.changed`, `order.completed`, `order.failed`.
  - [ ] 3.4 Validate HMAC signatures with shared secret.
  - [ ] 3.5 Publish order events to event bus and update DB.
  - [ ] 3.6 Wire new routers into `clean_backend/main.py` (include FastAPI `include_router`).
  - [ ] 3.7 Integration tests for routes & router wiring (`tests/backend/test_velafi_webhooks.py`).

- [ ] 4.0 Frontend Wallet Integration
  - [ ] 4.1 Detect `countryGroup==='LATAM'` in `deposit.tsx` & `withdraw.tsx` and call new backend endpoints.
  - [ ] 4.2 Create `components/RailInstructions.tsx` to render Pix/SPEI/CBU details.
  - [ ] 4.3 Add i18n strings (es, pt-BR) and country disclaimers (`public/config/disclaimer.json`).
  - [ ] 4.4 Add unit/UI tests (`tests/frontend/depositLatam.test.tsx`).
  - [ ] 4.5 Feature-flag rollout & graceful fallback copy.
  - [ ] 4.6 Update CountryPicker/LinkBank component to dynamically show enabled countries (US, EU, LATAM) and call correct flow based on `countryGroup`.
  - [ ] 4.7 Implement `LinkBankCountryGrid` page: dynamic tiles (US, EU active; Brazil, Argentina, Peru marked "Coming Soon").
  - [ ] 4.8 Backed by `/public/config/available_countries.json` or backend `/config/countries` endpoint.
  - [ ] 4.9 Verify end-to-end behaviour with Cypress: select Mexico → VelaFi rails shown; select US/EU → Plaid dialog appears.

- [ ] 5.0 Monitoring, Ops & QA
  - [ ] 5.1 Finalize `velafi_monitor.py` to poll & reconcile `processing` orders.
  - [ ] 5.2 Create Prometheus alerts + Grafana dashboards (webhook failure, pending > 30 min).
  - [ ] 5.3 Add secrets (VELA_APP_ID, VELA_API_KEY, VELA_WEBHOOK_SECRET) to vault & CI envs.
  - [ ] 5.4 Kubernetes CronJob YAML for monitor included in `infra/` repo.
  - [ ] 5.5 Implement OrderEventHandler._allocate_credit to credit bridge / custodial wallets for LATAM flow.
  - [ ] 5.6 Update Treasury sweep job to include LATAM balances.
  - [ ] 5.7 End-to-end Cypress tests for full deposit/withdraw happy path.

- [ ] 6.0 Legacy Models Hardening (optional but recommended)
  - [ ] 6.1 Replace String status/type columns with `SQLEnum` in legacy models.
  - [ ] 6.2 Fix mutable JSON defaults (`default=list`).
  - [ ] 6.3 Switch money fields stored as strings to `Numeric(18,6)`.
  - [ ] 6.4 Convert naive timestamps to timezone-aware `DateTime(timezone=True)` with `server_default=func.now()`.
  - [ ] 6.5 Add `index=True` on high-cardinality FKs.
  - [ ] 6.6 Review cascade options for relationships (e.g., `cascade="all, delete-orphan"`).
  - [ ] 6.7 Migration script to alter existing columns safely.
  - [ ] 6.8 Regression tests to ensure old data loads correctly.
