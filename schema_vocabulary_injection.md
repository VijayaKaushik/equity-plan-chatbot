# Schema & Business Vocabulary Injection Guide

## Overview: What to Inject Where

| Step | Information Type | Level of Detail | Why Here? |
|------|-----------------|-----------------|-----------|
| **Step 1: Understanding** | Business vocabulary only | High-level concepts | Helps LLM understand equity terminology |
| **Step 3: Entity Extraction** | Entity types + vocabulary | Medium detail | Knows what entities exist and are valid |
| **Step 5: Parameter Extraction** | Available metrics + schema relationships | Template-specific | Knows what metrics can be calculated |
| **Step 6: SQL Generation** | Full schema with columns/types | Complete detail | Generates accurate SQL |

---

## Step 1: Understanding - Business Vocabulary

### What to Include:
- Equity plan types (RSU, ISO, NSO, ESPP, PSU, SAR, RSA)
- Status values (active, terminated, vested, unvested, forfeited)
- Common equity terms and synonyms
- Metrics terminology

### File: `config/business_vocabulary.yaml`

```yaml
plan_types:
  - name: RSU
    full_name: Restricted Stock Units
    synonyms: [restricted stock, rsus]
  - name: ISO
    full_name: Incentive Stock Options
    synonyms: [incentive options, isos]
  - name: NSO
    full_name: Non-Qualified Stock Options
    synonyms: [non-qualified options, nqso, nsos]
  - name: ESPP
    full_name: Employee Stock Purchase Plan
    synonyms: [purchase plan, stock purchase]
  - name: PSU
    full_name: Performance Stock Units
    synonyms: [performance shares, psus]
  - name: SAR
    full_name: Stock Appreciation Rights
    synonyms: [appreciation rights, sars]

participant_statuses:
  - active: Currently employed
  - terminated: No longer employed
  - on_leave: Temporarily away (maternity, sabbatical)
  - retired: Retired with special treatment

vesting_statuses:
  - pending: Not yet vested
  - vested: Vested and available
  - forfeited: Lost due to termination
  - exercised: Options exercised
  - expired: Options expired unexercised

grant_terms:
  - vesting: The process of earning equity over time
  - cliff: Minimum period before any vesting occurs
  - tranche: A portion of a grant that vests on a specific date
  - exercise: Converting stock options to shares
  - strike_price: Price at which options can be exercised
  - fmv: Fair Market Value
  - spread: Difference between FMV and exercise price

metrics:
  - burn_rate: Rate at which share reserves are consumed
  - dilution: Increase in outstanding shares affecting ownership %
  - overhang: Ratio of unexercised options to shares outstanding
  - utilization: Percentage of share reserve granted
```

### Updated Prompt: `prompts/understanding_prompt.txt`

```txt
You are an expert at understanding natural language queries about equity compensation plans.

BUSINESS CONTEXT - Equity Compensation Terminology:

Plan Types:
- RSU (Restricted Stock Units): Grants of company stock that vest over time
- ISO (Incentive Stock Options): Tax-advantaged stock options
- NSO (Non-Qualified Stock Options): Standard stock options
- ESPP (Employee Stock Purchase Plan): Program allowing employees to purchase stock
- PSU (Performance Stock Units): Equity tied to performance goals
- SAR (Stock Appreciation Rights): Right to receive gain without buying stock

Key Terms:
- Vesting: Process of earning equity over time (e.g., "4-year vesting with 1-year cliff")
- Cliff: Minimum period before any equity vests
- Tranche: A portion of a grant vesting on a specific date
- Exercise: Converting stock options to actual shares
- Burn Rate: How quickly company grants equity from share reserve
- FMV (Fair Market Value): Current stock price

Status Values:
- Active: Currently employed participants
- Terminated: Former employees
- Vested: Equity that has completed vesting schedule
- Unvested/Pending: Equity still waiting to vest
- Forfeited: Equity lost due to termination
- Exercised: Options that have been converted to shares

Synonyms to Recognize:
- "Grants" = "Awards" = "Equity compensation"
- "Participants" = "Employees" = "Recipients"
- "Release dates" = "Vest dates" = "Vesting schedule"
- "Volume" = "Count" = "Number"

USER QUERY: "{query}"

[Rest of understanding prompt...]
```

---

## Step 3: Entity Extraction - Entity Types & Relationships

### What to Include:
- Available entity types
- High-level data model (which entities relate to which)
- Valid values for entity attributes

### File: `config/entity_schema.yaml`

```yaml
entity_types:
  clients:
    description: Companies/organizations in the system
    attributes: [name, industry, country]
    can_filter_by: [name, industry, country]
    
  participants:
    description: Employees receiving equity compensation
    attributes: [name, email, employee_id, department, country, status]
    can_filter_by: [name, department, country, status]
    belongs_to: clients
    
  plans:
    description: Equity compensation plans
    attributes: [plan_name, plan_type, status, share_reserve]
    can_filter_by: [plan_type, status]
    belongs_to: clients
    valid_plan_types: [RSU, ISO, NSO, ESPP, PSU, SAR, RSA]
    
  grants:
    description: Individual equity awards to participants
    attributes: [grant_date, quantity, status]
    can_filter_by: [grant_date, status, plan_type]
    belongs_to: [participants, plans]
    
  tranches:
    description: Subdivisions of grants with different vesting schedules
    attributes: [tranche_number, quantity]
    belongs_to: grants
    
  vesting_schedules:
    description: Specific dates when equity vests
    attributes: [vest_date, vest_quantity, vested_status]
    can_filter_by: [vest_date, vested_status]
    belongs_to: tranches

relationships:
  - clients have many participants
  - clients have many plans
  - participants have many grants
  - plans have many grants
  - grants have many tranches
  - tranches have many vesting_schedules
```

### Updated Prompt: `prompts/entity_extraction_prompt.txt`

Add this section at the top:

```txt
DATABASE ENTITY TYPES (High-Level):

Available Entities:
1. clients (companies) - Can filter by: name, industry, country
2. participants (employees) - Can filter by: name, department, country, status
3. plans (equity plans) - Can filter by: plan_type (RSU/ISO/NSO/ESPP/PSU), status
4. grants (individual awards) - Can filter by: grant_date, status, participant
5. tranches (grant subdivisions) - Relates to grants
6. vesting_schedules (vest dates) - Can filter by: vest_date, vested_status

Entity Relationships:
- Companies → have → Participants & Plans
- Participants → receive → Grants
- Plans → contain → Grants
- Grants → subdivided into → Tranches
- Tranches → scheduled in → Vesting Schedules

Valid Plan Types: RSU, ISO, NSO, ESPP, PSU, SAR, RSA
Valid Participant Statuses: active, terminated, on_leave, retired
Valid Vesting Statuses: pending, vested, forfeited, exercised, expired

[Rest of entity extraction prompt...]
```

---

## Step 5: Parameter Extraction - Available Metrics

### What to Include:
- Metrics available for each query type
- How metrics are calculated
- Which tables are needed for each metric

### File: `config/metrics_schema.yaml`

```yaml
client_level_metrics:
  participant_count:
    sql: "COUNT(DISTINCT p.id)"
    description: "Total number of participants"
    requires_tables: [participants]
    
  plan_count:
    sql: "COUNT(DISTINCT pl.id)"
    description: "Total number of equity plans"
    requires_tables: [plans]
    
  grant_count:
    sql: "COUNT(DISTINCT g.id)"
    description: "Total number of grants issued"
    requires_tables: [plans, grants]
    
  total_shares:
    sql: "SUM(g.quantity)"
    description: "Total shares granted"
    requires_tables: [plans, grants]
    
  active_participants:
    sql: "COUNT(DISTINCT CASE WHEN p.status = 'active' THEN p.id END)"
    description: "Count of currently active participants"
    requires_tables: [participants]
    
  vested_shares:
    sql: "SUM(CASE WHEN vs.vested_status = 'vested' THEN vs.vest_quantity ELSE 0 END)"
    description: "Total shares already vested"
    requires_tables: [plans, grants, tranches, vesting_schedules]
    
  unvested_shares:
    sql: "SUM(CASE WHEN vs.vested_status = 'pending' THEN vs.vest_quantity ELSE 0 END)"
    description: "Total shares not yet vested"
    requires_tables: [plans, grants, tranches, vesting_schedules]

participant_level_metrics:
  grant_count:
    sql: "COUNT(DISTINCT g.id)"
    description: "Number of grants per participant"
    requires_tables: [grants]
    
  vested_shares:
    sql: "SUM(CASE WHEN vs.vested_status = 'vested' THEN vs.vest_quantity ELSE 0 END)"
    requires_tables: [grants, tranches, vesting_schedules]
    
  unvested_shares:
    sql: "SUM(CASE WHEN vs.vested_status = 'pending' THEN vs.vest_quantity ELSE 0 END)"
    requires_tables: [grants, tranches, vesting_schedules]
    
  total_value:
    sql: "SUM(g.quantity * s.current_fmv)"
    description: "Total value of equity at current FMV"
    requires_tables: [grants, securities]
    
  latest_grant_date:
    sql: "MAX(g.grant_date)"
    requires_tables: [grants]

vesting_schedule_computed_fields:
  days_until_vest:
    sql: "DATE_PART('day', vs.vest_date - CURRENT_DATE)::int"
    description: "Days until vesting date"
    
  vest_value:
    sql: "vs.vest_quantity * s.current_fmv"
    description: "Value of vesting at current FMV"
    requires_tables: [securities]
    
  urgency:
    sql: "CASE WHEN vs.vest_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'Imminent' WHEN vs.vest_date <= CURRENT_DATE + INTERVAL '90 days' THEN 'Soon' ELSE 'Future' END"
    description: "Urgency level for upcoming vests"
```

### Updated Prompt: `prompts/param_extraction/client_level.txt`

Add this section:

```txt
AVAILABLE METRICS FOR CLIENT_LEVEL:

Standard Metrics:
- participant_count: COUNT(DISTINCT p.id) - requires JOIN participants
- plan_count: COUNT(DISTINCT pl.id) - requires JOIN plans
- grant_count: COUNT(DISTINCT g.id) - requires JOIN plans, grants
- total_shares: SUM(g.quantity) - requires JOIN plans, grants
- active_participants: COUNT(CASE WHEN p.status='active'...) - requires JOIN participants
- vested_shares: SUM(CASE WHEN vs.vested_status='vested'...) - requires JOIN to vesting_schedules
- unvested_shares: SUM(CASE WHEN vs.vested_status='pending'...) - requires JOIN to vesting_schedules

Join Requirements:
- If participant_count OR active_participants → need "participants" in joins_needed
- If plan_count → need "plans" in joins_needed
- If grant_count OR total_shares → need ["plans", "grants"] in joins_needed
- If vested_shares OR unvested_shares → need ["plans", "grants", "tranches", "vesting_schedules"]

[Rest of parameter extraction prompt...]
```

---

## Step 6: SQL Generation - Full Database Schema

### What to Include:
- Complete table definitions
- Column names and data types
- Foreign key relationships
- Index information (for optimization)

### File: `config/database_schema.yaml`

```yaml
tables:
  clients:
    columns:
      id: {type: integer, primary_key: true}
      name: {type: varchar(255), nullable: false}
      industry: {type: varchar(100)}
      country: {type: varchar(100)}
      legal_entity: {type: varchar(255)}
      status: {type: varchar(50), default: 'active'}
      outstanding_shares: {type: bigint}
      created_at: {type: timestamp}
    indexes:
      - name: idx_clients_name
        columns: [name]
    
  participants:
    columns:
      id: {type: integer, primary_key: true}
      client_id: {type: integer, foreign_key: clients.id, nullable: false}
      employee_id: {type: varchar(50)}
      name: {type: varchar(255), nullable: false}
      email: {type: varchar(255)}
      department: {type: varchar(100)}
      country: {type: varchar(100)}
      region: {type: varchar(50)}
      legal_entity: {type: varchar(255)}
      status: {type: varchar(50), default: 'active'}
      hire_date: {type: date}
      termination_date: {type: date}
      insider_status: {type: boolean, default: false}
      created_at: {type: timestamp}
    indexes:
      - name: idx_participants_client
        columns: [client_id]
      - name: idx_participants_name
        columns: [name]
      - name: idx_participants_status
        columns: [status]
    foreign_keys:
      - column: client_id
        references: clients(id)
        on_delete: RESTRICT
    
  plans:
    columns:
      id: {type: integer, primary_key: true}
      client_id: {type: integer, foreign_key: clients.id, nullable: false}
      plan_name: {type: varchar(255), nullable: false}
      plan_type: {type: varchar(50), nullable: false}
      status: {type: varchar(50), default: 'active'}
      share_reserve: {type: bigint}
      shares_granted: {type: bigint, default: 0}
      effective_date: {type: date}
      termination_date: {type: date}
      created_at: {type: timestamp}
    indexes:
      - name: idx_plans_client
        columns: [client_id]
      - name: idx_plans_type
        columns: [plan_type]
    foreign_keys:
      - column: client_id
        references: clients(id)
    constraints:
      - check: plan_type IN ('RSU','ISO','NSO','ESPP','PSU','SAR','RSA')
    
  grants:
    columns:
      id: {type: integer, primary_key: true}
      participant_id: {type: integer, foreign_key: participants.id, nullable: false}
      plan_id: {type: integer, foreign_key: plans.id, nullable: false}
      security_id: {type: integer, foreign_key: securities.id}
      grant_date: {type: date, nullable: false}
      quantity: {type: integer, nullable: false}
      exercise_price: {type: decimal(10,2)}
      fair_value_per_share: {type: decimal(10,2)}
      status: {type: varchar(50), default: 'active'}
      expiration_date: {type: date}
      forfeiture_date: {type: date}
      created_at: {type: timestamp}
    indexes:
      - name: idx_grants_participant
        columns: [participant_id]
      - name: idx_grants_plan
        columns: [plan_id]
      - name: idx_grants_date
        columns: [grant_date]
    foreign_keys:
      - column: participant_id
        references: participants(id)
      - column: plan_id
        references: plans(id)
    
  tranches:
    columns:
      id: {type: integer, primary_key: true}
      grant_id: {type: integer, foreign_key: grants.id, nullable: false}
      tranche_number: {type: integer, nullable: false}
      quantity: {type: integer, nullable: false}
      vesting_start_date: {type: date}
      created_at: {type: timestamp}
    indexes:
      - name: idx_tranches_grant
        columns: [grant_id]
    foreign_keys:
      - column: grant_id
        references: grants(id)
        on_delete: CASCADE
    
  vesting_schedules:
    columns:
      id: {type: integer, primary_key: true}
      tranche_id: {type: integer, foreign_key: tranches.id, nullable: false}
      vest_date: {type: date, nullable: false}
      vest_quantity: {type: integer, nullable: false}
      vested_status: {type: varchar(50), default: 'pending'}
      vested_date: {type: date}
      created_at: {type: timestamp}
    indexes:
      - name: idx_vesting_tranche
        columns: [tranche_id]
      - name: idx_vesting_date
        columns: [vest_date]
      - name: idx_vesting_status
        columns: [vested_status]
    foreign_keys:
      - column: tranche_id
        references: tranches(id)
        on_delete: CASCADE
    constraints:
      - check: vested_status IN ('pending','vested','forfeited')
    
  securities:
    columns:
      id: {type: integer, primary_key: true}
      plan_id: {type: integer, foreign_key: plans.id}
      security_type: {type: varchar(50)}
      share_class: {type: varchar(50)}
      current_fmv: {type: decimal(10,2)}
      fmv_date: {type: date}
      created_at: {type: timestamp}
```

### File: `templates/client_level.sql` (with schema comments)

```sql
-- CLIENT_LEVEL Query Template
-- Uses tables: clients, participants (optional), plans (optional), grants (optional)
-- Security: Always filter by accessible client IDs

SELECT 
    c.id,                    -- clients.id: integer (PK)
    c.name,                  -- clients.name: varchar(255)
    {metrics}                -- Dynamic metrics based on parameters
FROM clients c
{joins}                      -- Dynamic JOINs based on needed metrics
WHERE c.id IN ({accessible_clients})  -- Security filter (required)
    {filters}                -- Additional filters from query
{grouping}                   -- GROUP BY if metrics present
{ordering}                   -- ORDER BY for result ordering
{limit}                      -- LIMIT for pagination
```

### Code: How to Inject Schema in Step 6

```python
# step6_template_population.py

class TemplatePopulationStep:
    def __init__(self):
        # Load schema once at initialization
        with open('config/database_schema.yaml', 'r') as f:
            self.schema = yaml.safe_load(f)
    
    def execute(self, query_type: str, params: Dict, entities: Dict) -> Dict:
        # Get template
        template = self._load_template(query_type)
        
        # Build SQL components using schema knowledge
        metrics = self._build_metrics(params['metrics'])
        joins = self._build_joins_with_schema(
            params['joins_needed'], 
            params.get('filters', {})
        )
        filters = self._build_filters(entities, params.get('filters', {}))
        
        # Populate template
        sql = template.format(
            metrics=metrics,
            joins=joins,
            accessible_clients=','.join(map(str, entities['accessible_clients'])),
            filters=filters,
            grouping=params.get('grouping', ''),
            ordering=params.get('ordering', ''),
            limit=f"LIMIT {params.get('limit', 100)}"
        )
        
        return {'sql': sql, 'template_used': query_type}
    
    def _build_joins_with_schema(self, joins_needed: List[str], filters: Dict) -> str:
        """Build JOIN clauses using schema knowledge"""
        
        # Define JOIN patterns based on schema foreign keys
        JOIN_PATTERNS = {
            'participants': """
                LEFT JOIN participants p 
                    ON c.id = p.client_id
                    {participant_filters}
            """,
            'plans': """
                LEFT JOIN plans pl
                    ON c.id = pl.client_id
                    {plan_filters}
            """,
            'grants': """
                LEFT JOIN grants g
                    ON p.id = g.participant_id
                    {grant_filters}
            """,
            'tranches': """
                LEFT JOIN tranches t
                    ON g.id = t.grant_id
            """,
            'vesting_schedules': """
                LEFT JOIN vesting_schedules vs
                    ON t.id = vs.tranche_id
                    {vesting_filters}
            """
        }
        
        joins = []
        for join_name in joins_needed:
            if join_name in JOIN_PATTERNS:
                pattern = JOIN_PATTERNS[join_name]
                
                # Apply inline filters based on status
                inline_filters = []
                if join_name == 'participants' and filters.get('participant_status'):
                    inline_filters.append(f"AND p.status = '{filters['participant_status']}'")
                if join_name == 'plans' and filters.get('plan_status'):
                    inline_filters.append(f"AND pl.status = '{filters['plan_status']}'")
                
                pattern = pattern.format(
                    participant_filters=' '.join(inline_filters) if join_name == 'participants' else '',
                    plan_filters=' '.join(inline_filters) if join_name == 'plans' else '',
                    grant_filters='',
                    vesting_filters=''
                )
                
                joins.append(pattern)
        
        return '\n'.join(joins)
```

---

## Summary Table: What to Show Where

| Information | Step 1 | Step 3 | Step 5 | Step 6 |
|-------------|--------|--------|--------|--------|
| **Plan types** (RSU, ISO, NSO) | ✅ Full list | ✅ Full list | ✅ Full list | ✅ In schema |
| **Status values** | ✅ All statuses | ✅ All statuses | ✅ Valid values | ✅ In schema |
| **Equity terminology** | ✅ Definitions | ⬜ Not needed | ⬜ Not needed | ⬜ Not needed |
| **Entity types** | ⬜ Not needed | ✅ High-level list | ✅ With attributes | ✅ Full tables |
| **Relationships** | ⬜ Not needed | ✅ High-level | ✅ For joins | ✅ Foreign keys |
| **Available metrics** | ⬜ Not needed | ⬜ Not needed | ✅ Full list | ✅ SQL formulas |
| **Column names** | ⬜ Not needed | ⬜ Not needed | ⬜ Not needed | ✅ Complete |
| **Data types** | ⬜ Not needed | ⬜ Not needed | ⬜ Not needed | ✅ Complete |
| **Indexes** | ⬜ Not needed | ⬜ Not needed | ⬜ Not needed | ✅ For optimization |

---

## Implementation Checklist

- [ ] Create `config/business_vocabulary.yaml`
- [ ] Create `config/entity_schema.yaml`
- [ ] Create `config/metrics_schema.yaml`
- [ ] Create `config/database_schema.yaml`
- [ ] Update `prompts/understanding_prompt.txt` with vocabulary
- [ ] Update `prompts/entity_extraction_prompt.txt` with entity types
- [ ] Update all `prompts/param_extraction/*.txt` with available metrics
- [ ] Update SQL templates with schema comments
- [ ] Create schema loader utility class
- [ ] Add schema validation in Step 6

---

## Best Practices

1. **Keep prompts focused** - Don't dump entire schema in every prompt
2. **Progressive detail** - More detail as you get closer to SQL generation
3. **YAML files for maintainability** - Easy to update without changing prompts
4. **Schema validation** - Validate generated SQL against schema before execution
5. **Version control** - Track schema changes separately from code
6. **Documentation** - Keep business vocabulary synced with actual database

This approach gives the LLM **just enough context** at each step without overwhelming it with unnecessary details!