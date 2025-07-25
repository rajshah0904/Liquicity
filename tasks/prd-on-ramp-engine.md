# On-Ramp Engine (VelaFi Integration) – Product Requirements Document

## 1. Introduction / Overview
The On-Ramp Engine enables Liquicity users to convert fiat currency held in their external bank accounts into USDC, credited directly to their Bridge-hosted crypto wallets. The engine leverages **VelaFi’s fiat→crypto API** as the settlement layer. Bank-account linking and ACH authorization will be handled by a separate Plaid integration; this document focuses solely on the VelaFi workflow and its interaction with existing backend services.

## 2. Goals
1. Allow a fully KYC-verified user to deposit fiat (USD in v1) and receive USDC in their Bridge wallet in ≤10 minutes under normal conditions.
2. Provide an API endpoint that Plaid integration can call with account details to initiate an on-ramp order via VelaFi.
3. Automate order status monitoring and USDC crediting through webhook callbacks.
4. Persist full audit trail (order IDs, timestamps, FX rates, fees) for compliance and reconciliation.
5. Design with extensibility for additional rails (SPEI, SEPA) and stablecoins (USDT, DAI) in later phases.

## 3. User Stories
* **US-01** – *As a KYC-verified user*, I want to deposit funds from my linked US bank account, *so that* I can obtain USDC in my Liquicity wallet to trade or pay.
* **US-02** – *As a product manager*, I want to see real-time order status updates, *so that* I can monitor conversion performance and proactively handle failures.
* **US-03** – *As a finance ops analyst*, I want a reconciliation report matching VelaFi orders to Bridge wallet deposits, *so that* we satisfy regulatory and auditing requirements.

## 4. Functional Requirements
1. **Add Payment Method** – Endpoint `POST /onramp/payment_method`:
   • `user_id` (UUID)  
   • `plaid_token` (string)  
   – Calls VelaFi **Add Payment Method** and returns/stores `payment_method_id`, `fiat_rail`, `country`, and `currency`.  
   – Idempotent on `(user_id, plaid_token)` within 10 min (returns existing record).
2. **Create On-Ramp Order** – Endpoint `POST /onramp/order`:
   • `user_id`  
   • `fiat_amount`  
   • `payment_method_id` (FK from #1)  
   – Calls VelaFi **Create Fiat→Crypto Order** and stores `velafi_order_id`, `quote_rate`, `fee_usd`.  
   – Runs `EnhancedSecurityService.is_deposit_allowed()` before hitting VelaFi.
3. **Webhook Listener** – `POST /webhooks/velafi` (HMAC SHA-256, header `x-velafi-signature`):
   • Verify timestamp ±5 min to mitigate replay.  
   • Handle `order.completed` (USDC credit) & `order.failed` (surface error).
4. **Order Polling Fallback** – Async task `services/velafi_monitor.py` (or extend `transaction_monitor.py`) polls orders in `pending/processing` >5 min & reconciles state.
5. **USDC Credit Logic** – On `order.completed`, call `BridgeAPIClient.create_usdc_transfer_request`; credit timing (instant vs post-clearing) driven by config flag `ONRAMP_RISK_FORWARD=true|false`.
6. **Compliance Flags** – Reject if over env-configured limits *or* security service returns `risk_score > threshold`.
7. **Audit Logging** – Persist full request/response snapshots (minus PII) and state transitions in `onramp_orders`.
8. **Admin Dashboard Hooks** – Emit internal event bus message `order.status_changed` for React admin.

## 5. Non-Goals (Out of Scope for v1)
* Building UI components for the Plaid flow (handled by separate team).
* Supporting non-USD fiat or non-USDC stablecoins.
* Manual review workflows (assume auto-approve if within limits).
* Off-ramp (crypto→fiat) functionality.

## 6. Design Considerations (UX / UI)
* Frontend shows a progress tracker: *Initiated → Processing → Completed / Failed*.
* Display VelaFi quoted FX rate and estimated fees before user confirms.
* Warn user that ACH pulls may take up to 3 business days; funds will appear as pending until order completion.

## 7. Technical Considerations
* **Authentication** – VelaFi API key stored in Vault / env `VELAFI_API_KEY`; FastAPI dependency injects a singleton `VelaFiClient` similar to `BridgeAPIClient`.
* **Database** – New tables / columns:
  ```
  -- onramp_payment_methods
  id (PK) | user_id | payment_method_id | plaid_token_hash | fiat_rail | country | currency | created_at

  -- onramp_orders (adds new cols)
  id (PK) | user_id | payment_method_id (FK) | velafi_order_id | fiat_amount | fiat_currency | fiat_rail
  status  | usdc_amount | quote_rate | fee_usd | raw_payload JSONB | created_at | updated_at
  ```
* **Service Layer** – `services/velafi_client.py` wraps core endpoints: create_order, get_order, list_payment_methods, etc.
* **Webhook Security** – Validate `x-velafi-signature: {t=timestamp,v1=sha256}` header; reject if timestamp drift >5 min.
* **Background Monitor** – `velafi_monitor.py` runs every minute (Celery/async) to reconcile orphaned orders.
* **Retry Strategy** – Fibonacci back-off (max 5 attempts) for network failures.
* **Extensibility** – Store `country` & `currency` on **payment_method** to drive future SPEI / SEPA rails.
* **Testing** – Use VelaFi Sandbox environment; mock responses for CI.

## 8. Success Metrics
| Metric | Standard (post-settlement) | Express (instant credit) |
|--------|---------------------------|--------------------------|
| On-ramp completion time (p95) | 3 business days | ≤15 min |
| Order success rate | ≥95 % | ≥97 % |
| Support tickets /1 000 deposits | <2 | <2 |
| Reconciliation mismatches /mo | 0 | 0 |

## 9. Open Questions
1. Which additional regions (LATAM / Europe) are priority for phase 2?  
2. Exact daily / monthly deposit limits and AML thresholds?  
3. Do we need real-time FX quote locking, or can we allow slippage?  
4. What branding / copy needs to accompany VelaFi disclosures?  
5. **USDC credit risk timing** – instant vs post-clearing (requires legal approval).  
6. SLA for webhook delivery from VelaFi – do we need a dead-letter queue?  
7. Required velocity / AML thresholds for `EnhancedSecurityService`.  
8. Should we add dual-approval for deposits >$10 k?

---
**Next Steps**  
• Engineering to estimate effort and identify API surface changes needed in existing FastAPI codebase.  
• Security team to complete VelaFi vendor review.  
• Product to answer open questions and finalise limits before development sprint. 