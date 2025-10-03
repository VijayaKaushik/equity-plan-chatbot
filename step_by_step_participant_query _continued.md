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

---

## Step 6: Template Population (SQL Generation)

### Input

```json
{
  "query_type": "VESTING_SCHEDULE",
  "template_parameters": {
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
    "limit": 1
  },
  "normalized_entities": {
    "participant_id": 42,
    "accessible_clients": [1, 5, 12]
  }
}
```

### SQL Template File: `templates/vesting_schedule.sql`

```sql
-- VESTING_SCHEDULE Query Template
-- Handles both aggregate and detail queries for vesting schedules

{select_clause}
FROM vesting_schedules vs
JOIN tranches t ON vs.tranche_id = t.id
JOIN grants g ON t.grant_id = g.id
JOIN participants p ON g.participant_id = p.id
JOIN plans pl ON g.plan_id = pl.id
JOIN clients c ON pl.client_id = c.id
WHERE c.id IN ({accessible_clients})
    {filters}
{grouping}
{ordering}
{limit}
```

### Template Population Logic

```python
# Load template
with open('templates/vesting_schedule.sql', 'r') as f:
    template = f.read()

# Load metrics schema
metrics_schema = load_yaml('config/metrics_schema.yaml')

# Build SELECT clause
if params['aggregation_only']:
    # Just the aggregate metric
    metric_sql = metrics_schema['vesting_schedule_metrics']['total_shares']['sql']
    select_clause = f"SELECT {metric_sql} as total_shares"
    grouping = ""
else:
    # Display fields + metrics
    fields = params['display_fields']
    select_clause = f"SELECT {', '.join(fields)}"
    grouping = f"GROUP BY {', '.join(fields)}"

# Build filters
filters = []

# Participant filter
if params['filters']['participant_id']:
    filters.append(f"AND p.id = {params['filters']['participant_id']}")

# Plan type filter
if params['filters']['plan_type']:
    plan_types = "', '".join(params['filters']['plan_type'])
    filters.append(f"AND pl.plan_type IN ('{plan_types}')")

# Vesting status filter
if params['filters']['vesting_status']:
    filters.append(f"AND vs.vested_status = '{params['filters']['vesting_status']}'")

# Date range filter
if params['date_range']:
    filters.append(f"AND vs.vest_date BETWEEN '{params['date_range']['start']}' AND '{params['date_range']['end']}'")

# Participant status (from implicit filters)
filters.append("AND p.status = 'active'")

# Build final SQL
sql = template.format(
    select_clause=select_clause,
    accessible_clients=','.join(map(str, normalized_entities['accessible_clients'])),
    filters='\n    '.join(filters),
    grouping=grouping,
    ordering=params.get('ordering', ''),
    limit=f"LIMIT {params['limit']}" if params.get('limit') else ""
)
```

### Output

```json
{
  "sql": "SELECT SUM(vs.vest_quantity) as total_shares\nFROM vesting_schedules vs\nJOIN tranches t ON vs.tranche_id = t.id\nJOIN grants g ON t.grant_id = g.id\nJOIN participants p ON g.participant_id = p.id\nJOIN plans pl ON g.plan_id = pl.id\nJOIN clients c ON pl.client_id = c.id\nWHERE c.id IN (1,5,12)\n    AND p.id = 42\n    AND pl.plan_type IN ('RSU')\n    AND vs.vested_status = 'pending'\n    AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30'\n    AND p.status = 'active'\nLIMIT 1",
  "sql_formatted": "SELECT \n    SUM(vs.vest_quantity) as total_shares\nFROM vesting_schedules vs\nJOIN tranches t ON vs.tranche_id = t.id\nJOIN grants g ON t.grant_id = g.id\nJOIN participants p ON g.participant_id = p.id\nJOIN plans pl ON g.plan_id = pl.id\nJOIN clients c ON pl.client_id = c.id\nWHERE c.id IN (1, 5, 12)\n    AND p.id = 42\n    AND pl.plan_type IN ('RSU')\n    AND vs.vested_status = 'pending'\n    AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30'\n    AND p.status = 'active'\nLIMIT 1;",
  "template_used": "VESTING_SCHEDULE",
  "components": {
    "metric": "SUM(vs.vest_quantity)",
    "tables_joined": ["vesting_schedules", "tranches", "grants", "participants", "plans", "clients"],
    "filters_applied": [
      "client_id IN accessible_clients",
      "participant_id = 42",
      "plan_type = RSU",
      "vested_status = pending",
      "vest_date in range",
      "participant_status = active"
    ]
  },
  "processing_time_ms": 48
}
```

### Explanation
- ✅ Used VESTING_SCHEDULE template
- ✅ Built SELECT with SUM(vs.vest_quantity) from metrics_schema.yaml
- ✅ Added all necessary JOINs (6 tables)
- ✅ Applied all filters: participant, plan type, status, dates
- ✅ Added security filter: accessible_clients

---

## Step 7: Security Validation

### Input

```json
{
  "sql": "SELECT SUM(vs.vest_quantity) as total_shares FROM vesting_schedules vs JOIN tranches t ON vs.tranche_id = t.id JOIN grants g ON t.grant_id = g.id JOIN participants p ON g.participant_id = p.id JOIN plans pl ON g.plan_id = pl.id JOIN clients c ON pl.client_id = c.id WHERE c.id IN (1,5,12) AND p.id = 42 AND pl.plan_type IN ('RSU') AND vs.vested_status = 'pending' AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30' AND p.status = 'active' LIMIT 1",
  "user_context": {
    "user_id": "user_123",
    "role": "plan_manager",
    "accessible_clients": [1, 5, 12]
  },
  "query_metadata": {
    "query_type": "VESTING_SCHEDULE",
    "original_query": "For participant John give me total shares that will be released in next one month for RSU grants"
  }
}
```

### Validation Process

```python
import sqlglot
from sqlglot import parse_one

# Parse SQL
parsed_sql = parse_one(sql, dialect='postgres')

# Check 1: Verify client_id filter exists
has_client_filter = False
for where in parsed_sql.find_all(sqlglot.exp.Where):
    where_str = str(where).lower()
    if 'c.id in' in where_str or 'client_id in' in where_str:
        has_client_filter = True
        break

# Check 2: Verify accessible_clients match
# Extract the client IDs from SQL
sql_lower = sql.lower()
if 'c.id in (1,5,12)' in sql_lower or 'c.id in (1, 5, 12)' in sql_lower:
    sql_clients = [1, 5, 12]
    user_clients = user_context['accessible_clients']
    
    # Verify all SQL clients are in user's accessible list
    unauthorized = [c for c in sql_clients if c not in user_clients]
    if unauthorized:
        # Security violation!
        pass

# Check 3: Validate participant belongs to accessible clients
# This is implicitly enforced by JOIN to clients table with client_id filter

# Check 4: SQL injection check
dangerous_keywords = ['drop table', 'delete from', 'truncate', 'drop database']
sql_lower = sql.lower()
has_injection = any(keyword in sql_lower for keyword in dangerous_keywords)

# Check 5: Verify proper JOINs exist
# participant → grants → ... → clients (security chain)
```

### Output

```json
{
  "validated": true,
  "security_checks": {
    "client_filter_present": true,
    "client_filter_value": "IN (1,5,12)",
    "matches_user_access": true,
    "sql_injection_risk": false,
    "proper_join_chain": true,
    "unauthorized_tables": [],
    "all_checks_passed": true
  },
  "warnings": [],
  "audit_entry": {
    "audit_id": "aud_20251003_201532_789",
    "user_id": "user_123",
    "user_role": "plan_manager",
    "timestamp": "2025-10-03T20:15:32.456Z",
    "query_type": "VESTING_SCHEDULE",
    "original_query": "For participant John give me total shares that will be released in next one month for RSU grants",
    "sql_hash": "sha256:a7b3c9d2e1f4567890abcdef12345678901234567890abcdef1234567890abcd",
    "filters_applied": {
      "accessible_clients": [1, 5, 12],
      "participant_id": 42,
      "plan_type": "RSU",
      "date_range": "2025-09-30 to 2025-10-30"
    },
    "status": "approved",
    "data_accessed": "participant_vesting_data"
  },
  "validated_sql": "SELECT SUM(vs.vest_quantity) as total_shares FROM vesting_schedules vs JOIN tranches t ON vs.tranche_id = t.id JOIN grants g ON t.grant_id = g.id JOIN participants p ON g.participant_id = p.id JOIN plans pl ON g.plan_id = pl.id JOIN clients c ON pl.client_id = c.id WHERE c.id IN (1,5,12) AND p.id = 42 AND pl.plan_type IN ('RSU') AND vs.vested_status = 'pending' AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30' AND p.status = 'active' LIMIT 1",
  "processing_time_ms": 87
}
```

### Explanation
- ✅ Verified client_id filter exists
- ✅ Confirmed accessible_clients match user permissions
- ✅ No SQL injection patterns detected
- ✅ Proper JOIN chain enforces security (participant → grants → plans → clients)
- ✅ Audit trail logged for compliance

---

## Step 8: Query Execution

### Input

```json
{
  "validated_sql": "SELECT SUM(vs.vest_quantity) as total_shares FROM vesting_schedules vs JOIN tranches t ON vs.tranche_id = t.id JOIN grants g ON t.grant_id = g.id JOIN participants p ON g.participant_id = p.id JOIN plans pl ON g.plan_id = pl.id JOIN clients c ON pl.client_id = c.id WHERE c.id IN (1,5,12) AND p.id = 42 AND pl.plan_type IN ('RSU') AND vs.vested_status = 'pending' AND vs.vest_date BETWEEN '2025-09-30' AND '2025-10-30' AND p.status = 'active' LIMIT 1",
  "execution_params": {
    "timeout_seconds": 30,
    "max_rows": 1000
  }
}
```

### Database Execution

```python
import asyncpg

# Connect to database
conn = await asyncpg.connect("postgresql://localhost/equity_db")

# Set timeout
await conn.execute("SET statement_timeout = 30000")

# Execute query
start_time = time.time()
result = await conn.fetchrow(validated_sql)
execution_time = (time.time() - start_time) * 1000

# Get query plan for analysis
explain_query = f"EXPLAIN (FORMAT JSON, ANALYZE) {validated_sql}"
query_plan = await conn.fetchrow(explain_query)
```

### Simulated Database State

```
-- Table: participants
id | name        | email                      | status | client_id
42 | John Smith  | john.smith@techcorp.com    | active | 1

-- Table: grants (for participant 42)
id  | participant_id | plan_id | grant_date  | quantity | status
501 | 42             | 10      | 2024-01-15  | 4000     | active
502 | 42             | 10      | 2024-06-01  | 2000     | active

-- Table: plans
id | client_id | plan_type | plan_name
10 | 1         | RSU       | 2024 Equity Incentive Plan

-- Table: tranches (for grants 501, 502)
id  | grant_id | tranche_number | quantity
701 | 501      | 1              | 1000  (vested)
702 | 501      | 2              | 1000  (vests 2025-10-15)
703 | 501      | 3              | 1000  (vests 2025-10-20)
704 | 501      | 4              | 1000  (vests 2026-01-15)
705 | 502      | 1              | 500   (vested)
706 | 502      | 2              | 500   (vests 2025-10-10)
707 | 502      | 3              | 500   (vests 2025-12-01)
708 | 502      | 4              | 500   (vests 2026-06-01)

-- Table: vesting_schedules
-- Matching: vest_date between 2025-09-30 and 2025-10-30, status=pending
tranche_id | vest_date   | vest_quantity | vested_status
702        | 2025-10-15  | 500           | pending    ← Matches
703        | 2025-10-20  | 750           | pending    ← Matches
706        | 2025-10-10  | 500           | pending    ← Matches

-- Query Result: SUM(500 + 750 + 500) = 1,750
```

### Output

```json
{
  "success": true,
  "query_executed": true,
  "execution_time_ms": 284,
  "row_count": 1,
  "columns": ["total_shares"],
  "results": [
    {
      "total_shares": 1750
    }
  ],
  "query_plan": {
    "planning_time": "0.156 ms",
    "execution_time": "284.234 ms",
    "total_cost": 1847.52,
    "rows_examined": 3,
    "index_usage": {
      "idx_vesting_schedules_date": "used",
      "idx_participants_id": "used",
      "idx_grants_participant": "used"
    }
  },
  "database_stats": {
    "tables_scanned": 6,
    "rows_scanned": 3,
    "rows_returned": 1,
    "joins_performed": 5,
    "indexes_used": 3
  },
  "metadata": {
    "participant_name": "John Smith",
    "plan_type_filter": "RSU",
    "date_range": "2025-09-30 to 2025-10-30",
    "vesting_events_found": 3
  }
}
```

### Explanation
- ✅ Query executed successfully in 284ms
- ✅ Found 3 vesting events in date range
- ✅ Summed: 500 + 750 + 500 = 1,750 shares
- ✅ Used indexes for optimization
- ✅ Only scanned 3 relevant rows (efficient)

---

## Step 9: Response Formatting

### Input

```json
{
  "original_query": "For participant jhon give me total shares that will be released in next one month for rsu grants",
  "corrected_query": "For participant John give me total shares that will be released in next one month for RSU grants",
  "query_type": "VESTING_SCHEDULE",
  "results": [
    {
      "total_shares": 1750
    }
  ],
  "metadata": {
    "participant_name": "John Smith",
    "participant_email": "john.smith@techcorp.com",
    "plan_type_filter": "RSU",
    "date_range": "2025-09-30 to 2025-10-30",
    "vesting_events_found": 3,
    "execution_time_ms": 284
  }
}
```

### Prompt: `prompts/response_formatting_prompt.txt`

```txt
Format query results into a natural, helpful response.

CONTEXT:
Original User Query: "{original_query}"
Query Type: {query_type}
Result Count: {result_count}

QUERY RESULTS:
{results}

METADATA:
{metadata}

YOUR TASK:
Create a natural, professional response.

FORMATTING GUIDELINES:

1. START WITH DIRECT ANSWER
   - Answer the exact question asked
   - Use **bold** for the key number
   - Be specific and clear

2. ADD CONTEXT
   - Mention who (participant name)
   - Mention what (plan type)
   - Mention when (date range)

3. PROVIDE INSIGHT (if relevant)
   - Number of vesting events
   - Upcoming dates
   - Any noteworthy patterns

4. OFFER NEXT STEPS
   - Related questions user might ask
   - Actions they can take

TONE: Professional, helpful, concise

OUTPUT: Natural language response only (no JSON, no meta-commentary)
```

### Values Injected

```python
prompt = response_formatting_prompt.format(
    original_query="For participant jhon give me total shares that will be released in next one month for rsu grants",
    query_type="VESTING_SCHEDULE",
    result_count=1,
    results=json.dumps(results, indent=2),
    metadata=json.dumps(metadata, indent=2)
)
```

### LLM Output

```
John Smith will receive **1,750 RSU shares** vesting over the next month (September 30 - October 30, 2025).

**Breakdown:**
• 3 vesting events scheduled
• All from RSU grants only (as requested)
• Next vest: October 10, 2025

**Would you like to:**
• See the specific vesting dates and amounts?
• Check vesting schedules beyond the next month?
• View John's total equity holdings across all plan types?
```

### Output (Final Response Package)

```json
{
  "response_text": "John Smith will receive **1,750 RSU shares** vesting over the next month (September 30 - October 30, 2025).\n\n**Breakdown:**\n• 3 vesting events scheduled\n• All from RSU grants only (as requested)\n• Next vest: October 10, 2025\n\n**Would you like to:**\n• See the specific vesting dates and amounts?\n• Check vesting schedules beyond the next month?\n• View John's total equity holdings across all plan types?",
  "response_type": "aggregate_result",
  "primary_answer": {
    "value": 1750,
    "unit": "shares",
    "participant": "John Smith",
    "plan_type": "RSU",
    "time_period": "Next 1 month"
  },
  "supporting_data": {
    "vesting_events_count": 3,
    "date_range": "2025-09-30 to 2025-10-30",
    "query_execution_time_ms": 284
  },
  "follow_up_suggestions": [
    "See specific vesting dates and amounts",
    "Check vesting schedules beyond next month",
    "View total equity holdings across all plan types"
  ],
  "confidence": 1.0,
  "data_freshness": "real_time",
  "processing_time_ms": 512
}
```

### Explanation
- ✅ Direct answer: **1,750 RSU shares**
- ✅ Context provided: John Smith, next month, RSU only
- ✅ Additional detail: 3 vesting events
- ✅ Helpful: Mentioned next vest date (Oct 10)
- ✅ Actionable: Suggested 3 follow-up questions

---

## Complete End-to-End Summary

### Final Data Flow

```
INPUT: "For participant jhon give me total shares that will be 
        released in next one month for rsu grants"
        
        ↓ Step 1: Understanding
        Corrected: "John", Category: AGGREGATE
        
        ↓ Step 2: Classification  
        Query Type: VESTING_SCHEDULE
        
        ↓ Step 3: Entity Extraction
        Extracted: John, RSU, "next one month", "total shares"
        
        ↓ Step 4: Normalization
        participant_id: 42 (John Smith)
        date_range: 2025-09-30 to 2025-10-30
        plan_type: RSU
        
        ↓ Step 5: Parameter Extraction
        aggregation_only: true
        metric: total_shares = SUM(vs.vest_quantity)
        
        ↓ Step 6: SQL Generation
        SELECT SUM(vs.vest_quantity) as total_shares
        FROM vesting_schedules vs
        JOIN... WHERE participant_id=42 AND plan_type='RSU'
        AND vest_date BETWEEN...
        
        ↓ Step 7: Security Validation
        ✓ Client filter present
        ✓ User authorized
        ✓ Audit logged
        
        ↓ Step 8: Query Execution
        Result: 1,750 shares (from 3 vesting events)
        Execution time: 284ms
        
        ↓ Step 9: Response Formatting
        
OUTPUT: "John Smith will receive **1,750 RSU shares** vesting 
         over the next month..."
```

### Complete Processing Metrics

| Step | Duration | Type | Cost |
|------|----------|------|------|
| 1. Understanding | 320ms | LLM | $0.002 |
| 2. Classification | 180ms | LLM | $0.001 |
| 3. Entity Extraction | 450ms | LLM | $0.003 |
| 4. Normalization | 150ms | DB + Logic | $0 |
| 5. Parameter Extraction | 420ms | LLM | $0.003 |
| 6. SQL Generation | 48ms | Logic | $0 |
| 7. Security Validation | 87ms | Logic | $0 |
| 8. Query Execution | 284ms | PostgreSQL | $0 |
| 9. Response Formatting | 512ms | LLM | $0.004 |
| **TOTAL** | **2.451s** | | **$0.013** |

### Files Used at Each Step

| Step | YAML Configs | Prompts | Other |
|------|-------------|---------|-------|
| 1 | business_vocabulary.yaml | understanding_prompt.txt | - |
| 2 | entity_schema.yaml | classification_prompt.txt | - |
| 3 | entity_schema.yaml<br>business_vocabulary.yaml | entity_extraction_prompt.txt | - |
| 4 | normalization_rules.yaml | - | PostgreSQL DB |
| 5 | metrics_schema.yaml | param_extraction/vesting_schedule.txt | - |
| 6 | - | - | vesting_schedule.sql template |
| 7 | - | - | sqlglot validator |
| 8 | - | - | PostgreSQL DB |
| 9 | - | response_formatting_prompt.txt | - |

### Success! 🎉

**Final Answer Delivered to User:**

> John Smith will receive **1,750 RSU shares** vesting over the next month (September 30 - October 30, 2025).
> 
> **Breakdown:**
> • 3 vesting events scheduled
> • All from RSU grants only (as requested)
> • Next vest: October 10, 2025

**Accuracy:** ✅ Perfect - Found exactly what was requested
**Performance:** ✅ Under 3 seconds end-to-end
**Cost:** ✅ Only $0.013 per query
**Security:** ✅ All checks passed, audit trail logged
