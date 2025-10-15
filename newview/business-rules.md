# Business Rules: Grant Management System

## 1. Geographic Data Rules

### Country and State Handling
- **Country Code**: Use `country_cd` field for all country-level analysis
- **State/Province**: Use `state` field for regional analysis

### Geographic Aggregations
- **Country Summary**: `GROUP BY country_cd` for participant counts by country

---

## 2. Date and Time Rules

### Current Date
- **Always** use `CURRENT_DATE` for today's date in queries

### Future Date Ranges
- **"Next X days"**: 
  ```sql
  WHERE vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL 'X days'
  ```
- **"After today"**: Use `> CURRENT_DATE` (not `>= CURRENT_DATE`)

### Next Vesting Date Logic
- **"Next vesting date"** means the **minimum date greater than today**:
  ```sql
  -- Method 1: Using MIN
  SELECT MIN(vesting_dt) 
  FROM vGrants 
  WHERE vesting_dt > CURRENT_DATE
  
  -- Method 2: Using LIMIT (preferred for single result)
  SELECT vesting_dt 
  FROM vGrants 
  WHERE vesting_dt > CURRENT_DATE 
  ORDER BY vesting_dt ASC 
  LIMIT 1
  ```

---

## 3. Vesting Event Rules

### Identifying Vesting Events
- **Vesting Date**: Use `vesting_dt` field from vGrants
- **Upcoming Vestings**: `vesting_dt > CURRENT_DATE`
- **Past Vestings**: `vesting_dt <= CURRENT_DATE`

### Vesting Windows
- **Next 30 days**: `vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'`
- **Next 60 days**: `vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'`
- **Next 90 days**: `vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'`
- **This quarter**: Based on fiscal quarter logic

---

## 4. Grant Type and Classification Rules

### Grant Type Hierarchy
- **grant_type_code**: Most granular level (e.g., 'RSU', 'ISO', 'NSO', 'RSA')
- **grant_type_description**: Human-readable description
- **grant_type_group**: Higher-level categorization of grant types

### Grouping for "List" Queries
When users ask for **"list of grants"** or **"what grants"**, they mean **grant types**, not individual grant instances:
```sql
-- CORRECT: Group by type
SELECT grant_type_code, grant_type_description, COUNT(*) as count
FROM vGrants
GROUP BY grant_type_code, grant_type_description

-- INCORRECT: Don't list individual grants
SELECT grant_id, grant_type_code
FROM vGrants
```

### Grant Aggregations
- **Count of grant types**: `COUNT(DISTINCT grant_type_code)`
- **Count of individual grants**: `COUNT(DISTINCT grant_id)`
- **Total units granted**: `SUM(units_granted_amount)`

---

## 5. Plan Rules

### Plan Identification
- **plan_hub_key**: Unique identifier for a plan instance
- **plan_name**: Name of the plan (e.g., "2024 Equity Plan")
- **plan_type**: Type/category of plan (e.g., "ESPP", "RSU Plan", "Stock Option Plan")

### Grouping for "List" Queries
When users ask for **"list of plans"** or **"what plans"**, they mean **plan categories**, not individual plan instances:
```sql
-- CORRECT: Group by name and type
SELECT plan_name, plan_type, COUNT(DISTINCT plan_hub_key) as plan_count
FROM vGrants
GROUP BY plan_name, plan_type

-- INCORRECT: Don't list individual plan_hub_keys
SELECT DISTINCT plan_hub_key, plan_name
FROM vGrants
```

### Plan Aggregations
- **Number of plan types**: `GROUP BY plan_name, plan_type`
- **Participants per plan**: `COUNT(DISTINCT participant_hub_key)`
- **Grants per plan**: `COUNT(DISTINCT grant_id)`

---

## 6. Participant Counting Rules

### Avoiding Duplicates
- **ALWAYS** use `COUNT(DISTINCT participant_hub_key)` when counting participants
- **Why**: A participant can have multiple grants, addresses, or vesting events
- **Never** use `COUNT(participant_hub_key)` without DISTINCT

---

## 7. Join and Relationship Rules

### Required Joins
- **Participant + Grant data**: 
  ```sql
  FROM vGrants g 
  JOIN vparticipant p ON p.participant_hub_key = g.participant_hub_key
  ```
- **Client + Participant data**: 
  ```sql
  FROM vparticipant p 
  JOIN vclient c ON c.client_hub_key = p.client_hub_key
  ```
- **Client + Grant data**: 
  ```sql
  FROM vGrants g 
  JOIN vclient c ON c.client_hub_key = g.client_hub_key
  ```

### Cardinality and Hierarchies

**Basic Relationships:**
- One client → Many participants
- One participant → Many grants

**Hierarchical Relationships in vGrants:**
- **One client_hub_key → Many plan_hub_key**
  - A single client can have multiple plans (e.g., "2024 Equity Plan", "ESPP 2024")
  - When filtering by client, you may get grants from multiple plans
  
- **One plan_hub_key → Many grant_id**
  - A single plan contains multiple individual grants to different participants
  - When filtering by plan, you may get grants to many participants
  
- **One grant_id → Many vesting_dt (rows)**
  - A single grant has multiple vesting tranches over time
  - Each vesting tranche is a separate row in vGrants
  - This is why DISTINCT is critical when counting grants or participants

**Example Hierarchy:**
```
Client "ABC Corp"
  ├─ Plan "2024 Equity Plan"
  │   ├─ Grant to Employee A (3 vesting dates = 3 rows)
  │   ├─ Grant to Employee B (4 vesting dates = 4 rows)
  │   └─ Grant to Employee C (2 vesting dates = 2 rows)
  └─ Plan "ESPP 2024"
      ├─ Grant to Employee A (2 vesting dates = 2 rows)
      └─ Grant to Employee D (1 vesting date = 1 row)
```

### Query Implications

**When querying by client:**
- You'll get data from ALL plans under that client
- Use `GROUP BY plan_name` if you want to see breakdown by plan

**When querying by plan:**
- You'll get data from ALL grants under that plan
- Use `GROUP BY grant_type_code` if you want to see breakdown by grant type

**When counting:**
- Always use `COUNT(DISTINCT grant_id)` to count grants (not rows)
- Always use `COUNT(DISTINCT participant_hub_key)` to count participants
- A simple `COUNT(*)` counts vesting tranches (rows), not grants

---

## 8. List Query Interpretation Rules

When users say **"give me list of X"**, interpret as follows:

| User Request | Meaning | SQL Pattern |
|-------------|---------|-------------|
| "List of plans" | Plan categories (by name + type) | `GROUP BY plan_name, plan_type` |
| "List of grants" | Grant types | `GROUP BY grant_type_code, grant_type_description` |
| "List of participants" | Individual participants | `SELECT DISTINCT participant_hub_key, first_nm, last_nm` |
| "List of countries" | Countries with participants | `GROUP BY country_cd` |
| "List of clients" | Individual clients | `SELECT DISTINCT client_hub_key, client_name` |

**Key Principle**: "List of" usually means **categories/types**, not individual instances, UNLESS referring to people or companies.

---

## 9. Common Filters Quick Reference

| Filter Type | SQL Example |
|------------|-------------|
| US participants | `WHERE country_cd = 'US'` |
| Specific state | `WHERE country_cd = 'US' AND state = 'CA'` |
| China participants | `WHERE country_cd = 'CN'` |
| Upcoming vestings | `WHERE vesting_dt > CURRENT_DATE AND is_processed = FALSE` |
| Next 60 days vesting | `WHERE vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'` |
| Unprocessed vestings | `WHERE is_processed = FALSE` |

---

## 10. Aggregation Best Practices

### Standard Aggregations
- **Participants**: `COUNT(DISTINCT participant_hub_key)`
- **Grants**: `COUNT(DISTINCT grant_id)`
- **Plans**: `COUNT(DISTINCT plan_hub_key)` OR `GROUP BY plan_name, plan_type`
- **Total Units**: `SUM(units_granted_amount)`
- **Average Unit Price**: `AVG(unit_price)`
- **Next Vesting**: `MIN(vesting_dt) WHERE vesting_dt > CURRENT_DATE`

### When to Use GROUP BY
- Summarizing by category (country, grant type, plan type)
- Counting occurrences per group
- Calculating totals or averages per group

### When to Use DISTINCT
- Selecting unique values (participants, grant IDs, plan names)
- Counting unique entities across joined tables
- Avoiding duplicate rows from one-to-many relationships
