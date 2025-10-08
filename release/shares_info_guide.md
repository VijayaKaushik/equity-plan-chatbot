# Shares Information Reference Guide
## Complete Guide to Balance Calculations in Movement-Based Schema

---

## Table of Contents
1. [Schema Overview](#schema-overview)
2. [Balance Types Explained](#balance-types-explained)
3. [Calculation Patterns](#calculation-patterns)
4. [Common Queries](#common-queries)
5. [Natural Language Mapping](#natural-language-mapping)
6. [Examples](#examples)

---

## Schema Overview

### Core Tables

#### 1. `bi_fact_movement` (Fact Table)
Records every equity movement event

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| movement_hub_key | varchar | Primary key | MVT00000000000000000026 |
| participant_hub_key | varchar | Who | PRT00000000000000000042 |
| grant_award_hub_key | varchar | Which grant | GRT00000000000000000123 |
| client_hub_key | varchar | Which company | CLNT00000000000000000002 |
| **movement_type** | varchar | Category | Cancellation, Exercise, GrantAward |
| **movement_sub_type** | varchar | Sub-category | Forfeit, Expiry, SellToCover |
| **movement_sub_sub_type** | varchar | Detail | Manual, Termination, Savings |
| **share_units** | decimal | Quantity | 1000 |
| movement_date | date | When | 2024-06-15 |

**Key**: The 3 movement columns (type, sub_type, sub_sub_type) form a composite key

---

#### 2. `bi_movement_balance_mapping` (Dimension Table)
Defines how each movement affects different balance types

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| movement_balance_mapping_key | varchar | Primary key | - |
| **movement_type** | varchar | Joins to fact | - |
| **movement_sub_type** | varchar | Joins to fact | - |
| **movement_sub_sub_type** | varchar | Joins to fact | - |
| **granted** | decimal | Coefficient | -1, 0, 1 |
| **cancelled** | decimal | Coefficient | -1, 0, 1 |
| **vested** | decimal | Coefficient | -1, 0, 1 |
| **unveiled** | decimal | Coefficient | -1, 0, 1 |
| **exercised** | decimal | Coefficient | -1, 0, 1 |
| **exercisable** | decimal | Coefficient | -1, 0, 1 |
| **forfeited** | decimal | Coefficient | -1, 0, 1 |
| **expired** | decimal | Coefficient | -1, 0, 1 |
| **outstanding** | decimal | Coefficient | -1, 0, 1 |
| (+ 10 more) | decimal | Coefficient | -1, 0, 1 |

**Key Insight**: Each row defines how ONE movement type affects ALL balance types

---

#### 3. Example Movement Type Mapping

| movement_type | movement_sub_type | movement_sub_sub_type | granted | unveiled | vested | forfeited | outstanding |
|--------------|-------------------|----------------------|---------|----------|--------|-----------|-------------|
| GrantAward | EQUITY | | 1 | 1 | 0 | 0 | 1 |
| Cancellation | Forfeit | Termination | 0 | -1 | 0 | 1 | -1 |
| Cancellation | Expiry | Manual | 0 | -1 | 0 | 0 | -1 |
| Exercise | SellToCover | | 0 | -1 | 0 | 0 | -1 |
| Release | | | 0 | -1 | 1 | 0 | 0 |

**Reading the table**:
- GrantAward adds to: granted (+1), unveiled (+1), outstanding (+1)
- Forfeit due to termination: removes from unveiled (-1), adds to forfeited (+1), removes from outstanding (-1)
- Release: moves from unveiled (-1) to vested (+1), no change to outstanding

---

## Balance Types Explained

### Primary Balance Types

#### 1. **Granted**
**What it means**: Shares that have been awarded to the participant  
**When it changes**: On grant date  
**User asks**: "How many shares has John been granted?"  
**Calculation**: `SUM(share_units * granted)`

#### 2. **Unveiled**
**What it means**: Shares awarded but not yet vested  
**When it changes**: Grant date (+), vesting date (-), forfeit (-)  
**User asks**: "How many shares are still unveiled for Sarah?"  
**Calculation**: `SUM(share_units * unveiled)`

#### 3. **Vested**
**What it means**: Shares that have completed vesting requirements  
**When it changes**: Vesting date (+)  
**User asks**: "How many shares have vested for the engineering team?"  
**Calculation**: `SUM(share_units * vested)`

#### 4. **Exercisable**
**What it means**: Options that can be exercised now  
**When it changes**: Vesting date (+), exercise (-)  
**User asks**: "How many options can I exercise today?"  
**Calculation**: `SUM(share_units * exercisable)`  
**Note**: Only applies to stock options (ISO/NSO), not RSUs

#### 5. **Exercised**
**What it means**: Options that have been exercised  
**When it changes**: Exercise date (+)  
**User asks**: "How many options has John exercised?"  
**Calculation**: `SUM(share_units * exercised)`

#### 6. **Forfeited**
**What it means**: Shares lost due to termination, expiry, etc.  
**When it changes**: Termination date, expiry date  
**User asks**: "How many shares were forfeited last quarter?"  
**Calculation**: `SUM(share_units * forfeited)`

#### 7. **Outstanding**
**What it means**: Shares currently outstanding (for dilution calcs)  
**When it changes**: Grant (+), exercise (-), forfeit (-)  
**User asks**: "What's the total outstanding equity?"  
**Calculation**: `SUM(share_units * outstanding)`

---

## Calculation Patterns

### Basic Pattern
```sql
-- Single balance type
SELECT SUM(fm.share_units * mbm.[balance_type]) as [balance_name]
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
WHERE fm.client_hub_key = :client_hub_key
```

### Multiple Balance Types
```sql
-- Unveiled + Vested = Total Equity
SELECT 
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares,
    SUM(fm.share_units * mbm.vested) as vested_shares,
    SUM(fm.share_units * (mbm.unveiled + mbm.vested)) as total_equity
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
```

### By Participant
```sql
-- Unveiled shares per participant
SELECT 
    pd.participant_hub_key,
    pd.participant_name,
    pd.email,
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.participant_hub_key, pd.participant_name, pd.email
ORDER BY unveiled_shares DESC
```

---

## Common Queries

### 1. Total Unveiled Shares (Company-Wide)

**User Query**: "How many total unveiled shares do we have?"

**SQL**:
```sql
SELECT SUM(fm.share_units * mbm.unveiled) as total_unveiled
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
```

---

### 2. Participant's Equity Summary

**User Query**: "Show me John Smith's equity breakdown"

**SQL**:
```sql
SELECT 
    pd.participant_name,
    SUM(fm.share_units * mbm.granted) as granted_shares,
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares,
    SUM(fm.share_units * mbm.vested) as vested_shares,
    SUM(fm.share_units * mbm.forfeited) as forfeited_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE pd.participant_name = 'John Smith'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.participant_name
```

---

### 3. Retirement Acceleration Eligibility

**User Query**: "Who is eligible for retirement acceleration?"

**SQL**:
```sql
WITH participant_movements AS (
    SELECT 
        fm.participant_hub_key,
        fm.movement_type,
        fm.movement_sub_type,
        fm.movement_sub_sub_type,
        MIN(gal.retirement_eligibility_dt) AS retirement_eligibility_dt,
        SUM(fm.share_units) AS share_units
    FROM bi_fact_movement fm
    INNER JOIN bi_grant_award_latest gal 
        ON gal.grant_award_hub_key = fm.grant_award_hub_key
        AND gal.retirement_eligibility_dt IS NOT NULL
    WHERE fm.client_hub_key = 'CLNT00000000000000000002'
    GROUP BY 
        fm.participant_hub_key,
        fm.movement_type,
        fm.movement_sub_type,
        fm.movement_sub_sub_type
),
unveiled_participant AS (
    SELECT 
        pm.participant_hub_key,
        pm.retirement_eligibility_dt,
        SUM(pm.share_units * mbm.unveiled) AS unveiled_shares
    FROM participant_movements pm
    INNER JOIN bi_movement_balance_mapping mbm 
        ON pm.movement_type = mbm.movement_type
        AND pm.movement_sub_type = mbm.movement_sub_type
        AND pm.movement_sub_sub_type = mbm.movement_sub_sub_type
    GROUP BY 
        pm.participant_hub_key, 
        pm.retirement_eligibility_dt
)
SELECT 
    pd.participant_name,
    pd.email,
    up.retirement_eligibility_dt,
    up.unveiled_shares
FROM unveiled_participant up
INNER JOIN bi_participant_detail pd
    ON pd.participant_hub_key = up.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE up.unveiled_shares > 0
ORDER BY up.unveiled_shares DESC
```

---

### 4. Shares Vesting in Next 30 Days

**User Query**: "What shares are vesting in the next 30 days?"

**Note**: This requires a vesting schedule table or movement_date filter

**SQL** (if movements have future dates):
```sql
SELECT 
    pd.participant_name,
    fm.movement_date as vest_date,
    SUM(fm.share_units * mbm.vested) as vesting_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
    AND fm.movement_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND fm.movement_type = 'Release'
GROUP BY pd.participant_name, fm.movement_date
ORDER BY fm.movement_date
```

---

### 5. Department-Level Summary

**User Query**: "Show me unveiled shares by department"

**SQL**:
```sql
SELECT 
    pd.department,
    COUNT(DISTINCT pd.participant_hub_key) as participant_count,
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares,
    SUM(fm.share_units * mbm.vested) as vested_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.department
ORDER BY unveiled_shares DESC
```

---

## Natural Language Mapping

### User Query â†' Balance Type

| User Says | Balance Type | SQL Column |
|-----------|--------------|------------|
| "unveiled shares" | unveiled | `mbm.unveiled` |
| "shares that haven't vested" | unveiled | `mbm.unveiled` |
| "future equity" | unveiled | `mbm.unveiled` |
| "pending shares" | unveiled | `mbm.unveiled` |
| "vested shares" | vested | `mbm.vested` |
| "earned equity" | vested | `mbm.vested` |
| "shares I can sell" | vested | `mbm.vested` |
| "granted shares" | granted | `mbm.granted` |
| "total award" | granted | `mbm.granted` |
| "exercisable options" | exercisable | `mbm.exercisable` |
| "options I can exercise" | exercisable | `mbm.exercisable` |
| "forfeited shares" | forfeited | `mbm.forfeited` |
| "lost equity" | forfeited | `mbm.forfeited` |
| "outstanding shares" | outstanding | `mbm.outstanding` |
| "dilution" | outstanding | `mbm.outstanding` |

---

## Examples

### Example 1: Simple Participant Query

**User**: "How many unveiled shares does John Smith have?"

**Step-by-Step**:
1. Identify participant: John Smith
2. Identify balance type: "unveiled" â†' `mbm.unveiled`
3. Build query:

```sql
SELECT SUM(fm.share_units * mbm.unveiled) as unveiled_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE pd.participant_name = 'John Smith'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
```

**Result**: `unveiled_shares: 5000`

---

### Example 2: Multi-Balance Query

**User**: "Show me John's unveiled and vested shares"

**Step-by-Step**:
1. Identify participant: John Smith
2. Identify balance types: unveiled, vested
3. Build query with multiple SUMs:

```sql
SELECT 
    pd.participant_name,
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares,
    SUM(fm.share_units * mbm.vested) as vested_shares,
    SUM(fm.share_units * (mbm.unveiled + mbm.vested)) as total_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE pd.participant_name = 'John Smith'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.participant_name
```

**Result**:
```
participant_name | unveiled_shares | vested_shares | total_shares
John Smith       | 5000           | 3000          | 8000
```

---

### Example 3: Aggregation Query

**User**: "How many total unveiled shares across all participants?"

**Step-by-Step**:
1. No participant filter (company-wide)
2. Balance type: unveiled
3. Single aggregate result:

```sql
SELECT SUM(fm.share_units * mbm.unveiled) as total_unveiled
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
```

**Result**: `total_unveiled: 1,250,000`

---

## Movement Type Examples

### Example Movement Records

| movement_hub_key | participant | movement_type | movement_sub_type | movement_sub_sub_type | share_units | date |
|-----------------|-------------|---------------|-------------------|-----------------------|-------------|------|
| MVT001 | John Smith | GrantAward | EQUITY | | 4000 | 2024-01-15 |
| MVT002 | John Smith | Release | | | 1000 | 2024-07-15 |
| MVT003 | John Smith | Cancellation | Forfeit | Termination | 500 | 2024-09-01 |

### Mapping Table (Simplified)

| movement_type | movement_sub_type | granted | unveiled | vested | forfeited |
|--------------|-------------------|---------|----------|--------|-----------|
| GrantAward | EQUITY | 1 | 1 | 0 | 0 |
| Release | | 0 | -1 | 1 | 0 |
| Cancellation | Forfeit | 0 | -1 | 0 | 1 |

### Calculations

**Granted Shares**:
```
MVT001: 4000 * 1 = 4000
MVT002: 1000 * 0 = 0
MVT003: 500 * 0 = 0
Total: 4000
```

**Unveiled Shares**:
```
MVT001: 4000 * 1 = 4000
MVT002: 1000 * -1 = -1000
MVT003: 500 * -1 = -500
Total: 2500
```

**Vested Shares**:
```
MVT001: 4000 * 0 = 0
MVT002: 1000 * 1 = 1000
MVT003: 500 * 0 = 0
Total: 1000
```

**Forfeited Shares**:
```
MVT001: 4000 * 0 = 0
MVT002: 1000 * 0 = 0
MVT003: 500 * 1 = 500
Total: 500
```

**Summary**:
- John was granted **4000 shares**
- Currently has **2500 unveiled** (4000 - 1000 vested - 500 forfeited)
- Currently has **1000 vested**
- Lost **500 forfeited**

---

## Key Takeaways

1. **All calculations use the pattern**: `SUM(share_units * balance_type_coefficient)`

2. **The mapping table acts as a decoder** - it tells you how each movement affects each balance type

3. **Negative coefficients reduce balances** - e.g., Release moves shares from unveiled (-1) to vested (+1)

4. **Always join on 3 columns**: movement_type, movement_sub_type, movement_sub_sub_type

5. **Use is_latest = 'b1'** when joining to bi_participant_detail (gets current record)

6. **Filter by client_hub_key** for security (row-level access control)

---

## Using the MovementCalculator

```python
from builders.real_movement_calculator import RealMovementCalculator, MovementFilter

# Initialize
calc = RealMovementCalculator(config_path='config')

# Example 1: Unveiled shares for John
filters = MovementFilter(
    participant_hub_key='PRT00000000000000000042',
    client_hub_key='CLNT00000000000000000002'
)
sql = calc.build_unvested_shares_sql(filters)

# Example 2: Multiple balances
sql = calc.build_multi_balance_sql(
    balance_types_list=['unveiled', 'vested', 'granted'],
    filters=filters,
    group_by_participant=True
)

# Example 3: Retirement acceleration
sql = calc.build_retirement_acceleration_sql(filters)
```

---

## Glossary

**Balance Type**: A specific category of share measurement (unveiled, vested, etc.)

**Coefficient**: The multiplier in the mapping table (-1, 0, or 1) that determines how a movement affects a balance

**Composite Key**: The 3-column join (movement_type, movement_sub_type, movement_sub_sub_type)

**Hub Key**: Primary key format in data vault (e.g., PRT00000000000000000042)

**is_latest**: Flag in SCD Type 2 table indicating current record ('b1' = current, 'b0' = historical)

**Movement**: Any equity event (grant, vest, exercise, forfeit, etc.)

**Share Units**: The quantity in bi_fact_movement that gets multiplied by coefficients
