## Relevant Files

- `clean_backend/services/velafi_client.py` – Typed async client wrapping VelaFi REST endpoints & signature verification.
- `clean_backend/routers/onramp.py` – FastAPI routes for payment-method creation & order initiation.
- `clean_backend/routers/webhooks_velafi.py` – FastAPI route that receives VelaFi webhooks & triggers wallet credit.
- `clean_backend/services/velafi_monitor.py` – Background reconciliation/polling task for unsettled orders.
- `clean_backend/models/onramp.py` – SQLAlchemy models for `onramp_payment_methods` and `onramp_orders` tables.
- `alembic/versions/xxxx_onramp_tables.py` – DB migration creating new tables & indexes.
- `clean_backend/config/settings.py` – Adds new env-config fields (`VELAFI_API_KEY`, etc.).
- `docs/VELAFI_ONRAMP_API.md` – Developer-facing request/response reference & sequence diagrams.
- `docs/samples/velafi_onramp.postman_collection.json` – Postman collection for QA & partners.
- `lib/api.ts` – TypeScript interfaces + helper methods for frontend Plaid team.
- `tests/unit/test_velafi_client.py` – Unit tests for VelaFi client wrapper.
- `tests/integration/test_onramp_flow.py` – End-to-end happy-path tests (mocked VelaFi sandbox).

### Notes

- Unit tests live in `tests/` mirroring source tree; use `pytest -q`.
- Migration file name `xxxx_onramp_tables.py` will be prefixed with timestamp by Alembic autogenerate.

## Tasks

- [ ] **1.0 Backend Foundation**
  - [ ] 1.1 Scaffold `services/velafi_client.py` with async session & base URL config.
  - [ ] 1.2 Implement `add_payment_method`, `create_order`, `get_order`, `verify_signature`, plus idempotency + retry helpers.
  - [ ] 1.3 Write unit tests for client success & error paths.

- [ ] **2.0 API Routes**
  - [ ] 2.1 Create `routers/onramp.py`; add `POST /onramp/payment_method` with security/validation.
  - [ ] 2.2 Add `POST /onramp/order` integrating security checks & event emission.
  - [ ] 2.3 Register router in `clean_backend/main.py` + update OpenAPI tags.

- [ ] **3.0 Webhook Handling**
  - [ ] 3.1 Create `routers/webhooks_velafi.py`; implement HMAC signature validation (`x-velafi-signature`).
  - [ ] 3.2 Handle `order.completed` (credit via Bridge) & `order.failed` (error pipeline).
  - [ ] 3.3 Add integration tests covering both webhook paths.

- [ ] **4.0 Background Monitor**
  - [ ] 4.1 Implement `services/velafi_monitor.py` polling logic with configurable interval.
  - [ ] 4.2 Integrate with existing scheduler/worker (Celery or FastAPI task runner).
  - [ ] 4.3 Emit `order.status_changed` events for admin dashboard.

- [ ] **5.0 Database & Models**
  - [ ] 5.1 Design SQLAlchemy models in `models/onramp.py` reflecting PRD schema.
  - [ ] 5.2 Create Alembic migration `xxxx_onramp_tables.py` generating tables & indexes.
  - [ ] 5.3 Update `__init__.py` exports for model discovery.

- [ ] **6.0 Security & Limits**
  - [ ] 6.1 Extend `services/security.py` with `is_deposit_allowed` (AML / velocity thresholds).
  - [ ] 6.2 Add env-configurable thresholds and defaults.
  - [ ] 6.3 Unit tests for edge-limit enforcement.

- [ ] **7.0 Configuration**
  - [ ] 7.1 Add new settings in `config/settings.py` with type hints & default values.
  - [ ] 7.2 Update `.env.example` / README with new variables.

- [ ] **8.0 Documentation & Samples**
  - [ ] 8.1 Draft `docs/VELAFI_ONRAMP_API.md` including sequence diagrams.
  - [ ] 8.2 Produce Postman collection and place in `docs/samples/`.
  - [ ] 8.3 Update `docs/BRIDGE_PAYMENT_SYSTEM.md` adding on-ramp section.

- [ ] **9.0 CI/CD & Secrets**
  - [ ] 9.1 Update GitHub Actions workflow to run new tests.
  - [ ] 9.2 Add secret placeholders (`VELAFI_API_KEY`, `VELAFI_WEBHOOK_SECRET`).

- [ ] **10.0 Frontend Contract (Plaid Team)**
  - [ ] 10.1 Add TypeScript interfaces & helper functions in `lib/api.ts`.
  - [ ] 10.2 Publish API contract docs for frontend handoff.

- [ ] **11.0 Deployment Checklist**
  - [ ] 11.1 Provision VelaFi sandbox credentials & whitelist IPs.
  - [ ] 11.2 Configure webhook URL in VelaFi dashboard.
  - [ ] 11.3 Populate staging `.env` and verify end-to-end happy path. 