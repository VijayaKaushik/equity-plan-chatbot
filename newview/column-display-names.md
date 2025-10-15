# Column Display Names - Business-Friendly Aliases

This document maps technical database field names to business-friendly display names for query results.

---

## vclient - Client View

| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| client_hub_key | Client ID | `AS "Client ID"` |
| client_id | Client Code | `AS "Client Code"` |
| client_name | Client Name | `AS "Client Name"` |

---

## vparticipant - Participant View

### Identification Fields
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| participant_hub_key | Participant ID | `AS "Participant ID"` |
| client_hub_key | Client ID | `AS "Client ID"` |
| first_nm | First Name | `AS "First Name"` |
| last_nm | Last Name | `AS "Last Name"` |

### Account Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| account_open_completion_dt | Account Opening Date | `AS "Account Opening Date"` |
| account_open_completion_status | Account Status | `AS "Account Status"` |

### Geographic Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| city | City | `AS "City"` |
| country_cd | Country | `AS "Country"` |
| state | State | `AS "State"` |

### Verification Status
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| kyc_status | KYC Status | `AS "KYC Status"` |
| id_verification_status | ID Verification Status | `AS "ID Verification Status"` |

### Employment Roles
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| is_director | Is Director | `AS "Is Director"` |
| is_officer | Is Officer | `AS "Is Officer"` |
| is_blackout_insider | Is Blackout Insider | `AS "Is Blackout Insider"` |

---

## vGrants - Grants View

### Grant Identification
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| grant_id | Grant ID | `AS "Grant ID"` |
| grant_award_hub_key | Grant Award ID | `AS "Grant Award ID"` |
| participant_hub_key | Participant ID | `AS "Participant ID"` |
| client_hub_key | Client ID | `AS "Client ID"` |
| plan_hub_key | Plan ID | `AS "Plan ID"` |

### Grant Type Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| grant_type_code | Grant Type Code | `AS "Grant Type Code"` |
| grant_type_description | Grant Type | `AS "Grant Type"` |
| grant_type_group | Grant Category | `AS "Grant Category"` |
| description | Grant Description | `AS "Grant Description"` |

### Acceptance Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| acceptance_cd | Acceptance Code | `AS "Acceptance Code"` |
| acceptance_date | Acceptance Date | `AS "Acceptance Date"` |
| acceptance_status | Acceptance Status | `AS "Acceptance Status"` |

### Date Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| expected_expiration_date | Expected Expiration Date | `AS "Expected Expiration Date"` |
| actual_expiration_date | Actual Expiration Date | `AS "Actual Expiration Date"` |
| vesting_dt | Vesting Date | `AS "Vesting Date"` |

### Financial Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| units_granted_amount | Units Granted | `AS "Units Granted"` |
| unit_price | Unit Price | `AS "Unit Price"` |
| market_price_at_award | Market Price at Award | `AS "Market Price at Award"` |
| fair_value_price | Fair Value Price | `AS "Fair Value Price"` |

### Plan Information
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| plan_name | Plan Name | `AS "Plan Name"` |
| plan_type | Plan Type | `AS "Plan Type"` |
| plan_start_date | Plan Start Date | `AS "Plan Start Date"` |
| plan_duration | Plan Duration | `AS "Plan Duration"` |

### Processing Status
| Technical Field Name | Display Name | Example Alias |
|---------------------|--------------|---------------|
| is_processed | Is Processed | `AS "Is Processed"` |

---

## Common Aggregate Fields

### Count Aggregations
| Technical Expression | Display Name | Example Alias |
|---------------------|--------------|---------------|
| COUNT(DISTINCT participant_hub_key) | Participant Count | `AS "Participant Count"` |
| COUNT(DISTINCT grant_id) | Grant Count | `AS "Grant Count"` |
| COUNT(DISTINCT plan_hub_key) | Plan Count | `AS "Plan Count"` |
| COUNT(DISTINCT client_hub_key) | Client Count | `AS "Client Count"` |
| COUNT(*) | Total Count | `AS "Total Count"` |

### Sum Aggregations
| Technical Expression | Display Name | Example Alias |
|---------------------|--------------|---------------|
| SUM(units_granted_amount) | Total Units Granted | `AS "Total Units Granted"` |
| SUM(units_granted_amount * fair_value_price) | Total Grant Value | `AS "Total Grant Value"` |
| SUM(units_granted_amount * unit_price) | Total Unit Value | `AS "Total Unit Value"` |

### Date Aggregations
| Technical Expression | Display Name | Example Alias |
|---------------------|--------------|---------------|
| MIN(vesting_dt) | Next Vesting Date | `AS "Next Vesting Date"` |
| MAX(vesting_dt) | Last Vesting Date | `AS "Last Vesting Date"` |
| MIN(plan_start_date) | Earliest Plan Start | `AS "Earliest Plan Start"` |
| MAX(plan_start_date) | Latest Plan Start | `AS "Latest Plan Start"` |

### Other Aggregations
| Technical Expression | Display Name | Example Alias |
|---------------------|--------------|---------------|
| AVG(unit_price) | Average Unit Price | `AS "Average Unit Price"` |
| AVG(fair_value_price) | Average Fair Value | `AS "Average Fair Value"` |

---

## Usage Guidelines

### 1. Always Use Aliases in SELECT
**Good:**
```sql
SELECT 
    country_cd AS "Country",
    COUNT(DISTINCT participant_hub_key) AS "Participant Count"
FROM vparticipant
GROUP BY country_cd;
```

**Bad:**
```sql
SELECT 
    country_cd,
    COUNT(DISTINCT participant_hub_key)
FROM vparticipant
GROUP BY country_cd;
```

### 2. Use Double Quotes for Multi-Word Aliases
```sql
-- Correct
SELECT first_nm AS "First Name"

-- Incorrect
SELECT first_nm AS First Name  -- Will cause error
SELECT first_nm AS 'First Name'  -- Single quotes are for strings, not aliases
```

### 3. Keep Technical Names in GROUP BY and ORDER BY
```sql
-- Correct
SELECT 
    country_cd AS "Country",
    COUNT(DISTINCT participant_hub_key) AS "Participant Count"
FROM vparticipant
GROUP BY country_cd  -- Use technical name
ORDER BY COUNT(DISTINCT participant_hub_key) DESC;  -- Or use technical expression

-- Also Correct (using alias in ORDER BY)
SELECT 
    country_cd AS "Country",
    COUNT(DISTINCT participant_hub_key) AS "Participant Count"
FROM vparticipant
GROUP BY country_cd
ORDER BY "Participant Count" DESC;  -- Can reference alias in ORDER BY
```

### 4. Consistent Naming Convention
- Use Title Case for all display names
- Be descriptive but concise
- Avoid abbreviations in display names (except common ones like ID, KYC)
- Use "Is" prefix for boolean fields

---

## Special Cases

### Calculated Fields
| Calculation | Display Name | Example |
|------------|--------------|---------|
| Current date check | Status | `CASE WHEN vesting_dt > CURRENT_DATE THEN 'Future' ELSE 'Past' END AS "Status"` |
| Full name | Full Name | `first_nm || ' ' || last_nm AS "Full Name"` |
| Acceptance rate | Acceptance Rate | `ROUND(100.0 * accepted / total, 2) AS "Acceptance Rate %"` |
| Grant value | Grant Value | `units_granted_amount * fair_value_price AS "Grant Value"` |

### Conditional Display
```sql
-- Show user-friendly status
CASE 
    WHEN vesting_dt <= CURRENT_DATE THEN 'Past'
    WHEN vesting_dt <= CURRENT_DATE + INTERVAL '30 days' THEN 'Next 30 Days'
    WHEN vesting_dt <= CURRENT_DATE + INTERVAL '90 days' THEN 'Next 90 Days'
    ELSE 'Future'
END AS "Vesting Window"
```

---

## Quick Reference: Common Query Patterns

### Country Summary
```sql
SELECT 
    country_cd AS "Country",
    COUNT(DISTINCT participant_hub_key) AS "Participant Count"
FROM vparticipant
GROUP BY country_cd
ORDER BY "Participant Count" DESC;
```

### Grant Type Summary
```sql
SELECT 
    grant_type_code AS "Grant Type Code",
    grant_type_description AS "Grant Type",
    COUNT(DISTINCT grant_id) AS "Grant Count",
    COUNT(DISTINCT participant_hub_key) AS "Participant Count",
    SUM(units_granted_amount) AS "Total Units Granted"
FROM vGrants
GROUP BY grant_type_code, grant_type_description
ORDER BY "Grant Count" DESC;
```

### Next Vesting Events
```sql
SELECT 
    plan_name AS "Plan Name",
    grant_type_description AS "Grant Type",
    vesting_dt AS "Vesting Date",
    units_granted_amount AS "Units Vesting"
FROM vGrants
WHERE vesting_dt > CURRENT_DATE
    AND is_processed = FALSE
ORDER BY "Vesting Date" ASC;
```

---

## Implementation in SQL Generation

When generating SQL queries:
1. **Always include AS aliases** for all fields in SELECT clause
2. **Use the Display Name** from this mapping document
3. **Wrap multi-word aliases in double quotes**
4. **Keep technical names** in WHERE, GROUP BY, and JOIN clauses
5. **Can use aliases** in ORDER BY clause (optional)
