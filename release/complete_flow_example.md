# Complete Flow: User Query → SQL Execution
## Step-by-Step Example with Movement Schema

---

## Query Example
**User asks**: *"How many unveiled shares does John Smith have?"*

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER QUERY                                                  │
│ "How many unveiled shares does John Smith have?"           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 0+1: Query Processing & Understanding                  │
├─────────────────────────────────────────────────────────────┤
│ • Corrects typos                                            │
│ • Resolves context from chat history                        │
│ • Classifies: AGGREGATE query                               │
│ • Intent: aggregate                                         │
│ • Complexity: simple                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Output:
                         │   {
                         │     "processed_query": "How many unveiled shares does John Smith have?",
                         │     "query_category": "AGGREGATE",
                         │     "intent": "aggregate"
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Query Type Classification                          │
├─────────────────────────────────────────────────────────────┤
│ • Determines query template type                            │
│ • "John Smith" + "shares" → PARTICIPANT_LEVEL              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Output:
                         │   {
                         │     "query_type": "PARTICIPANT_LEVEL"
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Entity Extraction                                  │
├─────────────────────────────────────────────────────────────┤
│ • Extracts entities from query                              │
│ • Participant: "John Smith"                                 │
│ • Balance type: "unveiled"                                  │
│ • Metric: "shares"                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Output:
                         │   {
                         │     "entities": {
                         │       "participant_names": ["John Smith"],
                         │       "balance_keywords": ["unveiled"],
                         │       "metrics": ["shares"]
                         │     }
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Entity Normalization                               │
├─────────────────────────────────────────────────────────────┤
│ • Looks up "John Smith" in database                         │
│ • Finds: participant_hub_key = PRT00000000000000000042      │
│ • Applies user security filters                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Output:
                         │   {
                         │     "normalized_entities": {
                         │       "participant_hub_key": "PRT00000000000000000042",
                         │       "participant_name": "John Smith"
                         │     }
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Template Parameter Extraction                      │
├─────────────────────────────────────────────────────────────┤
│ • "unveiled" → balance type: 'unveiled'                     │
│ • "how many" → aggregation_only: true                       │
│ • Determines metrics needed                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Output:
                         │   {
                         │     "template_parameters": {
                         │       "aggregation_only": true,
                         │       "metrics": ["unveiled_shares"],
                         │       "filters": {
                         │         "participant_hub_key": "PRT00000000000000000042"
                         │       }
                         │     }
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Template Population ★ NEW INTEGRATION ★            │
├─────────────────────────────────────────────────────────────┤
│ 1. Detects schema type: 'movement'                          │
│ 2. Creates MovementFilter:                                  │
│    • participant_hub_key = PRT00000000000000000042          │
│    • client_hub_key = CLNT00000000000000000002              │
│ 3. Routes to: build_unvested_shares_sql()                   │
│ 4. Generates SQL                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Generated SQL:
                         │   
                         │   SELECT SUM(fm.share_units * mbm.unveiled) as unveiled_shares
                         │   FROM bi_fact_movement fm
                         │   INNER JOIN bi_movement_balance_mapping mbm
                         │       ON fm.movement_type = mbm.movement_type
                         │       AND fm.movement_sub_type = mbm.movement_sub_type
                         │       AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
                         │   INNER JOIN bi_participant_detail pd
                         │       ON fm.participant_hub_key = pd.participant_hub_key
                         │       AND pd.is_latest = 'b1'
                         │   WHERE pd.participant_hub_key = 'PRT00000000000000000042'
                         │       AND fm.client_hub_key = 'CLNT00000000000000000002'
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Security Validation                                │
├─────────────────────────────────────────────────────────────┤
│ • Verifies client_hub_key filter present                    │
│ • Checks user has access to CLNT00000000000000000002        │
│ • Logs audit trail                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Validation Result:
                         │   {
                         │     "validated": true,
                         │     "audit_id": "audit_20251007_123456"
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: Query Execution                                    │
├─────────────────────────────────────────────────────────────┤
│ • Executes SQL against database                             │
│ • Returns result: 5000 shares                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► Execution Result:
                         │   {
                         │     "success": true,
                         │     "results": [{"unveiled_shares": 5000}],
                         │     "execution_time_ms": 284
                         │   }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: Response Formatting                                │
├─────────────────────────────────────────────────────────────┤
│ • Formats result into natural language                      │
│ • Adds context and suggestions                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ FINAL RESPONSE TO USER                                      │
├─────────────────────────────────────────────────────────────┤
│ John Smith has **5,000 unveiled shares**.                  │
│                                                             │
│ These shares have been granted but have not yet vested.     │
│                                                             │
│ Would you like to:                                          │
│ • See when these shares will vest?                          │
│ • View John's vested shares?                                │
│ • Check John's total equity holdings?                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Flow in Step 6

### 1. Detection Phase

```python
# Step 6 initialization
step6 = TemplatePopulationStep(config_path='config')

# Auto-detects schema type
schema_type = step6._detect_schema_type()
# Returns: 'movement'

# Initializes RealMovementCalculator
step6.movement_calc = RealMovementCalculator(config_path)
```

### 2. Execution Phase

```python
# Called by orchestrator
result = await step6.execute(
    query_type='PARTICIPANT_LEVEL',
    parameters={
        'aggregation_only': True,
        'metrics': ['unveiled_shares']
    },
    normalized_entities={
        'participant_hub_key': 'PRT00000000000000000042'
    },
    user_context={
        'client_hub_key': 'CLNT00000000000000000002'
    }
)
```

### 3. Filter Building

```python
# Convert normalized entities to MovementFilter
filters = MovementFilter(
    participant_hub_key='PRT00000000000000000042',
    client_hub_key='CLNT00000000000000000002'
)
```

### 4. Method Routing

```python
# Step 6 routes based on metrics
if metrics == ['unveiled_shares']:
    sql = step6.movement_calc.build_unvested_shares_sql(filters)
```

### 5. SQL Generation

```python
# RealMovementCalculator builds SQL
def build_unvested_shares_sql(filters):
    calc_expr = "SUM(fm.share_units * mbm.unveiled)"
    
    sql = f"""
    SELECT {calc_expr} as unveiled_shares
    FROM bi_fact_movement fm
    INNER JOIN bi_movement_balance_mapping mbm
        ON fm.movement_type = mbm.movement_type
        AND fm.movement_sub_type = mbm.movement_sub_type
        AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
    WHERE fm.participant_hub_key = '{filters.participant_hub_key}'
        AND fm.client_hub_key = '{filters.client_hub_key}'
    """
    
    return sql
```

---

## Example 2: Multiple Balance Types

**User asks**: *"Show me John's unveiled and vested shares"*

### Key Differences from Example 1

| Step | Example 1 (Aggregate) | Example 2 (Multiple Balances) |
|------|----------------------|-------------------------------|
| **Step 1** | AGGREGATE category | DETAIL category |
| **Step 5** | `metrics: ['unveiled_shares']`<br>`aggregation_only: true` | `metrics: ['unveiled_shares', 'vested_shares']`<br>`aggregation_only: false` |
| **Step 6 Method** | `build_unvested_shares_sql()` | `build_multi_balance_sql()` |
| **SQL Output** | Single SUM | Multiple SUMs with columns |

### Generated SQL (Example 2)

```sql
SELECT 
    pd.participant_hub_key,
    pd.participant_name,
    pd.email,
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
WHERE pd.participant_hub_key = 'PRT00000000000000000042'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.participant_hub_key, pd.participant_name, pd.email
```

### Response to User

```
John Smith's equity breakdown:

Balance Type      | Shares
------------------|--------
Unveiled          | 5,000
Vested            | 3,000
Total             | 8,000

Would you like to:
• See when the unveiled shares will vest?
• View exercisable options?
• Check forfeited shares?
```

---

## Example 3: Retirement Acceleration

**User asks**: *"Who is eligible for retirement acceleration?"*

### Flow Differences

| Step | Action |
|------|--------|
| **Step 3** | Extracts: `query_keywords: ['retirement']` |
| **Step 5** | Sets: `has_retirement_eligibility: true` |
| **Step 6** | Detects special pattern via `_is_retirement_query()` |
| **Step 6** | Routes to: `build_retirement_acceleration_sql()` |

### Generated SQL (Example 3)

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
    up.participant_hub_key,
    up.retirement_eligibility_dt,
    up.unveiled_shares,
    pd.participant_name,
    pd.email
FROM unveiled_participant up
INNER JOIN bi_participant_detail pd
    ON pd.participant_hub_key = up.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE up.unveiled_shares > 0
ORDER BY up.unveiled_shares DESC
```

---

## Decision Tree in Step 6

```
┌─────────────────────────────────────────┐
│ Step 6: Template Population             │
└───────────────┬─────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Schema Type?  │
        └───────┬───────┘
                │
        ┌───────┴───────┐
        ▼               ▼
    Movement        Traditional
        │               │
        ▼               │
┌───────────────┐       │
│ Special Query?│       │
└───┬───────────┘       │
    │                   │
    ├─ YES: Retirement? ────► build_retirement_acceleration_sql()
    │
    └─ NO
        │
        ▼
┌───────────────┐
│ Single Metric?│
└───┬───────────┘
    │
    ├─ YES
    │   │
    │   ├─ unveiled_shares ────► build_unvested_shares_sql()
    │   ├─ vested_shares ────► build_vested_shares_sql()
    │   └─ other ────► build_participant_balance_sql()
    │
    └─ NO (Multiple)
        │
        ▼
┌───────────────────┐
│ Aggregation Only? │
└───┬───────────────┘
    │
    ├─ YES ────► build_multi_balance_sql(group_by=False)
    │
    └─ NO ────► build_multi_balance_sql(group_by=True)
```

---

## Testing Step 6 Integration

### Test Case 1: Simple Aggregate

```python
# Test unveiled shares for participant
params = {
    'aggregation_only': True,
    'metrics': ['unveiled_shares']
}
entities = {
    'participant_hub_key': 'PRT00000000000000000042'
}
user_ctx = {
    'client_hub_key': 'CLNT00000000000000000002'
}

result = await step6.execute('PARTICIPANT_LEVEL', params, entities, user_ctx)

assert 'SUM(fm.share_units * mbm.unveiled)' in result.sql
assert 'PRT00000000000000000042' in result.sql
```

### Test Case 2: Multiple Balances

```python
params = {
    'aggregation_only': False,
    'metrics': ['unveiled_shares', 'vested_shares']
}

result = await step6.execute('PARTICIPANT_LEVEL', params, entities, user_ctx)

assert 'mbm.unveiled' in result.sql
assert 'mbm.vested' in result.sql
assert 'GROUP BY' in result.sql
```

### Test Case 3: Retirement Query

```python
params = {
    'metrics': ['unveiled_shares'],
    'query_keywords': ['retirement_acceleration']
}
entities = {}

result = await step6.execute('PARTICIPANT_LEVEL', params, entities, user_ctx)

assert 'WITH participant_movements AS' in result.sql
assert 'retirement_eligibility_dt' in result.sql
```

---

## Summary

### What Changed in Step 6

1. ✅ **Auto-detection** of schema type (movement vs traditional)
2. ✅ **Router logic** to select appropriate calculator method
3. ✅ **MovementFilter** building from normalized entities
4. ✅ **Special pattern detection** (retirement, etc.)
5. ✅ **Multi-metric support** with proper grouping

### Integration Points

- **Step 5** provides metrics → Step 6 maps to balance types
- **Step 4** provides participant IDs → Step 6 builds filters
- **User context** provides security → Step 6 adds client filters
- **Step 7** receives SQL → validates security constraints

### Key Benefits

- ✅ **No hardcoded SQL** - all built dynamically
- ✅ **Schema agnostic** - works with movement or traditional
- ✅ **Extensible** - easy to add new query patterns
- ✅ **Testable** - clear inputs/outputs at each stage
- ✅ **Maintainable** - SQL logic in config files, not code
