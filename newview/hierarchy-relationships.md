# Hierarchical Relationships in Grant Management System

This document explains the hierarchical structure within the vGrants view and its query implications.

---

## 📊 The Hierarchy

```
Client (client_hub_key)
  │
  ├─── Plan 1 (plan_hub_key)
  │     │
  │     ├─── Grant A (grant_id)
  │     │     ├─── Vesting 2024-06-01 (row 1)
  │     │     ├─── Vesting 2024-12-01 (row 2)
  │     │     └─── Vesting 2025-06-01 (row 3)
  │     │
  │     └─── Grant B (grant_id)
  │           ├─── Vesting 2024-06-01 (row 4)
  │           └─── Vesting 2024-12-01 (row 5)
  │
  └─── Plan 2 (plan_hub_key)
        │
        └─── Grant C (grant_id)
              └─── Vesting 2024-07-01 (row 6)
```

---

## 🔗 Cardinality Rules

### Level 1: Client → Plans
**One client_hub_key → Many plan_hub_key**

```sql
-- Example: How many plans does each client have?
SELECT 
    client_hub_key,
    COUNT(DISTINCT plan_hub_key) AS plan_count
FROM vGrants
GROUP BY client_hub_key;
```

**Real-world example:**
- Client "ABC Corp" might have:
  - "2024 Equity Plan"
  - "ESPP 2024"
  - "Executive Bonus Plan"
  - "Director Compensation Plan"

---

### Level 2: Plan → Grants
**One plan_hub_key → Many grant_id**

```sql
-- Example: How many grants in each plan?
SELECT 
    plan_name,
    plan_type,
    COUNT(DISTINCT grant_id) AS grant_count
FROM vGrants
GROUP BY plan_name, plan_type;
```

**Real-world example:**
- Plan "2024 Equity Plan" might contain:
  - 500 RSU grants to employees
  - 50 ISO grants to executives
  - 25 NSO grants to consultants

---

### Level 3: Grant → Vesting Tranches
**One grant_id → Many rows (vesting_dt)**

```sql
-- Example: Show all vesting tranches for a grant
SELECT 
    grant_id,
    vesting_dt,
    units_granted_amount,
    is_processed
FROM vGrants
WHERE grant_id = 'G001'
ORDER BY vesting_dt;
```

**Real-world example:**
- Grant G001 (4-year vest, annual schedule):
  - Row 1: Vesting 2024-01-01 (25% of shares)
  - Row 2: Vesting 2025-01-01 (25% of shares)
  - Row 3: Vesting 2026-01-01 (25% of shares)
  - Row 4: Vesting 2027-01-01 (25% of shares)

**This is why vGrants has multiple rows per grant!**

---

## ⚠️ Critical Implications for Queries

### 1. Always Use DISTINCT When Counting

❌ **WRONG:**
```sql
-- This counts ROWS (vesting tranches), not grants!
SELECT COUNT(*) FROM vGrants;  -- Returns 10,000 rows

-- This counts ROWS per client, not grants!
SELECT 
    client_hub_key,
    COUNT(*) AS grant_count  -- WRONG!
FROM vGrants
GROUP BY client_hub_key;
```

✅ **CORRECT:**
```sql
-- Count distinct grants
SELECT COUNT(DISTINCT grant_id) FROM vGrants;  -- Returns 2,500 grants

-- Count grants per client
SELECT 
    client_hub_key,
    COUNT(DISTINCT grant_id) AS grant_count  -- CORRECT!
FROM vGrants
GROUP BY client_hub_key;
```

---

### 2. Filtering by Client Gets ALL Plans

When you filter by client, you automatically get data from all plans under that client.

```sql
-- This returns grants from ALL plans for this client
SELECT 
    plan_name,
    COUNT(DISTINCT grant_id) AS grant_count
FROM vGrants
WHERE client_hub_key = 'C001'
GROUP BY plan_name;
```

**Result might show:**
- 2024 Equity Plan: 500 grants
- ESPP 2024: 300 grants
- Executive Bonus: 50 grants

---

### 3. Filtering by Plan Gets ALL Grants in That Plan

```sql
-- This returns ALL grants in this plan, across all grant types
SELECT 
    grant_type_description,
    COUNT(DISTINCT grant_id) AS grant_count
FROM vGrants
WHERE plan_name = '2024 Equity Plan'
GROUP BY grant_type_description;
```

**Result might show:**
- RSU: 400 grants
- ISO: 80 grants
- NSO: 20 grants

---

### 4. Understanding Row Count vs Entity Count

```sql
-- Query to see the difference
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT grant_id) AS distinct_grants,
    COUNT(DISTINCT plan_hub_key) AS distinct_plans,
    COUNT(DISTINCT client_hub_key) AS distinct_clients,
    COUNT(DISTINCT participant_hub_key) AS distinct_participants
FROM vGrants;
```

**Example result:**
- Total Rows: 10,000 (vesting tranches)
- Distinct Grants: 2,500 (individual grants)
- Distinct Plans: 25 (plans across all clients)
- Distinct Clients: 5 (total clients)
- Distinct Participants: 1,800 (people with grants)

---

## 📋 Common Query Patterns

### Pattern 1: Client → Plans Breakdown
```sql
SELECT 
    c.client_name,
    g.plan_name,
    g.plan_type,
    COUNT(DISTINCT g.plan_hub_key) AS plan_instances,
    COUNT(DISTINCT g.grant_id) AS grant_count,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count
FROM vclient c
JOIN vGrants g ON g.client_hub_key = c.client_hub_key
GROUP BY c.client_name, g.plan_name, g.plan_type
ORDER BY c.client_name, grant_count DESC;
```

---

### Pattern 2: Plan → Grant Types Breakdown
```sql
SELECT 
    plan_name,
    plan_type,
    grant_type_description,
    COUNT(DISTINCT grant_id) AS grant_count,
    SUM(units_granted_amount) AS total_units
FROM vGrants
GROUP BY plan_name, plan_type, grant_type_description
ORDER BY plan_name, grant_count DESC;
```

---

### Pattern 3: Grant → Vesting Schedule
```sql
SELECT 
    grant_id,
    plan_name,
    grant_type_description,
    vesting_dt,
    units_granted_amount,
    is_processed,
    ROW_NUMBER() OVER (PARTITION BY grant_id ORDER BY vesting_dt) AS tranche_number
FROM vGrants
WHERE participant_hub_key = 'P001'
ORDER BY grant_id, vesting_dt;
```

---

## 🎯 Key Takeaways

1. **vGrants is denormalized** - It contains plan details repeated across all grants in that plan

2. **One row = One vesting tranche** - Not one grant, not one plan, but one specific vesting event

3. **Always use DISTINCT** when counting:
   - `COUNT(DISTINCT grant_id)` for grants
   - `COUNT(DISTINCT plan_hub_key)` for plans
   - `COUNT(DISTINCT client_hub_key)` for clients
   - `COUNT(DISTINCT participant_hub_key)` for participants

4. **The hierarchy flows downward**:
   - Filter by client → Get all its plans → Get all grants in those plans
   - Filter by plan → Get all grants in that plan
   - Filter by grant → Get all vesting tranches for that grant

5. **GROUP BY controls the level of detail**:
   - `GROUP BY client_hub_key` → Client-level summary
   - `GROUP BY plan_name, plan_type` → Plan-level summary
   - `GROUP BY grant_id` → Grant-level summary
   - No GROUP BY + specific grant_id filter → Vesting tranche detail

---

## 🧪 Testing Your Understanding

**Question:** If a query returns 1,000 rows from vGrants, what does that tell you?

**Answer:** It tells you there are 1,000 vesting tranches. It does NOT tell you:
- How many grants (could be 250 grants with 4 tranches each)
- How many plans (could be 5 plans)
- How many participants (could be 200 participants)

**Always use DISTINCT to count entities!**

---

## 📖 Related Documentation

- See **schema-definitions.sql** for the complete ER diagram
- See **business-rules.md** Section 7 for join rules
- See **example-queries.sql** Q19-Q24 for hierarchy query examples
