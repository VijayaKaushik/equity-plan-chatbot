# Deep Dive: Steps 2, 5, and 6
## Understanding Query Type Classification, Parameter Extraction, and SQL Generation

---

## Table of Contents
1. [Overview: How Steps 2, 5, 6 Work Together](#overview)
2. [Step 2: Query Type Classification](#step-2)
3. [Step 5: Template Parameter Extraction](#step-5)
4. [Step 6: Template Population (SQL Generation)](#step-6)
5. [Complete Examples](#complete-examples)

---

## Overview: How Steps 2, 5, 6 Work Together

### The Big Picture

```
Step 2: Query Type Classification
    ↓
    Determines WHICH template to use
    Output: "PARTICIPANT_LEVEL" or "CLIENT_LEVEL" or "VESTING_SCHEDULE"
    
Step 5: Template Parameter Extraction  
    ↓
    Determines WHAT data to extract from that template
    Output: metrics, filters, grouping, etc.
    
Step 6: Template Population
    ↓
    Generates the actual SQL using the template + parameters
    Output: Executable SQL query
```

### Analogy

Think of it like ordering food:

- **Step 2** = Choosing the **menu** (Pizza menu vs Burger menu vs Salad menu)
- **Step 5** = Specifying your **order details** (Large pepperoni, extra cheese, thin crust)
- **Step 6** = **Cooking** the food (Making the actual pizza)

---

## Step 2: Query Type Classification

### What It Does

Step 2 determines **WHICH template category** the query belongs to. This is a high-level categorization.

### Available Query Types

| Query Type | When to Use | Example Queries |
|------------|-------------|-----------------|
| **PARTICIPANT_LEVEL** | Query about individual employees | "Show John's grants", "List participants with RSUs" |
| **CLIENT_LEVEL** | Query about companies | "List companies with participant counts" |
| **VESTING_SCHEDULE** | Query about time-based vesting | "What vests in next 30 days?" |
| **REGIONAL** | Query about geographic grouping | "Participants by country" |
| **FINANCIAL_METRICS** | Query about burn rate, expense | "What's our burn rate?" |
| **COMPLIANCE_AUDIT** | Query about regulatory compliance | "Who exceeds 5% ownership?" |

### Decision Logic

```python
def classify_query_type(query: str, query_category: str) -> str:
    """
    Step 2: Classify into query type
    
    Args:
        query: Processed query from Step 1
        query_category: AGGREGATE or DETAIL from Step 1
    
    Returns:
        Query type string
    """
    
    # Rule 1: Check for participant mentions
    if mentions_specific_person(query):
        return "PARTICIPANT_LEVEL"
    
    # Rule 2: Check for time/vesting keywords
    if has_time_keywords(query):
        # "vesting in", "releasing", "vest dates"
        return "VESTING_SCHEDULE"
    
    # Rule 3: Check for company/client focus
    if query_category == "AGGREGATE" and mentions_companies(query):
        return "CLIENT_LEVEL"
    
    # Rule 4: Check for geographic keywords
    if has_geographic_keywords(query):
        # "by country", "in UK", "EMEA"
        return "REGIONAL"
    
    # Rule 5: Check for financial metrics
    if has_financial_keywords(query):
        # "burn rate", "expense", "dilution"
        return "FINANCIAL_METRICS"
    
    # Default based on category
    if query_category == "AGGREGATE":
        return "CLIENT_LEVEL"
    else:
        return "PARTICIPANT_LEVEL"
```

### Detailed Classification Rules

#### Rule 1: Participant-Level Indicators

**Positive Indicators** (→ PARTICIPANT_LEVEL):
- Specific person names: "John Smith", "Sarah"
- Pronouns after discussing person: "his grants", "her vesting"
- Keywords: "participant", "employee", "who", "show me [person]"
- Plural participants with details: "List all participants with..."

**Examples**:
```
"Show me John's grants" → PARTICIPANT_LEVEL
"Who has unvested RSUs?" → PARTICIPANT_LEVEL
"List participants in engineering" → PARTICIPANT_LEVEL
```

#### Rule 2: Vesting Schedule Indicators

**Positive Indicators** (→ VESTING_SCHEDULE):
- Time expressions: "in next 30 days", "this quarter", "by December"
- Vesting verbs: "vesting", "releasing", "vest dates"
- Schedule keywords: "schedule", "timeline", "upcoming"

**Examples**:
```
"What's vesting in next 30 days?" → VESTING_SCHEDULE
"Show upcoming release dates" → VESTING_SCHEDULE
"When do John's shares vest?" → VESTING_SCHEDULE
```

#### Rule 3: Client-Level Indicators

**Positive Indicators** (→ CLIENT_LEVEL):
- Company focus: "companies", "clients", "portfolio"
- Aggregations by company: "per company", "by company"
- Company comparisons: "which company has most..."

**Examples**:
```
"List companies with participant counts" → CLIENT_LEVEL
"How many grants per company?" → CLIENT_LEVEL
"Which companies have most equity?" → CLIENT_LEVEL
```

### Step 2 Example Walkthrough

**Query**: "How many unveiled shares does John Smith have?"

**Step 1 Output**:
```json
{
  "processed_query": "How many unveiled shares does John Smith have?",
  "query_category": "AGGREGATE",
  "intent": "aggregate"
}
```

**Step 2 Processing**:
```python
# Input
query = "How many unveiled shares does John Smith have?"
category = "AGGREGATE"

# Check Rule 1: Specific person mentioned?
if "John Smith" in query:  # ✅ YES
    # Even though AGGREGATE, this is about a specific participant
    return "PARTICIPANT_LEVEL"
```

**Step 2 Output**:
```json
{
  "query_type": "PARTICIPANT_LEVEL",
  "confidence": 0.98,
  "reasoning": "Query mentions specific participant 'John Smith'. Even though asking for aggregate (count), the focus is participant-level data.",
  "alternative_type": null
}
```

---

## Step 5: Template Parameter Extraction

### What It Does

Step 5 takes the **query type from Step 2** and extracts **specific parameters** needed to populate that template.

### Why We Need Step 5

Different query types need different information:

```
PARTICIPANT_LEVEL needs:
- Which participant(s)?
- Which metrics? (unveiled, vested, granted)
- Group by participant or aggregate?
- Which fields to display?

CLIENT_LEVEL needs:
- Which clients?
- Which aggregate metrics?
- Include zero counts?

VESTING_SCHEDULE needs:
- Date range?
- Which participants?
- Vesting status (pending/vested)?
```

### Parameter Types

#### 1. **Metrics** (What to Calculate)

Maps user intent to specific calculations:

| User Says | Metric Name | What It Calculates |
|-----------|-------------|-------------------|
| "unveiled shares" | `unveiled_shares` | `SUM(fm.share_units * mbm.unveiled)` |
| "vested shares" | `vested_shares` | `SUM(fm.share_units * mbm.vested)` |
| "granted shares" | `granted_shares` | `SUM(fm.share_units * mbm.granted)` |
| "total equity" | `total_shares` | Sum of all balance types |

#### 2. **Aggregation Type**

Determines output format:

- **aggregation_only = true**: Returns single number
  - Query: "How many unveiled shares does John have?"
  - Output: `5000`

- **aggregation_only = false**: Returns rows with details
  - Query: "Show me John's unveiled shares by grant"
  - Output: Table with grant details

#### 3. **Filters**

Which data to include:

```python
filters = {
    'participant_hub_key': 'PRT00000000000000000042',  # From Step 4
    'client_hub_key': 'CLNT00000000000000000002',      # Security
    'date_range': {'start': '2024-01-01', 'end': '2024-12-31'},
    'plan_type': 'RSU'
}
```

#### 4. **Display Fields**

What columns to show (if not aggregation_only):

```python
display_fields = [
    'pd.participant_name',
    'pd.email',
    'pd.department'
]
```

### Step 5 Prompt Structure

Each query type has its own prompt. Here's the PARTICIPANT_LEVEL prompt:

```
You are extracting parameters for PARTICIPANT_LEVEL queries.

USER QUERY: "How many unveiled shares does John Smith have?"
NORMALIZED ENTITIES: {
    "participant_hub_key": "PRT00000000000000000042"
}

AVAILABLE METRICS:
- unveiled_shares: SUM(fm.share_units * mbm.unveiled)
- vested_shares: SUM(fm.share_units * mbm.vested)
- granted_shares: SUM(fm.share_units * mbm.granted)

PARAMETERS TO EXTRACT:

1. aggregation_only (boolean)
   - true: User wants ONLY summary number
   - false: User wants to see details

2. metrics (list)
   - Which metrics to calculate
   
3. display_fields (list)
   - Which columns to show (if aggregation_only=false)
   
4. filters (object)
   - participant_hub_key: from normalized entities
   - date_range: if time filter mentioned
   
5. group_by (string)
   - How to group results

OUTPUT FORMAT: JSON
```

### Step 5 Example Walkthrough

**Query**: "How many unveiled shares does John Smith have?"

**Step 2 Output**: `query_type = "PARTICIPANT_LEVEL"`

**Step 4 Output** (Normalized Entities):
```json
{
  "participant_hub_key": "PRT00000000000000000042",
  "participant_name": "John Smith"
}
```

**Step 5 Processing**:
```python
# LLM analyzes query with prompt
prompt = f"""
Extract parameters for PARTICIPANT_LEVEL query.

Query: "How many unveiled shares does John Smith have?"
Entities: {normalized_entities}
Available Metrics: {metrics_schema}

Determine:
1. aggregation_only: Does user want just a number or details?
   - "how many" = true (just the count)
   - "show me" = false (want details)
   
2. metrics: Which balance types?
   - Query says "unveiled shares" → ['unveiled_shares']
   
3. display_fields: What to show?
   - If aggregation_only=true, not needed
   
4. filters: What constraints?
   - participant_hub_key from entities
"""

# LLM Response
```

**Step 5 Output**:
```json
{
  "aggregation_only": true,
  "metrics": ["unveiled_shares"],
  "display_fields": [],
  "filters": {
    "participant_hub_key": "PRT00000000000000000042"
  },
  "group_by": "",
  "ordering": "",
  "limit": 1,
  "reasoning": "User asks 'how many' which indicates wanting a single aggregate number, not a list. Query mentions 'unveiled' so metric is 'unveiled_shares'. Specific participant (John Smith) so filter by participant_hub_key."
}
```

### Decision Logic in Step 5

```python
def extract_aggregation_only(query: str) -> bool:
    """Determine if user wants just aggregate or details"""
    
    # Aggregate indicators
    aggregate_keywords = [
        'how many', 'total', 'count', 'sum',
        'what is the', "what's the"
    ]
    
    # Detail indicators
    detail_keywords = [
        'show', 'list', 'display', 'give me',
        'which', 'who', 'what are'
    ]
    
    query_lower = query.lower()
    
    # Check for aggregate keywords
    has_aggregate = any(kw in query_lower for kw in aggregate_keywords)
    
    # Check for detail keywords
    has_detail = any(kw in query_lower for kw in detail_keywords)
    
    # Decision
    if has_aggregate and not has_detail:
        return True  # Aggregate only
    elif has_detail and not has_aggregate:
        return False  # Details
    elif 'list' in query_lower or 'show' in query_lower:
        return False  # When ambiguous, prefer details
    else:
        return True  # Default to aggregate
```

### Metric Extraction Logic

```python
def extract_metrics(query: str) -> List[str]:
    """Extract which balance types user is asking about"""
    
    balance_keywords = {
        'unveiled': ['unveiled', 'unvested', 'not vested', 'pending'],
        'vested': ['vested', 'earned'],
        'granted': ['granted', 'awarded', 'total grant'],
        'exercisable': ['exercisable', 'can exercise'],
        'forfeited': ['forfeited', 'lost']
    }
    
    query_lower = query.lower()
    metrics = []
    
    # Check for each balance type
    for balance_type, keywords in balance_keywords.items():
        if any(kw in query_lower for kw in keywords):
            metrics.append(f"{balance_type}_shares")
    
    # Default if nothing found
    if not metrics:
        # If asking about "equity" or "shares" generally
        if 'equity' in query_lower or 'shares' in query_lower:
            metrics = ['unveiled_shares']  # Most common
    
    return metrics
```

---

## Step 6: Template Population (SQL Generation)

### What It Does

Step 6 takes the **query type** (from Step 2) and **parameters** (from Step 5) and generates the actual SQL.

### Architecture

```
Step 6 Components:

1. TemplatePopulationStep (orchestrator)
   ├─ Detects schema type (movement/traditional)
   ├─ Routes to appropriate builder
   └─ Returns SQLResult
   
2. RealMovementCalculator (for movement schema)
   ├─ build_unvested_shares_sql()
   ├─ build_vested_shares_sql()
   ├─ build_multi_balance_sql()
   ├─ build_participant_balance_sql()
   └─ build_retirement_acceleration_sql()
```

### Routing Logic

```python
class TemplatePopulationStep:
    
    def _route_to_calculator_method(
        self,
        query_type: str,
        metrics: List[str],
        filters: MovementFilter,
        parameters: Dict
    ) -> str:
        """
        Route to appropriate method based on:
        1. Special patterns (retirement)
        2. Number of metrics (single vs multiple)
        3. Aggregation type
        """
        
        # STEP 1: Check for special patterns
        if self._is_retirement_query(parameters):
            return self.movement_calc.build_retirement_acceleration_sql(filters)
        
        # STEP 2: Single metric queries
        if len(metrics) == 1:
            metric = metrics[0]
            
            if metric == 'unveiled_shares':
                return self.movement_calc.build_unvested_shares_sql(filters)
            
            elif metric == 'vested_shares':
                return self.movement_calc.build_vested_shares_sql(filters)
            
            # Other single metrics...
        
        # STEP 3: Multiple metrics
        if len(metrics) > 1:
            balance_types = [m.replace('_shares', '') for m in metrics]
            
            # Check if need participant grouping
            if query_type == 'PARTICIPANT_LEVEL':
                if parameters.get('aggregation_only'):
                    # Single participant, aggregate
                    return self.movement_calc.build_multi_balance_sql(
                        balance_types_list=balance_types,
                        filters=filters,
                        group_by_participant=False
                    )
                else:
                    # Multiple participants or details needed
                    return self.movement_calc.build_multi_balance_sql(
                        balance_types_list=balance_types,
                        filters=filters,
                        group_by_participant=True
                    )
        
        # STEP 4: Fallback
        return self.movement_calc.build_movement_breakdown_sql(filters)
```

### SQL Building Process

```python
class RealMovementCalculator:
    
    def build_unvested_shares_sql(self, filters: MovementFilter) -> str:
        """
        Build SQL for unveiled shares
        
        Steps:
        1. Build calculation expression: SUM(fm.share_units * mbm.unveiled)
        2. Build FROM/JOIN clauses
        3. Build WHERE clause from filters
        4. Combine into final SQL
        """
        
        # STEP 1: Build calculation
        calc_expr = "SUM(fm.share_units * mbm.unveiled)"
        
        # STEP 2: Build FROM/JOIN
        sql = f"""SELECT {calc_expr} as unveiled_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type"""
        
        # STEP 3: Build WHERE clause
        where_conditions = []
        
        if filters.participant_hub_key:
            where_conditions.append(
                f"fm.participant_hub_key = '{filters.participant_hub_key}'"
            )
        
        if filters.client_hub_key:
            where_conditions.append(
                f"fm.client_hub_key = '{filters.client_hub_key}'"
            )
        
        if where_conditions:
            sql += "\nWHERE " + " AND ".join(where_conditions)
        
        return sql
```

---

## Complete Examples

### Example 1: Simple Aggregate Query

**User Query**: "How many unveiled shares does John Smith have?"

#### Step 2: Classification

**Input**:
- Query: "How many unveiled shares does John Smith have?"
- Category: AGGREGATE

**Processing**:
```python
# Check indicators
mentions_person = "John Smith" in query  # ✅ True
has_time_keywords = False
is_aggregate = category == "AGGREGATE"  # ✅ True

# Decision
if mentions_person:
    return "PARTICIPANT_LEVEL"  # ✅
```

**Output**:
```json
{
  "query_type": "PARTICIPANT_LEVEL",
  "confidence": 0.98
}
```

#### Step 5: Parameter Extraction

**Input**:
- Query type: PARTICIPANT_LEVEL
- Normalized entities: `{"participant_hub_key": "PRT00000000000000000042"}`

**Processing**:
```python
# 1. Aggregation type
"how many" in query  # ✅ aggregate indicator
aggregation_only = True

# 2. Metrics
"unveiled" in query  # ✅
metrics = ["unveiled_shares"]

# 3. Display fields
if aggregation_only:
    display_fields = []  # Not needed

# 4. Filters
filters = {
    "participant_hub_key": "PRT00000000000000000042"
}
```

**Output**:
```json
{
  "aggregation_only": true,
  "metrics": ["unveiled_shares"],
  "display_fields": [],
  "filters": {
    "participant_hub_key": "PRT00000000000000000042"
  }
}
```

#### Step 6: SQL Generation

**Input**:
- Query type: PARTICIPANT_LEVEL
- Parameters: (from Step 5)
- User context: `{"client_hub_key": "CLNT00000000000000000002"}`

**Processing**:
```python
# 1. Build MovementFilter
filters = MovementFilter(
    participant_hub_key="PRT00000000000000000042",
    client_hub_key="CLNT00000000000000000002"
)

# 2. Route to method
len(metrics) == 1  # ✅ Single metric
metrics[0] == 'unveiled_shares'  # ✅

# Call: build_unvested_shares_sql(filters)

# 3. Generate SQL
calc_expr = "SUM(fm.share_units * mbm.unveiled)"
# Build FROM/JOIN/WHERE...
```

**Output**:
```sql
SELECT SUM(fm.share_units * mbm.unveiled) as unveiled_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
WHERE fm.participant_hub_key = 'PRT00000000000000000042'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
```

---

### Example 2: Multiple Balance Types with Details

**User Query**: "Show me John's unveiled and vested shares"

#### Step 2: Classification

**Input**:
- Query: "Show me John's unveiled and vested shares"
- Category: DETAIL

**Processing**:
```python
mentions_person = "John" in query  # ✅ True
category = "DETAIL"  # ✅

return "PARTICIPANT_LEVEL"
```

**Output**:
```json
{
  "query_type": "PARTICIPANT_LEVEL",
  "confidence": 0.95
}
```

#### Step 5: Parameter Extraction

**Input**:
- Query type: PARTICIPANT_LEVEL
- Normalized entities: `{"participant_hub_key": "PRT00000000000000000042"}`

**Processing**:
```python
# 1. Aggregation type
"show me" in query  # ✅ detail indicator
aggregation_only = False  # User wants to see details

# 2. Metrics
"unveiled" in query  # ✅
"vested" in query  # ✅
metrics = ["unveiled_shares", "vested_shares"]

# 3. Display fields (since aggregation_only=False)
display_fields = [
    "pd.participant_name",
    "pd.email"
]

# 4. Filters
filters = {
    "participant_hub_key": "PRT00000000000000000042"
}
```

**Output**:
```json
{
  "aggregation_only": false,
  "metrics": ["unveiled_shares", "vested_shares"],
  "display_fields": ["pd.participant_name", "pd.email"],
  "filters": {
    "participant_hub_key": "PRT00000000000000000042"
  }
}
```

#### Step 6: SQL Generation

**Input**:
- Query type: PARTICIPANT_LEVEL
- Parameters: Multiple metrics, aggregation_only=false

**Processing**:
```python
# 1. Build MovementFilter (same as Example 1)

# 2. Route to method
len(metrics) == 2  # ✅ Multiple metrics
aggregation_only = False  # ✅ Need details

# Call: build_multi_balance_sql(
#     balance_types_list=['unveiled', 'vested'],
#     filters=filters,
#     group_by_participant=False  # Single participant
# )

# 3. Generate SQL with multiple SUMs
```

**Output**:
```sql
SELECT 
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
WHERE fm.participant_hub_key = 'PRT00000000000000000042'
    AND fm.client_hub_key = 'CLNT00000000000000000002'
GROUP BY pd.participant_name, pd.email
```

---

### Example 3: Company-Wide Aggregate

**User Query**: "How many total unveiled shares do we have?"

#### Step 2: Classification

**Input**:
- Query: "How many total unveiled shares do we have?"
- Category: AGGREGATE

**Processing**:
```python
mentions_person = False  # No specific person
is_aggregate = True
mentions_companies = False
has_we = "we" in query  # Company-wide scope

# Decision: Company-wide aggregate
return "CLIENT_LEVEL"
```

**Output**:
```json
{
  "query_type": "CLIENT_LEVEL",
  "confidence": 0.85,
  "reasoning": "Aggregate query with company-wide scope ('we')"
}
```

#### Step 5: Parameter Extraction

**Input**:
- Query type: CLIENT_LEVEL
- No specific entities (company-wide)

**Processing**:
```python
# 1. Aggregation type
"how many total" in query  # ✅ Strong aggregate
aggregation_only = True

# 2. Metrics
metrics = ["unveiled_shares"]

# 3. No grouping needed (company-wide total)
```

**Output**:
```json
{
  "aggregation_only": true,
  "metrics": ["unveiled_shares"],
  "filters": {}
}
```

#### Step 6: SQL Generation

**Input**:
- Query type: CLIENT_LEVEL
- Parameters: Single metric, aggregation_only=true
- User context: `{"client_hub_key": "CLNT00000000000000000002"}`

**Processing**:
```python
# 1. Build MovementFilter (only client filter)
filters = MovementFilter(
    client_hub_key="CLNT00000000000000000002"
)

# 2. Route to method
len(metrics) == 1  # ✅
# Call: build_unvested_shares_sql(filters)
```

**Output**:
```sql
SELECT SUM(fm.share_units * mbm.unveiled) as unveiled_shares
FROM bi_fact_movement fm
INNER JOIN bi_movement_balance_mapping mbm
    ON fm.movement_type = mbm.movement_type
    AND fm.movement_sub_type = mbm.movement_sub_type
    AND fm.movement_sub_sub_type = mbm.movement_sub_sub_type
WHERE fm.client_hub_key = 'CLNT00000000000000000002'
```

---

### Example 4: Retirement Acceleration (Special Pattern)

**User Query**: "Who is eligible for retirement acceleration?"

#### Step 2: Classification

**Input**:
- Query: "Who is eligible for retirement acceleration?"
- Category: DETAIL

**Processing**:
```python
has_retirement = "retirement" in query  # ✅
is_who_query = query.startswith("Who")  # ✅

# Special case for retirement
return "PARTICIPANT_LEVEL"
```

**Output**:
```json
{
  "query_type": "PARTICIPANT_LEVEL",
  "confidence": 0.99,
  "reasoning": "Retirement acceleration query about participants"
}
```

#### Step 5: Parameter Extraction

**Input**:
- Query type: PARTICIPANT_LEVEL
- Special keyword: "retirement"

**Processing**:
```python
# 1. Detect special pattern
"retirement" in query  # ✅
query_keywords = ["retirement_acceleration"]

# 2. Metrics
metrics = ["unveiled_shares"]  # Retirement only cares about unvested

# 3. Special filters
has_retirement_eligibility = True
```

**Output**:
```json
{
  "aggregation_only": false,
  "metrics": ["unveiled_shares"],
  "display_fields": ["pd.participant_name", "pd.email"],
  "query_keywords": ["retirement_acceleration"],
  "filters": {
    "has_retirement_eligibility": true
  }
}
```

#### Step 6: SQL Generation

**Input**:
- Query type: PARTICIPANT_LEVEL
- Parameters: query_keywords contains "retirement"

**Processing**:
```python
# 1. Detect special pattern
if "retirement" in parameters.get('query_keywords', []):
    # ✅ Use special method
    return self.movement_calc.build_retirement_acceleration_sql(filters)
```

**Output**:
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

## Summary Tables

### Step 2: Query Type Decision Matrix

| Query Characteristics | Query Type |
|----------------------|------------|
| Mentions specific person + any category | PARTICIPANT_LEVEL |
| Time keywords (vesting in, by date) | VESTING_SCHEDULE |
| Company-wide + AGGREGATE | CLIENT_LEVEL |
| Geographic keywords (by country, region) | REGIONAL |
| Financial keywords (burn rate, expense) | FINANCIAL_METRICS |

### Step 5: Parameter Extraction Rules

| User Says | Parameter | Value |
|-----------|-----------|-------|
| "how many", "total" | aggregation_only | true |
| "show me", "list" | aggregation_only | false |
| "unveiled", "unvested" | metrics | ['unveiled_shares'] |
| "vested" | metrics | ['vested_shares'] |
| "unveiled and vested" | metrics | ['unveiled_shares', 'vested_shares'] |

### Step 6: Method Routing Rules

| Conditions | Method Called |
|-----------|---------------|
| query_keywords contains "retirement" | build_retirement_acceleration_sql() |
| 1 metric = 'unveiled_shares' | build_unvested_shares_sql() |
| 1 metric = 'vested_shares' | build_vested_shares_sql() |
| Multiple metrics + group_by_participant=True | build_multi_balance_sql(group=True) |
| Multiple metrics + group_by_participant=False | build_multi_balance_sql(group=False) |

---

## Key Takeaways

1. **Step 2** determines **WHICH template** (high-level category)
2. **Step 5** determines **WHAT data** from that template (specific parameters)
3. **Step 6** generates **ACTUAL SQL** using template + parameters

4. The steps work as a **funnel**:
   - Step 2: Broad categorization (6 types)
   - Step 5: Detailed extraction (10+ parameters)
   - Step 6: Precise SQL generation (multiple methods)

5. **Special patterns** (like retirement) are detected across all steps:
   - Step 2: Recognizes retirement context
   - Step 5: Extracts retirement-specific parameters
   - Step 6: Routes to specialized method
