-- ============================================
-- SCHEMA DEFINITIONS: GRANT MANAGEMENT SYSTEM
-- ============================================

-- ============================================
-- SCHEMA DEFINITIONS: GRANT MANAGEMENT SYSTEM
-- ============================================

-- ============================================
-- VIEW: vclient
-- ============================================
-- Purpose: Client master data
-- Primary Key: client_hub_key

VIEW vclient
├── client_hub_key          (PRIMARY KEY, VARCHAR)    - Unique client identifier
├── client_id               (VARCHAR)                 - Client ID
└── client_name             (VARCHAR)                 - Client company name


-- ============================================
-- VIEW: vparticipant
-- ============================================
-- Purpose: Participant demographics, KYC, and employment details
-- Primary Key: participant_hub_key
-- Foreign Keys: client_hub_key → vclient.client_hub_key

VIEW vparticipant
├── client_hub_key                  (FOREIGN KEY, VARCHAR)    - Links to vclient
├── participant_hub_key             (PRIMARY KEY, VARCHAR)    - Unique participant identifier
├── first_nm                        (VARCHAR)                 - First name
├── last_nm                         (VARCHAR)                 - Last name
├── account_open_completion_dt      (DATE)                    - Account opening date
├── account_open_completion_status  (VARCHAR)                 - Account status (e.g., ACTIVE, CLOSED)
├── city                            (VARCHAR)                 - Participant's city
├── country_cd                      (VARCHAR)                 - Country code (e.g., US, CN, IN)
├── state                           (VARCHAR)                 - State/province (relevant for US)
├── kyc_status                      (VARCHAR)                 - KYC verification status
├── id_verification_status          (VARCHAR)                 - ID verification status
├── is_director                     (BOOLEAN)                 - Flag if participant is a director
├── is_officer                      (BOOLEAN)                 - Flag if participant is an officer
└── is_blackout_insider             (BOOLEAN)                 - Flag if participant is a blackout insider


-- ============================================
-- VIEW: vGrants
-- ============================================
-- Purpose: Grant awards, vesting schedules, and plan details
-- Grain: One row per vesting tranche (grant_id + vesting_dt combination)
-- Foreign Keys: 
--   - client_hub_key → vclient.client_hub_key
--   - participant_hub_key → vparticipant.participant_hub_key

VIEW vGrants
├── client_hub_key              (FOREIGN KEY, VARCHAR)    - Links to vclient
├── participant_hub_key         (FOREIGN KEY, VARCHAR)    - Links to vparticipant
│
├── PLAN INFORMATION
│   ├── plan_hub_key            (VARCHAR)                 - Plan identifier
│   ├── plan_name               (VARCHAR)                 - Plan name (e.g., "2024 Equity Plan")
│   ├── plan_type               (VARCHAR)                 - Plan type (e.g., ESPP, RSU Plan)
│   ├── plan_start_date         (DATE)                    - Plan start date
│   └── plan_duration           (VARCHAR)                 - Plan duration
│
├── GRANT IDENTIFICATION
│   ├── grant_id                (VARCHAR)                 - Grant identifier
│   ├── grant_award_hub_key     (VARCHAR)                 - Grant award identifier
│   └── description             (VARCHAR)                 - Grant description
│
├── GRANT TYPE
│   ├── grant_type_code         (VARCHAR)                 - Grant type code (e.g., RSU, ISO, NSO)
│   ├── grant_type_description  (VARCHAR)                 - Grant type description
│   └── grant_type_group        (VARCHAR)                 - Grant category/group
│
├── ACCEPTANCE
│   ├── acceptance_cd           (VARCHAR)                 - Acceptance code
│   ├── acceptance_date         (DATE)                    - Date grant was accepted
│   └── acceptance_status       (VARCHAR)                 - Acceptance status
│
├── DATES
│   ├── vesting_dt              (DATE)                    - Vesting date for this tranche
│   ├── expected_expiration_date (DATE)                   - Expected expiration date
│   └── actual_expiration_date  (DATE)                    - Actual expiration date
│
├── FINANCIAL
│   ├── units_granted_amount    (NUMERIC)                 - Number of units granted
│   ├── unit_price              (NUMERIC)                 - Price per unit
│   ├── market_price_at_award   (NUMERIC)                 - Market price at time of award
│   └── fair_value_price        (NUMERIC)                 - Fair value price
│
└── PROCESSING STATUS
    └── is_processed            (BOOLEAN)                 - Whether vesting has been processed


-- ============================================
-- ENTITY RELATIONSHIPS
-- ============================================

-- vclient (1) ─────< (M) vparticipant
--    client_hub_key = client_hub_key

-- vclient (1) ─────< (M) vGrants
--    client_hub_key = client_hub_key

-- vparticipant (1) ─────< (M) vGrants
--    participant_hub_key = participant_hub_key

-- ============================================
-- HIERARCHICAL RELATIONSHIPS IN vGrants
-- ============================================

-- Client → Plans → Grants Hierarchy:
-- 
-- vclient (1) ─────< (M) plan_hub_key
--    One client can have many plans
--    client_hub_key → plan_hub_key (one-to-many)
--
-- plan_hub_key (1) ─────< (M) grant_id
--    One plan can have many grants
--    plan_hub_key → grant_id (one-to-many)
--
-- grant_id (1) ─────< (M) vesting_dt
--    One grant can have many vesting tranches (rows)
--    grant_id → multiple rows with different vesting_dt

-- Example Hierarchy:
--   Client ABC (client_hub_key = 'C001')
--      ├── 2024 Equity Plan (plan_hub_key = 'P001')
--      │   ├── Grant G001
--      │   │   ├── Vesting 2024-06-01
--      │   │   └── Vesting 2024-12-01
--      │   └── Grant G002
--      │       ├── Vesting 2024-06-01
--      │       └── Vesting 2024-12-01
--      └── ESPP 2024 (plan_hub_key = 'P002')
--          └── Grant G003
--              └── Vesting 2024-07-01

-- Key Notes:
-- 1. One client can have many participants
-- 2. One participant can have many grants
-- 3. One client can have many plans (within vGrants)
-- 4. One plan can have many grants (within vGrants)
-- 5. One grant can have many vesting tranches (represented as multiple rows in vGrants)
-- 6. vGrants is denormalized with plan details included for easier querying
