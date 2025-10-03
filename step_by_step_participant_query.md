# Complete Walkthrough: Steps 1-5
## Query: "For participant jhon give me total shares that will be released in next one month for rsu grants"

---

## YAML Configuration Files

### File: `config/business_vocabulary.yaml`

```yaml
plan_types:
  - name: RSU
    full_name: Restricted Stock Units
    synonyms: [restricted stock, rsus, rsu grants]
  - name: ISO
    full_name: Incentive Stock Options
    synonyms: [incentive options, isos]
  - name: NSO
    full_name: Non-Qualified Stock Options
    synonyms: [non-qualified options, nqso, stock options]

equity_terms:
  - term: vesting
    synonyms: [vest, vested, vesting schedule]
    definition: Process of earning equity over time
  - term: release
    synonyms: [released, release dates, vest dates]
    definition: Date when equity becomes available
  - term: shares
    synonyms: [units, equity, stock]
    definition: Quantity of equity granted

participant_synonyms: [employee, recipient, person, individual]
grant_synonyms: [award, equity, allocation]
```

### File: `config/entity_schema.yaml`

```yaml
entity_types:
  participants:
    description: Employees receiving equity compensation
    attributes: [name, email, employee_id, department, country, status]
    can_filter_by: [name, department, country, status]
    belongs_to: clients
    
  grants:
    description: Individual equity awards to participants
    attributes: [grant_date, quantity, status, plan_type]
    can_filter_by: [grant_date, status, plan_type]
    belongs_to: [participants, plans]
    
  vesting_schedules:
    description: Specific dates when equity vests/releases
    attributes: [vest_date, vest_quantity, vested_status]
    can_filter_by: [vest_date, vested_status]
    belongs_to: tranches

relationships:
  - participants have many grants
  - grants have many tranches
  - tranches have many vesting_schedules
```

### File: `config/normalization_rules.yaml`

```yaml
status_mappings:
  vesting_status:
    mappings:
      pending: pending
      unvested: pending
      not vested: pending
      will be released: pending
      upcoming: pending
      future: pending

plan_type_mappings:
  mappings:
    RSU: RSU
    rsu: RSU
    rsus: RSU
    rsu grants: RSU
    restricted stock: RSU

date_expression_patterns:
  relative:
    - pattern: "next one month"
      type: future_months
      value: 1
    - pattern: "next (\\d+) month[s]?"
      type: future_months
    - pattern: "next (\\d+) day[s]?"
      type: future_days

implicit_filters:
  default_participant_status: active
  default_vesting_status: pending
```

### File: `config/metrics_schema.yaml`

```yaml
vesting_schedule_metrics:
  total_shares:
    sql: "SUM(vs.vest_quantity)"
    description: "Total shares vesting"
    requires_tables: [vesting_schedules]
  
  vest_quantity:
    sql: "vs.vest_quantity"
    description: "Quantity vesting on specific date"
    requires_tables: [vesting_schedules]

vesting_schedule_computed_fields:
  days_until_vest:
    sql: "DATE_PART('day', vs.vest_date - CURRENT_DATE)::int"
```

---

## Step 1: Query Understanding

### Input

```json
{
  "user_query": "For participant jhon give me total shares that will be released in next one month for rsu grants",
  "user_id": "user_123"
}
```

### Prompt: `prompts/understanding_prompt.txt`

```txt
You are an expert at understanding natural language queries about equity compensation plans.

BUSINESS CONTEXT - Equity Compensation Terminology:
{vocabulary}

Plan Types:
- RSU (Restricted Stock Units): Grants of company stock that vest over time
- ISO (Incentive Stock Options): Tax-advantaged stock options
- NSO (Non-Qualified Stock Options): Standard stock options

Key Terms:
- Vesting/Release: Process of earning equity over time
- Shares: Quantity of equity (also called "units")

Synonyms to Recognize:
- "Grants" = "Awards" = "Equity compensation"
- "Participants" = "Employees" = "Recipients"
- "Release dates" = "Vest dates" = "Vesting schedule"
- "Released" = "Vested" = "Becoming available"

USER QUERY: "{query}"

INSTRUCTIONS:

1. CORRECT TYPOS AND GRAMMAR
   - Fix any obvious spelling mistakes
   - Correct grammatical errors

2. DETERMINE QUERY CATEGORY
   AGGREGATE queries return summary numbers/statistics:
   - Keywords: "how many", "total", "count", "sum", "average"
   - Examples: "How many grants?", "Total shares?"
   
   DETAIL queries return row-by-row data:
   - Keywords: "list", "show", "who", "which", "find", "give me"
   - Examples: "List all participants", "Show vesting dates"

3. IDENTIFY INTENT
   Choose from: list, aggregate, search, calculate

4. ASSESS COMPLEXITY
   - simple: Single entity, straightforward
   - medium: Multiple entities or filters
   - complex: Multiple entities, complex filters

OUTPUT FORMAT (JSON only):
{
  "corrected_query": "corrected version",
  "intent": "aggregate|list|search|calculate",
  "query_category": "AGGREGATE|DETAIL",
  "complexity": "simple|medium|complex",
  "requires_clarification": false,
  "reasoning": "Brief explanation"
}
```

### Values Injected into Prompt

```python
vocabulary = load_yaml('config/business_vocabulary.yaml')

prompt = understanding_prompt_template.format(
    vocabulary=vocabulary,  # Plan types, synonyms
    query="For participant jhon give me total shares that will be released in next one month for rsu grants"
)
```

### LLM Output

```json
{
  "corrected_query": "For participant John give me total shares that will be released in next one month for RSU grants",
  "intent": "aggregate",
  "query_category": "AGGREGATE",
  "complexity": "medium",
  "requires_clarification": false,
  "reasoning": "Corrected 'jhon' to 'John'. Query asks for 'total shares' which is an aggregate metric. 'Released' refers to vesting. Medium complexity due to specific participant, time filter, and plan type filter."
}
```

### Explanation
- ✅ Typo corrected: "jhon" → "John"
- ✅ Used vocabulary to understand: "released" = vesting, "rsu grants" = RSU plan type
- ✅ Identified "total shares" as AGGREGATE (sum, not list)

---

## Step 2: Query Type Classification

### Input

```json
{
  "corrected_query": "For participant John give me total shares that will be released in next one month for RSU grants",
  "query_category": "AGGREGATE",
  "complexity": "medium"
}
```

### Prompt: `prompts/classification_prompt.txt`

```txt
You are an expert at classifying equity compensation queries into predefined template categories.

USER QUERY: "{query}"
QUERY CATEGORY: {query_category}
COMPLEXITY: {complexity}

AVAILABLE QUERY TYPES:
{entity_types}

1. CLIENT_LEVEL
   - Company-wide aggregations
   - Examples: "List companies with participant counts"
   - Use when: Query focuses on company/client as primary entity

2. PARTICIPANT_LEVEL
   - Individual employee equity details
   - Examples: "Show John Smith's equity", "List participants with unvested RSUs"
   - Use when: Query focuses on individual employees/participants

3. VESTING_SCHEDULE
   - Time-based vesting analysis
   - Examples: "What's vesting in next 30 days?", "Show vesting schedule"
   - Use when: Query mentions vesting dates, release dates, or time-based equity events

CLASSIFICATION RULES:

If query mentions specific participant name → PARTICIPANT_LEVEL
If query asks "when" or mentions dates/releases → Consider VESTING_SCHEDULE
If query asks for participant's equity details → PARTICIPANT_LEVEL

OUTPUT FORMAT (JSON only):
{
  "query_type": "PARTICIPANT_LEVEL|VESTING_SCHEDULE|CLIENT_LEVEL",
  "confidence": 0.95,
  "reasoning": "Explanation",
  "alternative_type": "second option or null"
}
```

### Values Injected

```python
entity_types = load_yaml('config/entity_schema.yaml')

prompt = classification_prompt_template.format(
    query="For participant John give me total shares that will be released in next one month for RSU grants",
    query_category="AGGREGATE",
    complexity="medium",
    entity_types=yaml.dump(entity_types['entity_types'])
)
```

### LLM Output

```json
{
  "query_type": "VESTING_SCHEDULE",
  "confidence": 0.95,
  "reasoning": "Query mentions 'released in next one month' which is time-based vesting. While it's for a specific participant (John), the focus is on when shares vest/release. VESTING_SCHEDULE template handles time-based queries with participant filters.",
  "alternative_type": "PARTICIPANT_LEVEL",
  "alternative_confidence": 0.70
}
```

### Explanation
- ✅ Chose VESTING_SCHEDULE because of "released in next one month" (time-based)
- ✅ Entity schema helped identify relationships: participants → grants → vesting_schedules
- ✅ High confidence due to clear time expression

---

## Step 3: Entity Extraction

### Input

```json
{
  "corrected_query": "For participant John give me total shares that will be released in next one month for RSU grants"
}
```

### Prompt: `prompts/entity_extraction_prompt.txt`

```txt
You are an expert at extracting entities from equity compensation queries.

USER QUERY: "{query}"

ENTITY TYPES TO EXTRACT:
{entity_types_list}

ENTITY TYPES:
1. participant_names: Employee names (e.g., "John Smith", "Jane Doe")
2. plan_types: Equity plan types (RSU, ISO, NSO, ESPP, PSU)
3. statuses: Status filters (active, vested, unvested, pending)
4. date_expressions: Time references (e.g., "next 30 days", "next one month")
5. metrics: What to measure (count, sum, total, shares, quantity)

SYNONYMS FROM VOCABULARY:
{vocabulary_synonyms}
- "released" = vesting/vest dates
- "shares" = units = equity = stock
- "RSU grants" = RSU plan type

OUTPUT FORMAT (JSON only):
{
  "entities": {
    "participant_names": [],
    "plan_types": [],
    "statuses": [],
    "date_expressions": [],
    "metrics": []
  },
  "implicit_filters": {
    "description of implied filters"
  },
  "reasoning": "Explanation"
}
```

### Values Injected

```python
entity_types_list = load_yaml('config/entity_schema.yaml')['entity_types']
vocabulary = load_yaml('config/business_vocabulary.yaml')

prompt = entity_extraction_prompt.format(
    query="For participant John give me total shares that will be released in next one month for RSU grants",
    entity_types_list=entity_types_list,
    vocabulary_synonyms=vocabulary
)
```

### LLM Output

```json
{
  "entities": {
    "participant_names": ["John"],
    "plan_types": ["RSU"],
    "statuses": [],
    "date_expressions": ["next one month"],
    "metrics": ["total shares"]
  },
  "implicit_filters": {
    "participant_status": "active",
    "vesting_status": "pending",
    "description": "'Released' implies pending/unvested status. 'Will be' indicates future vesting events."
  },
  "reasoning": "Extracted participant name 'John'. Plan type 'RSU' from 'rsu grants'. Time expression 'next one month'. Metric is 'total shares' (sum aggregation). Implicit: only pending vests since asking about future releases."
}
```

### Explanation
- ✅ Found participant name: "John"
- ✅ Identified plan type: "RSU" (from "rsu grants")
- ✅ Extracted time: "next one month"
- ✅ Recognized metric: "total shares"
- ✅ Inferred implicit filter: "released" = pending vesting status

---

## Step 4: Entity Normalization

### Input

```json
{
  "raw_entities": {
    "participant_names": ["John"],
    "plan_types": ["RSU"],
    "date_expressions": ["next one month"],
    "metrics": ["total shares"],
    "implicit_filters": {
      "vesting_status": "pending"
    }
  },
  "user_context": {
    "user_id": "user_123",
    "accessible_clients": [1, 5, 12]
  }
}
```

### Process (uses normalization_rules.yaml)

```python
# Load normalization rules
norm_rules = load_yaml('config/normalization_rules.yaml')

# 1. Normalize plan type
plan_type_mappings = norm_rules['plan_type_mappings']['mappings']
normalized_plan_type = plan_type_mappings['RSU']  # = 'RSU'

# 2. Normalize date expression
date_patterns = norm_rules['date_expression_patterns']['relative']
# Pattern: "next one month" → type: future_months, value: 1
today = datetime.now().date()  # 2025-09-30
start_date = today
end_date = today + timedelta(days=30)  # 2025-10-30

# 3. Normalize vesting status
status_mappings = norm_rules['status_mappings']['vesting_status']['mappings']
normalized_status = status_mappings['pending']  # = 'pending'

# 4. Look up participant ID in database
query = """
    SELECT p.id, p.name, p.email
    FROM participants p
    WHERE p.name ILIKE '%John%'
      AND p.client_id IN (1, 5, 12)
      AND p.status = 'active'
"""
# Result: id=42, name="John Smith", email="john.smith@techcorp.com"

# 5. Normalize metric
metrics = load_yaml('config/metrics_schema.yaml')
metric_info = metrics['vesting_schedule_metrics']['total_shares']
# SQL: "SUM(vs.vest_quantity)"

# 6. Apply implicit filters
implicit = norm_rules['implicit_filters']
# default_participant_status: active
# default_vesting_status: pending
```

### Output

```json
{
  "normalized_entities": {
    "participant_id": 42,
    "participant_name": "John Smith",
    "participant_email": "john.smith@techcorp.com",
    "plan_types": ["RSU"],
    "date_range": {
      "start": "2025-09-30",
      "end": "2025-10-30"
    },
    "vesting_status": "pending",
    "metrics": ["total_shares"],
    "status_filters": {
      "participant_status": "active",
      "vesting_status": "pending"
    },
    "accessible_clients": [1, 5, 12]
  },
  "normalization_log": [
    {
      "field": "participant_names",
      "from": ["John"],
      "to": 42,
      "matched": "John Smith",
      "method": "database_lookup",
      "confidence": 0.95
    },
    {
      "field": "plan_types",
      "from": ["RSU"],
      "to": ["RSU"],
      "method": "exact_match"
    },
    {
      "field": "date_expressions",
      "from": ["next one month"],
      "to": {"start": "2025-09-30", "end": "2025-10-30"},
      "method": "pattern_match"
    }
  ]
}
```

### Explanation
- ✅ "John" → participant_id=42 via database lookup
- ✅ "RSU" stays "RSU" (already normalized)
- ✅ "next one month" → ISO date range
- ✅ "pending" status applied from implicit filter
- ✅ Applied user's accessible_clients filter

---

## Step 5: Template Parameter Extraction

### Input

```json
{
  "query_type": "VESTING_SCHEDULE",
  "corrected_query": "For participant John give me total shares that will be released in next one month for RSU grants",
  "normalized_entities": {
    "participant_id": 42,
    "plan_types": ["RSU"],
    "date_range": {"start": "2025-09-30", "end": "2025-10-30"},
    "vesting_status": "pending",
    "metrics": ["total_shares"]
  }
}
```

### Prompt: `prompts/param_extraction/vesting_schedule.txt`

```txt
Extract parameters for VESTING_SCHEDULE template.

USER QUERY: "{query}"
NORMALIZED ENTITIES: {entities}

AVAILABLE METRICS FOR VESTING_SCHEDULE:
{available_metrics}

total_shares:
  sql: SUM(vs.vest_quantity)
  description: Total shares vesting
  requires_tables: [vesting_schedules]

vest_quantity:
  sql: vs.vest_quantity
  description: Individual vesting amounts
  requires_tables: [vesting_schedules]

PARAMETERS TO EXTRACT:

1. aggregation_only (boolean)
   - true: User wants ONLY summary number (just the total)
   - false: User wants to see individual vesting events

2. display_fields (list)
   - If aggregation_only=true: Not needed
   - If aggregation_only=false: ["vs.vest_date", "p.name", "vs.vest_quantity", "pl.plan_type"]

3. metrics (list)
   - What to calculate: ["total_shares"]

4. date_range (from normalized entities)
   - start_date, end_date

5. filters (object)
   - participant_id: specific ID
   - vesting_status: pending/vested/all
   - plan_type: RSU/ISO/NSO

OUTPUT FORMAT (JSON only):
{
  "aggregation_only": true,
  "display_fields": [],
  "metrics": ["total_shares"],
  "date_range": {"start": "...", "end": "..."},
  "filters": {
    "participant_id": 42,
    "vesting_status": "pending",
    "plan_type": ["RSU"]
  },
  "computed_fields": [],
  "ordering": "",
  "limit": 1,
  "reasoning": "..."
}
```

### Values Injected

```python
available_metrics = load_yaml('config/metrics_schema.yaml')['vesting_schedule_metrics']

prompt = param_extraction_prompt.format(
    query="For participant John give me total shares that will be released in next one month for RSU grants",
    entities=json.dumps(normalized_entities, indent=2),
    available_metrics=yaml.dump(available_metrics)
)
```

### LLM Output

```json
{
  "aggregation_only": true,
  "display_fields": [],
  "metrics": ["total_shares"],
  "date_range": {
    "start": "2025-09-30",
    "end": "2025-10-30"
  },
  "filters": {
    "participant_id": 42,
    "vesting_status": "pending",
    "plan_type": ["RSU"]
  },
  "computed_fields": [],
  "ordering": "",
  "limit": 1,
  "reasoning": "User asks for 'total shares' which is an aggregate sum, not individual vesting events. Therefore aggregation_only=true. Apply filters: specific participant (id=42), only pending vests ('will be released'), RSU grants only, within date range."
}
```

### Explanation
- ✅ `aggregation_only=true` because query asks for "total" (not a list)
- ✅ Metric: `total_shares` from metrics_schema.yaml
- ✅ Filters: participant_id, plan_type, vesting_status, date_range
- ✅ No display_fields needed (just returning sum)

---

## Summary: Data Flow Through Steps 1-5

```
┌─────────────────────────────────────────────────────────────┐
│ ORIGINAL QUERY                                              │
│ "For participant jhon give me total shares that will be     │
│  released in next one month for rsu grants"                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────▼─────────────────────┐
        │ STEP 1: Understanding                   │
        │ Uses: business_vocabulary.yaml          │
        │                                         │
        │ Output:                                 │
        │ - Corrected: "John" (not "jhon")       │
        │ - Category: AGGREGATE                   │
        │ - Intent: aggregate                     │
        └───────────────────┬─────────────────────┘
                            │
        ┌───────────────────▼─────────────────────┐
        │ STEP 2: Classification                  │
        │ Uses: entity_schema.yaml                │
        │                                         │
        │ Output:                                 │
        │ - Query Type: VESTING_SCHEDULE          │
        │ - Confidence: 0.95                      │
        └───────────────────┬─────────────────────┘
                            │
        ┌───────────────────▼─────────────────────┐
        │ STEP 3: Entity Extraction               │
        │ Uses: entity_schema.yaml,               │
        │       business_vocabulary.yaml          │
        │                                         │
        │ Output:                                 │
        │ - participant_names: ["John"]           │
        │ - plan_types: ["RSU"]                   │
        │ - date_expressions: ["next one month"]  │
        │ - metrics: ["total shares"]             │
        └───────────────────┬─────────────────────┘
                            │
        ┌───────────────────▼─────────────────────┐
        │ STEP 4: Normalization                   │
        │ Uses: normalization_rules.yaml          │
        │ DB Lookup: participants table           │
        │                                         │
        │ Output:                                 │
        │ - participant_id: 42                    │
        │ - plan_types: ["RSU"]                   │
        │ - date_range:                           │
        │   start: "2025-09-30"                   │
        │   end: "2025-10-30"                     │
        │ - vesting_status: "pending"             │
        └───────────────────┬─────────────────────┘
                            │
        ┌───────────────────▼─────────────────────┐
        │ STEP 5: Parameter Extraction            │
        │ Uses: metrics_schema.yaml               │
        │                                         │
        │ Output:                                 │
        │ - aggregation_only: true                │
        │ - metrics: ["total_shares"]             │
        │ - filters: {                            │
        │     participant_id: 42,                 │
        │     plan_type: ["RSU"],                 │
        │     vesting_status: "pending",          │
        │     date_range: {...}                   │
        │   }                                     │
        └───────────────────┬─────────────────────┘
                            │
                            ▼
                   Ready for Step 6
                   (SQL Generation)
```

## Key YAML → Prompt → Output Mappings

| Step | YAML File Used | Values Injected Into Prompt | Output |
|------|---------------|----------------------------|---------|
| **1** | `business_vocabulary.yaml` | Plan types, synonyms, equity terms | Corrected query, category, intent |
| **2** | `entity_schema.yaml` | Entity types, relationships | Query type (VESTING_SCHEDULE) |
| **3** | `entity_schema.yaml`<br>`business_vocabulary.yaml` | Entity types, synonyms | Raw entities extracted |
| **4** | `normalization_rules.yaml`<br>Database | Status mappings, date patterns, plan types | Normalized IDs, dates, statuses |
| **5** | `metrics_schema.yaml` | Available metrics & SQL | Template parameters ready for SQL |

## Next Step

With these parameters, Step 6 will generate:

```sql
SELECT 
    SUM(vs.vest_quantity) as total_shares
FROM vesting_schedules vs
JOIN tranches t ON vs.tranche_id = t.id
JOIN grants g ON t.grant_id = g.id
JOIN participants p ON g.participant_id = p.id
JOIN plans pl ON g.plan_id = pl.id
WHERE p.id = 42
  AND pl.plan_type = 'RSU'
  AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30'
  AND vs.vested_status = 'pending'
  AND p.status = 'active'
```

**Result: 1,250 shares** 🎯
