# Equity Chatbot Implementation Guide
## Complete File Structure, Process Flow & Sample Data

---

## Step 1: Query Understanding

### Files to Create
| File | Purpose |
|------|---------|
| `step1_understanding.py` | Main logic for query understanding |
| `prompts/understanding_prompt.txt` | LLM prompt template |
| `tests/test_step1.py` | Unit tests |

### Process Flow
1. Receive raw user query
2. Call LLM with understanding prompt
3. Parse LLM response
4. Validate output structure
5. Return QueryContext with understanding fields populated

### Sample Input
```json
{
  "user_query": "Give me this of companies and the volume of participants along with number of plans per company",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

### Sample Output
```json
{
  "corrected_query": "Give me LIST of companies and the volume of participants along with number of plans per company",
  "intent": "aggregate_report",
  "query_category": "AGGREGATE",
  "complexity": "medium",
  "requires_clarification": false,
  "reasoning": "Corrected typo 'this' to 'LIST'. Intent is to generate aggregate report of companies with metrics.",
  "llm_tokens_used": 285,
  "processing_time_ms": 320
}
```

### Code Sample: `step1_understanding.py`
```python
from typing import Dict
from dataclasses import dataclass
import openai

@dataclass
class UnderstandingResult:
    corrected_query: str
    intent: str
    query_category: str
    complexity: str
    requires_clarification: bool
    reasoning: str

class QueryUnderstandingStep:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt_template = self._load_prompt()
    
    def _load_prompt(self) -> str:
        with open('prompts/understanding_prompt.txt', 'r') as f:
            return f.read()
    
    async def execute(self, user_query: str) -> UnderstandingResult:
        prompt = self.prompt_template.format(query=user_query)
        
        response = await self.llm.call(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        result = self._parse_response(response)
        return UnderstandingResult(**result)
```

---

## Step 2: Query Type Classification

### Files to Create
| File | Purpose |
|------|---------|
| `step2_classification.py` | Query type classifier |
| `prompts/classification_prompt.txt` | Classification prompt template |
| `config/query_types.yaml` | Query type definitions |
| `tests/test_step2.py` | Unit tests |

### Process Flow
1. Receive corrected query + query_category from Step 1
2. Call LLM with classification prompt
3. Map to one of 6 query types
4. Validate confidence threshold
5. Return query type with confidence score

### Sample Input
```json
{
  "corrected_query": "Give me LIST of companies and the volume of participants along with number of plans per company",
  "query_category": "AGGREGATE",
  "complexity": "medium"
}
```

### Sample Output
```json
{
  "query_type": "CLIENT_LEVEL",
  "confidence": 0.95,
  "reasoning": "Query asks for company-level aggregations (participant count, plan count). AGGREGATE category confirms this is not detail listing.",
  "alternative_type": "REGIONAL",
  "alternative_confidence": 0.15,
  "processing_time_ms": 180
}
```

### Code Sample: `step2_classification.py`
```python
from enum import Enum

class QueryType(Enum):
    CLIENT_LEVEL = "client-level"
    PARTICIPANT_LEVEL = "participant-level"
    VESTING_SCHEDULE = "vesting-schedule"
    REGIONAL = "regional"
    FINANCIAL_METRICS = "financial-metrics"
    COMPLIANCE_AUDIT = "compliance-audit"

class QueryTypeClassifier:
    CONFIDENCE_THRESHOLD = 0.70
    
    async def execute(self, corrected_query: str, query_category: str) -> Dict:
        prompt = self.prompt_template.format(
            query=corrected_query,
            category=query_category
        )
        
        response = await self.llm.call(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=150
        )
        
        result = json.loads(response['choices'][0]['message']['content'])
        
        if result['confidence'] < self.CONFIDENCE_THRESHOLD:
            result['warning'] = "Low confidence - may need clarification"
        
        return result
```

---

## Step 3: Entity Extraction

### Files to Create
| File | Purpose |
|------|---------|
| `step3_entity_extraction.py` | Entity extractor with ambiguity detection |
| `prompts/entity_extraction_prompt.txt` | Entity extraction prompt |
| `utils/entity_level_detector.py` | Detects RECORDS vs TYPES vs PLANS |
| `config/entity_indicators.yaml` | Indicator definitions |
| `tests/test_step3.py` | Unit tests |

### Process Flow
1. Receive corrected query
2. Call LLM to extract entities
3. For "grants", detect entity level (RECORDS/TYPES/PLANS)
4. Calculate confidence score
5. Determine if clarification needed
6. Return entities with metadata

### Sample Input
```json
{
  "corrected_query": "Give me LIST of companies and the volume of participants along with number of plans per company",
  "query_type": "CLIENT_LEVEL"
}
```

### Sample Output
```json
{
  "entities": {
    "client_names": [],
    "participant_names": [],
    "plan_types": [],
    "statuses": ["active"],
    "date_expressions": [],
    "metrics": ["participant_volume", "plan_count"],
    "departments": [],
    "countries": []
  },
  "entity_level": null,
  "entity_level_confidence": null,
  "implicit_filters": {
    "participant_status": "active",
    "plan_status": "active"
  },
  "needs_clarification": false,
  "processing_time_ms": 450
}
```

### Sample for Ambiguous Query
**Input:** `"List all grants"`

**Output:**
```json
{
  "entities": {
    "entity_type": "grants",
    "client_names": [],
    "participant_names": []
  },
  "entity_level": "GRANT_RECORDS",
  "entity_level_confidence": 0.60,
  "indicators_found": [],
  "needs_clarification": true,
  "clarification_type": "entity_level_disambiguation",
  "clarification_options": [
    {
      "value": "GRANT_RECORDS",
      "label": "Grant records (individual awards)",
      "description": "Show 847 individual grant transactions",
      "is_default": true
    },
    {
      "value": "GRANT_TYPES",
      "label": "Grant types (RSU, ISO, NSO, etc.)",
      "description": "Show different types/categories"
    },
    {
      "value": "GRANT_PLANS",
      "label": "Grant plans (plan names)",
      "description": "Show equity plan names"
    }
  ],
  "reasoning": "No strong indicators found. Defaulting to GRANT_RECORDS but confidence is low (60%).",
  "processing_time_ms": 420
}
```

### Code Sample: `step3_entity_extraction.py`
```python
from utils.entity_level_detector import EntityLevelDetector

class EntityExtractionStep:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.detector = EntityLevelDetector()
    
    async def execute(self, corrected_query: str) -> Dict:
        # Extract entities using LLM
        entities = await self._extract_entities(corrected_query)
        
        # Check for ambiguous entity types
        if entities.get('entity_type') == 'grants':
            detection = self.detector.detect_entity_level(corrected_query)
            
            entities.update({
                'entity_level': detection['entity_level'],
                'entity_level_confidence': detection['confidence'],
                'indicators_found': detection['indicators_found'],
                'needs_clarification': detection['should_clarify'],
                'reasoning': detection['reasoning']
            })
            
            if detection['should_clarify']:
                entities['clarification_options'] = self._build_clarification_options()
        
        return entities
```

---

## Step 4: Entity Normalization

### Files to Create
| File | Purpose |
|------|---------|
| `step4_normalization.py` | Entity normalizer with DB lookups |
| `normalizers/client_normalizer.py` | Client name → ID lookup |
| `normalizers/participant_normalizer.py` | Participant name → ID lookup |
| `normalizers/date_normalizer.py` | Natural language → ISO dates |
| `normalizers/status_normalizer.py` | Status terms → enum values |
| `tests/test_step4.py` | Unit tests |

### Process Flow
1. Receive raw entities from Step 3
2. For each entity type, call appropriate normalizer
3. Perform database lookups (client names → IDs, etc.)
4. Convert natural language dates to ISO format
5. Apply user security filters
6. Return normalized entities ready for SQL

### Sample Input
```json
{
  "entities": {
    "client_names": [],
    "statuses": ["active"],
    "metrics": ["participant_volume", "plan_count"]
  },
  "user_context": {
    "user_id": "user_123",
    "accessible_clients": [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
  }
}
```

### Sample Output
```json
{
  "normalized_entities": {
    "client_ids": [],
    "participant_ids": [],
    "status_filters": {
      "participant_status": "active",
      "plan_status": "active"
    },
    "date_range": null,
    "metrics": ["participant_count", "plan_count"],
    "accessible_clients": [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
  },
  "normalization_log": [
    {
      "field": "statuses",
      "from": ["active"],
      "to": {"participant_status": "active", "plan_status": "active"},
      "method": "status_enum_mapping"
    },
    {
      "field": "metrics",
      "from": ["participant_volume", "plan_count"],
      "to": ["participant_count", "plan_count"],
      "method": "metric_standardization"
    }
  ],
  "database_queries_executed": 0,
  "processing_time_ms": 150
}
```

### Code Sample: `step4_normalization.py`
```python
from normalizers import ClientNormalizer, DateNormalizer, StatusNormalizer

class EntityNormalizationStep:
    def __init__(self, db_connection):
        self.db = db_connection
        self.client_normalizer = ClientNormalizer(db_connection)
        self.date_normalizer = DateNormalizer()
        self.status_normalizer = StatusNormalizer()
    
    async def execute(self, raw_entities: Dict, user_context: Dict) -> Dict:
        normalized = {}
        log = []
        
        # Normalize client names to IDs
        if raw_entities.get('client_names'):
            client_ids = await self.client_normalizer.normalize(
                raw_entities['client_names'],
                user_context['accessible_clients']
            )
            normalized['client_ids'] = client_ids
            log.append({
                'field': 'client_names',
                'from': raw_entities['client_names'],
                'to': client_ids,
                'method': 'database_lookup'
            })
        
        # Normalize dates
        if raw_entities.get('date_expressions'):
            date_range = self.date_normalizer.normalize(
                raw_entities['date_expressions']
            )
            normalized['date_range'] = date_range
        
        # Normalize statuses
        if raw_entities.get('statuses'):
            status_filters = self.status_normalizer.normalize(
                raw_entities['statuses']
            )
            normalized['status_filters'] = status_filters
        
        # Add user security context
        normalized['accessible_clients'] = user_context['accessible_clients']
        
        return {
            'normalized_entities': normalized,
            'normalization_log': log,
            'database_queries_executed': len([l for l in log if l['method'] == 'database_lookup'])
        }
```

---

## Step 5: Template Parameter Extraction

### Files to Create
| File | Purpose |
|------|---------|
| `step5_parameter_extraction.py` | Template-specific param extractor |
| `prompts/param_extraction/client_level.txt` | CLIENT_LEVEL params prompt |
| `prompts/param_extraction/participant_level.txt` | PARTICIPANT_LEVEL params prompt |
| `prompts/param_extraction/vesting_schedule.txt` | VESTING_SCHEDULE params prompt |
| `tests/test_step5.py` | Unit tests |

### Process Flow
1. Receive query type and normalized entities
2. Load appropriate prompt template for query type
3. Call LLM to extract template-specific parameters
4. Validate parameters against template requirements
5. Return parameters ready for template population

### Sample Input
```json
{
  "query_type": "CLIENT_LEVEL",
  "corrected_query": "Give me LIST of companies with participant count and plan count",
  "normalized_entities": {
    "status_filters": {"participant_status": "active", "plan_status": "active"},
    "accessible_clients": [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
  }
}
```

### Sample Output
```json
{
  "template_parameters": {
    "aggregation_only": false,
    "metrics": ["participant_count", "plan_count"],
    "display_fields": ["c.id", "c.name", "c.industry"],
    "joins_needed": ["participants", "plans"],
    "filters": {
      "participant_status": "active",
      "plan_status": "active"
    },
    "grouping": "GROUP BY c.id, c.name, c.industry",
    "ordering": "ORDER BY participant_count DESC",
    "limit": 100,
    "include_zero_counts": true
  },
  "reasoning": "Query requests company list with aggregated metrics. Not aggregate-only since user wants to see individual companies.",
  "processing_time_ms": 420
}
```

### Code Sample: `step5_parameter_extraction.py`
```python
class TemplateParameterExtractor:
    PROMPTS = {
        'CLIENT_LEVEL': 'prompts/param_extraction/client_level.txt',
        'PARTICIPANT_LEVEL': 'prompts/param_extraction/participant_level.txt',
        'VESTING_SCHEDULE': 'prompts/param_extraction/vesting_schedule.txt'
    }
    
    async def execute(self, query_type: str, corrected_query: str, 
                     normalized_entities: Dict) -> Dict:
        
        prompt_file = self.PROMPTS.get(query_type)
        if not prompt_file:
            raise ValueError(f"No prompt template for query type: {query_type}")
        
        with open(prompt_file, 'r') as f:
            prompt_template = f.read()
        
        prompt = prompt_template.format(
            query=corrected_query,
            entities=json.dumps(normalized_entities, indent=2)
        )
        
        response = await self.llm.call(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )
        
        params = json.loads(response['choices'][0]['message']['content'])
        
        # Validate parameters
        self._validate_parameters(query_type, params)
        
        return {
            'template_parameters': params,
            'reasoning': params.pop('reasoning', 'No reasoning provided')
        }
```

---

## Step 6: Template Population

### Files to Create
| File | Purpose |
|------|---------|
| `step6_template_population.py` | SQL template populator |
| `templates/client_level.sql` | CLIENT_LEVEL SQL template |
| `templates/participant_level.sql` | PARTICIPANT_LEVEL template |
| `templates/vesting_schedule.sql` | VESTING_SCHEDULE template |
| `builders/metric_builder.py` | Builds metric SQL clauses |
| `builders/join_builder.py` | Builds JOIN clauses |
| `builders/filter_builder.py` | Builds WHERE clauses |
| `tests/test_step6.py` | Unit tests |

### Process Flow
1. Receive query type and template parameters
2. Load SQL template for query type
3. Build metric clauses from parameters
4. Build JOIN clauses based on needed tables
5. Build WHERE clauses from filters
6. Populate template with all components
7. Return complete SQL query

### Sample Input
```json
{
  "query_type": "CLIENT_LEVEL",
  "template_parameters": {
    "metrics": ["participant_count", "plan_count"],
    "joins_needed": ["participants", "plans"],
    "filters": {"participant_status": "active"},
    "grouping": "GROUP BY c.id, c.name",
    "ordering": "ORDER BY participant_count DESC",
    "limit": 100
  },
  "normalized_entities": {
    "accessible_clients": [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
  }
}
```

### Sample Output
```json
{
  "sql": "SELECT \n    c.id,\n    c.name,\n    COUNT(DISTINCT p.id) as participant_count,\n    COUNT(DISTINCT pl.id) as plan_count\nFROM clients c\nLEFT JOIN participants p ON c.id = p.client_id AND p.status = 'active'\nLEFT JOIN plans pl ON c.id = pl.client_id AND pl.status = 'active'\nWHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101)\nGROUP BY c.id, c.name\nORDER BY participant_count DESC\nLIMIT 100",
  "sql_formatted": "-- CLIENT_LEVEL Query\nSELECT \n    c.id,\n    c.name,\n    COUNT(DISTINCT p.id) as participant_count,\n    COUNT(DISTINCT pl.id) as plan_count\nFROM clients c\nLEFT JOIN participants p \n    ON c.id = p.client_id \n    AND p.status = 'active'\nLEFT JOIN plans pl \n    ON c.id = pl.client_id \n    AND pl.status = 'active'\nWHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101)\nGROUP BY c.id, c.name\nORDER BY participant_count DESC\nLIMIT 100;",
  "template_used": "CLIENT_LEVEL",
  "components": {
    "metrics": "COUNT(DISTINCT p.id) as participant_count, COUNT(DISTINCT pl.id) as plan_count",
    "joins": "LEFT JOIN participants p..., LEFT JOIN plans pl...",
    "filters": "WHERE c.id IN (...) AND p.status = 'active' AND pl.status = 'active'",
    "grouping": "GROUP BY c.id, c.name",
    "ordering": "ORDER BY participant_count DESC"
  },
  "processing_time_ms": 60
}
```

### Code Sample: `step6_template_population.py`
```python
from builders import MetricBuilder, JoinBuilder, FilterBuilder

class TemplatePopulationStep:
    def __init__(self):
        self.metric_builder = MetricBuilder()
        self.join_builder = JoinBuilder()
        self.filter_builder = FilterBuilder()
    
    def execute(self, query_type: str, template_params: Dict, 
                normalized_entities: Dict) -> Dict:
        
        # Load template
        template = self._load_template(query_type)
        
        # Build components
        metrics = self.metric_builder.build(template_params['metrics'])
        joins = self.join_builder.build(
            template_params['joins_needed'],
            template_params.get('filters', {})
        )
        filters = self.filter_builder.build(
            normalized_entities,
            template_params.get('filters', {})
        )
        
        # Populate template
        sql = template.format(
            metrics=metrics,
            joins=joins,
            filters=filters,
            accessible_clients=','.join(map(str, normalized_entities['accessible_clients'])),
            grouping=template_params.get('grouping', ''),
            ordering=template_params.get('ordering', ''),
            limit=template_params.get('limit', 100)
        )
        
        return {
            'sql': sql,
            'sql_formatted': self._format_sql(sql),
            'template_used': query_type,
            'components': {
                'metrics': metrics,
                'joins': joins,
                'filters': filters
            }
        }
```

---

## Step 7: Security Validation

### Files to Create
| File | Purpose |
|------|---------|
| `step7_security_validation.py` | Security validator |
| `security/rls_validator.py` | Row-level security checker |
| `security/sql_injection_detector.py` | SQL injection detector |
| `security/audit_logger.py` | Audit trail logger |
| `tests/test_step7.py` | Unit tests |

### Process Flow
1. Receive generated SQL and user context
2. Validate SQL contains security WHERE clauses
3. Check for SQL injection patterns
4. Verify user access to requested clients
5. Log audit trail
6. Return validated SQL or security errors

### Sample Input
```json
{
  "sql": "SELECT c.id, c.name, COUNT(DISTINCT p.id) as participant_count FROM clients c LEFT JOIN participants p ON c.id = p.client_id WHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101) GROUP BY c.id, c.name",
  "user_context": {
    "user_id": "user_123",
    "role": "plan_manager",
    "accessible_clients": [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
  },
  "query_metadata": {
    "query_type": "CLIENT_LEVEL",
    "original_query": "Give me list of companies with participant count"
  }
}
```

### Sample Output
```json
{
  "validated": true,
  "security_checks": {
    "rls_applied": true,
    "client_filter_present": true,
    "sql_injection_risk": false,
    "unauthorized_access": false
  },
  "audit_entry": {
    "audit_id": "audit_789",
    "user_id": "user_123",
    "timestamp": "2025-09-30T20:15:32.123Z",
    "query_type": "CLIENT_LEVEL",
    "sql_hash": "a7b3c9d2e1f4567890abcdef12345678",
    "filters_applied": ["client_id IN (...)"],
    "status": "approved"
  },
  "warnings": [],
  "sql": "SELECT c.id, c.name, COUNT(DISTINCT p.id) as participant_count FROM clients c LEFT JOIN participants p ON c.id = p.client_id WHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101) GROUP BY c.id, c.name",
  "processing_time_ms": 95
}
```

### Code Sample: `step7_security_validation.py`
```python
from security import RLSValidator, SQLInjectionDetector, AuditLogger

class SecurityValidationStep:
    def __init__(self, db_connection):
        self.rls_validator = RLSValidator()
        self.sql_detector = SQLInjectionDetector()
        self.audit_logger = AuditLogger(db_connection)
    
    async def execute(self, sql: str, user_context: Dict, 
                     query_metadata: Dict) -> Dict:
        
        validation_result = {
            'validated': True,
            'security_checks': {},
            'warnings': []
        }
        
        # Check 1: RLS applied?
        rls_check = self.rls_validator.validate(sql, user_context)
        validation_result['security_checks']['rls_applied'] = rls_check['passed']
        
        if not rls_check['passed']:
            validation_result['validated'] = False
            validation_result['warnings'].append(rls_check['message'])
        
        # Check 2: SQL injection risk?
        injection_check = self.sql_detector.detect(sql)
        validation_result['security_checks']['sql_injection_risk'] = injection_check['detected']
        
        if injection_check['detected']:
            validation_result['validated'] = False
            validation_result['warnings'].append(f"SQL injection risk: {injection_check['pattern']}")
        
        # Check 3: Unauthorized access?
        # Validate all client IDs in query are in user's accessible_clients
        
        # Log audit trail
        audit_entry = await self.audit_logger.log(
            user_id=user_context['user_id'],
            query_type=query_metadata['query_type'],
            sql=sql,
            status='approved' if validation_result['validated'] else 'blocked'
        )
        
        validation_result['audit_entry'] = audit_entry
        validation_result['sql'] = sql if validation_result['validated'] else None
        
        return validation_result
```

---

## Step 8: Query Execution

### Files to Create
| File | Purpose |
|------|---------|
| `step8_execution.py` | Database query executor |
| `db/connection_pool.py` | DB connection pool manager |
| `db/query_optimizer.py` | Query performance optimizer |
| `tests/test_step8.py` | Unit tests |

### Process Flow
1. Receive validated SQL
2. Get DB connection from pool
3. Execute query with timeout
4. Fetch results
5. Log execution metrics
6. Return result set

### Sample Input
```json
{
  "sql": "SELECT c.id, c.name, COUNT(DISTINCT p.id) as participant_count, COUNT(DISTINCT pl.id) as plan_count FROM clients c LEFT JOIN participants p ON c.id = p.client_id AND p.status = 'active' LEFT JOIN plans pl ON c.id = pl.client_id WHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101) GROUP BY c.id, c.name ORDER BY participant_count DESC LIMIT 100",
  "execution_params": {
    "timeout_seconds": 30,
    "max_rows": 1000
  }
}
```

### Sample Output
```json
{
  "success": true,
  "row_count": 15,
  "execution_time_ms": 342,
  "columns": ["id", "name", "participant_count", "plan_count"],
  "results": [
    {
      "id": 1,
      "name": "TechCorp Inc",
      "participant_count": 2847,
      "plan_count": 5
    },
    {
      "id": 5,
      "name": "Global Innovations",
      "participant_count": 1653,
      "plan_count": 4
    },
    {
      "id": 12,
      "name": "Startup Ventures",
      "participant_count": 892,
      "plan_count": 3
    },
    {
      "id": 18,
      "name": "Enterprise Solutions",
      "participant_count": 745,
      "plan_count": 2
    },
    {
      "id": 23,
      "name": "Digital Dynamics",
      "participant_count": 524,
      "plan_count": 3
    }
  ],
  "query_plan": {
    "planning_time": "0.234 ms",
    "execution_time": "342.156 ms",
    "total_cost": 1245.67,
    "rows_examined": 15234
  },
  "warnings": []
}
```

### Code Sample: `step8_execution.py`
```python
import asyncpg
from db import ConnectionPool

class QueryExecutionStep:
    def __init__(self, connection_pool: ConnectionPool):
        self.pool = connection_pool
    
    async def execute(self, sql: str, timeout_seconds: int = 30) -> Dict:
        start_time = time.time()
        
        async with self.pool.acquire() as conn:
            try:
                # Set statement timeout
                await conn.execute(f"SET statement_timeout = {timeout_seconds * 1000}")
                
                # Execute query
                results = await conn.fetch(sql)
                
                # Get query plan for metrics
                explain_results = await conn.fetch(f"EXPLAIN (FORMAT JSON) {sql}")
                query_plan = json.loads(explain_results[0]['QUERY PLAN'])[0]['Plan']
                
                execution_time = (time.time() - start_time) * 1000
                
                return {
                    'success': True,
                    'row_count': len(results),
                    'execution_time_ms': round(execution_time, 2),
                    'columns': list(results[0].keys()) if results else [],
                    'results': [dict(row) for row in results],
                    'query_plan': self._parse_query_plan(query_plan),
                    'warnings': []
                }
                
            except asyncpg.exceptions.QueryCanceledError:
                return {
                    'success': False,
                    'error': 'Query timeout exceeded',
                    'timeout_seconds': timeout_seconds
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
```

---

## Step 9: Response Formatting

### Files to Create
| File | Purpose |
|------|---------|
| `step9_response_formatting.py` | Response formatter |
| `prompts/response_formatting_prompt.txt` | Formatting prompt |
| `formatters/table_formatter.py` | Markdown table generator |
| `formatters/insight_generator.py` | Insight generator |
| `tests/test_step9.py` | Unit tests |

### Process Flow
1. Receive query results and original query
2. Call LLM to generate natural language response
3. Format data as markdown tables if needed
4. Generate insights and summaries
5. Add follow-up suggestions
6. Return formatted response

### Sample Input
```json
{
  "original_query": "Give me list of companies with participant count and plan count",
  "query_type": "CLIENT_LEVEL",
  "results": [
    {"id": 1, "name": "TechCorp Inc", "participant_count": 2847, "plan_count": 5},
    {"id": 5, "name": "Global Innovations", "participant_count": 1653, "plan_count": 4},
    {"id": 12, "name": "Startup Ventures", "participant_count": 892, "plan_count": 3}
  ],
  "row_count": 15,
  "execution_time_ms": 342
}
```

### Sample Output
```json
{
  "response_text": "I found **15 companies** in your portfolio. Here's the breakdown:\n\n**Summary Statistics:**\n- Total participants: 12,847\n- Total plans: 52\n- Average participants per company: 856\n- Average plans per company: 3.5\n\n**Top 5 Companies:**\n\n| Company | Participants | Plans |\n|---------|-------------|-------|\n| TechCorp Inc | 2,847 | 5 |\n| Global Innovations | 1,653 | 4 |\n| Startup Ventures | 892 | 3 |\n| Enterprise Solutions | 745 | 2 |\n| Digital Dynamics | 524 | 3 |\n\n*... and 10 more companies*\n\n**Key Insights:**\n- TechCorp Inc has the most participants (2,847)\n- Most companies have 2-5 equity plans\n- 3 companies have no active participants\n\n**Would you like to:**\n- See the complete list of all 15 companies?\n- Filter by specific plan types or regions?\n- View participant breakdown by department?",
  "formatted_data": {
    "summary": {
      "total_companies": 15,
      "total_participants": 12847,
      "total_plans": 52,
      "avg_participants": 856,
      "avg_plans": 3.5
    },
    "table": "| Company | Participants | Plans |\n|---------|-------------|-------|\n| TechCorp Inc | 2,847 | 5 |...",
    "insights": [
      "TechCorp Inc has the most participants with 2,847 active employees",
      "Most companies maintain between 2-5 different equity plans"
    ]
  },
  "follow_up_suggestions": [
    "Show complete list of all 15 companies",
    "Break down by plan type (RSU vs ISO vs NSO)",
    "View geographic distribution"
  ],
  "processing_time_ms": 580
}
```

### Code Sample: `step9_response_formatting.py`
```python
from formatters import TableFormatter, InsightGenerator

class ResponseFormattingStep:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.table_formatter = TableFormatter()
        self.insight_generator = InsightGenerator()
    
    async def execute(self, original_query: str, results: List[Dict], 
                     query_type: str) -> Dict:
        
        # Generate summary statistics
        summary = self._generate_summary(results, query_type)
        
        # Format as table if multiple rows
        table = None
        if len(results) > 1:
            table = self.table_formatter.format(results, max_rows=10)
        
        # Generate insights
        insights = self.insight_generator.generate(results, query_type)
        
        # Call LLM to create natural language response
        prompt = self._build_formatting_prompt(
            original_query=original_query,
            summary=summary,
            sample_results=results[:10],
            insights=insights
        )
        
        response = await self.llm.call(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        
        response_text = response['choices'][0]['message']['content']
        
        # Generate follow-up suggestions
        follow_ups = self._generate_follow_ups(query_type, results)
        
        return {
            'response_text': response_text,
            'formatted_data': {
                'summary': summary,
                'table': table,
                'insights': insights
            },
            'follow_up_suggestions': follow_ups
        }
```

---

## Main Orchestrator

### Files to Create
| File | Purpose |
|------|---------|
| `orchestrator.py` | Main pipeline orchestrator |
| `context.py` | QueryContext data class |
| `config.py` | Configuration management |
| `exceptions.py` | Custom exception classes |

### Code Sample: `orchestrator.py`
```python
from dataclasses import dataclass
from typing import Optional, Dict, List
import time

@dataclass
class QueryContext:
    # Step 1
    original_query: str
    corrected_query: Optional[str] = None
    intent: Optional[str] = None
    query_category: Optional[str] = None
    complexity: Optional[str] = None
    
    # Step 2
    query_type: Optional[str] = None
    
    # Step 3
    raw_entities: Optional[Dict] = None
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    
    # Step 4
    normalized_entities: Optional[Dict] = None
    
    # Step 5
    template_parameters: Optional[Dict] = None
    
    # Step 6
    sql: Optional[str] = None
    
    # Step 7
    security_validated: bool = False
    
    # Step 8
    results: Optional[List[Dict]] = None
    
    # Step 9
    response: Optional[str] = None
    
    # Metadata
    processing_times: Dict = None
    total_cost: float = 0.0

class EquityChatbotOrchestrator:
    def __init__(self, config):
        self.step1 = QueryUnderstandingStep(config.llm_client)
        self.step2 = QueryTypeClassifier(config.llm_client)
        self.step3 = EntityExtractionStep(config.llm_client)
        self.step4 = EntityNormalizationStep(config.db)
        self.step5 = TemplateParameterExtractor(config.llm_client)
        self.step6 = TemplatePopulationStep()
        self.step7 = SecurityValidationStep(config.db)
        self.step8 = QueryExecutionStep(config.db_pool)
        self.step9 = ResponseFormattingStep(config.llm_client)
    
    async def process(self, user_query: str, user_context: Dict) -> Dict:
        context = QueryContext(
            original_query=user_query,
            processing_times={}
        )
        
        try:
            # Step 1: Understanding
            start = time.time()
            understanding = await self.step1.execute(user_query)
            context.processing_times['step1'] = time.time() - start
            
            context.corrected_query = understanding.corrected_query
            context.intent = understanding.intent
            context.query_category = understanding.query_category
            context.complexity = understanding.complexity
            
            # Step 2: Classification
            start = time.time()
            classification = await self.step2.execute(
                context.corrected_query,
                context.query_category
            )
            context.processing_times['step2'] = time.time() - start
            
            context.query_type = classification['query_type']
            
            # Step 3: Entity Extraction
            start = time.time()
            entities = await self.step3.execute(context.corrected_query)
            context.processing_times['step3'] = time.time() - start
            
            context.raw_entities = entities
            
            # Check for clarification
            if entities.get('needs_clarification'):
                context.needs_clarification = True
                context.clarification_prompt = entities.get('clarification_prompt')
                
                return {
                    'type': 'clarification_needed',
                    'prompt': context.clarification_prompt,
                    'context': context
                }
            
            # Step 4: Normalization
            start = time.time()
            normalized = await self.step4.execute(
                context.raw_entities,
                user_context
            )
            context.processing_times['step4'] = time.time() - start
            
            context.normalized_entities = normalized['normalized_entities']
            
            # Step 5: Parameter Extraction
            start = time.time()
            params = await self.step5.execute(
                context.query_type,
                context.corrected_query,
                context.normalized_entities
            )
            context.processing_times['step5'] = time.time() - start
            
            context.template_parameters = params['template_parameters']
            
            # Step 6: Template Population
            start = time.time()
            sql_result = self.step6.execute(
                context.query_type,
                context.template_parameters,
                context.normalized_entities
            )
            context.processing_times['step6'] = time.time() - start
            
            context.sql = sql_result['sql']
            
            # Step 7: Security Validation
            start = time.time()
            validation = await self.step7.execute(
                context.sql,
                user_context,
                {'query_type': context.query_type}
            )
            context.processing_times['step7'] = time.time() - start
            
            if not validation['validated']:
                return {
                    'type': 'security_error',
                    'errors': validation['warnings']
                }
            
            context.security_validated = True
            
            # Step 8: Execution
            start = time.time()
            execution = await self.step8.execute(context.sql)
            context.processing_times['step8'] = time.time() - start
            
            if not execution['success']:
                return {
                    'type': 'execution_error',
                    'error': execution['error']
                }
            
            context.results = execution['results']
            
            # Step 9: Response Formatting
            start = time.time()
            response = await self.step9.execute(
                context.original_query,
                context.results,
                context.query_type
            )
            context.processing_times['step9'] = time.time() - start
            
            context.response = response['response_text']
            
            # Calculate totals
            total_time = sum(context.processing_times.values())
            
            return {
                'type': 'success',
                'response': context.response,
                'results': context.results,
                'metadata': {
                    'query_type': context.query_type,
                    'total_time_ms': round(total_time * 1000, 2),
                    'processing_times': {
                        k: round(v * 1000, 2) 
                        for k, v in context.processing_times.items()
                    },
                    'sql': context.sql
                }
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'error': str(e),
                'context': context
            }
```

---

## Directory Structure

```
equity-chatbot/
├── orchestrator.py
├── context.py
├── config.py
├── exceptions.py
├── requirements.txt
├── README.md
│
├── steps/
│   ├── __init__.py
│   ├── step1_understanding.py
│   ├── step2_classification.py
│   ├── step3_entity_extraction.py
│   ├── step4_normalization.py
│   ├── step5_parameter_extraction.py
│   ├── step6_template_population.py
│   ├── step7_security_validation.py
│   ├── step8_execution.py
│   └── step9_response_formatting.py
│
├── prompts/
│   ├── understanding_prompt.txt
│   ├── classification_prompt.txt
│   ├── entity_extraction_prompt.txt
│   ├── response_formatting_prompt.txt
│   └── param_extraction/
│       ├── client_level.txt
│       ├── participant_level.txt
│       └── vesting_schedule.txt
│
├── templates/
│   ├── client_level.sql
│   ├── participant_level.sql
│   ├── vesting_schedule.sql
│   ├── regional.sql
│   ├── financial_metrics.sql
│   └── compliance_audit.sql
│
├── builders/
│   ├── __init__.py
│   ├── metric_builder.py
│   ├── join_builder.py
│   └── filter_builder.py
│
├── normalizers/
│   ├── __init__.py
│   ├── client_normalizer.py
│   ├── participant_normalizer.py
│   ├── date_normalizer.py
│   └── status_normalizer.py
│
├── formatters/
│   ├── __init__.py
│   ├── table_formatter.py
│   └── insight_generator.py
│
├── security/
│   ├── __init__.py
│   ├── rls_validator.py
│   ├── sql_injection_detector.py
│   └── audit_logger.py
│
├── utils/
│   ├── __init__.py
│   └── entity_level_detector.py
│
├── db/
│   ├── __init__.py
│   ├── connection_pool.py
│   └── query_optimizer.py
│
├── config/
│   ├── query_types.yaml
│   └── entity_indicators.yaml
│
└── tests/
    ├── test_step1.py
    ├── test_step2.py
    ├── test_step3.py
    ├── test_step4.py
    ├── test_step5.py
    ├── test_step6.py
    ├── test_step7.py
    ├── test_step8.py
    └── test_step9.py
```

---

## Summary Table

| Step | Key Files | Input Sample | Output Sample | Process Time |
|------|-----------|--------------|---------------|--------------|
| 1. Understanding | `step1_understanding.py` | `"Give me this of companies..."` | `corrected_query, intent, category` | ~320ms |
| 2. Classification | `step2_classification.py` | `corrected_query, category` | `query_type: "CLIENT_LEVEL"` | ~180ms |
| 3. Entity Extraction | `step3_entity_extraction.py` | `corrected_query` | `entities, needs_clarification` | ~450ms |
| 4. Normalization | `step4_normalization.py` | `raw_entities, user_context` | `normalized_entities with IDs` | ~150ms |
| 5. Param Extraction | `step5_parameter_extraction.py` | `query_type, normalized_entities` | `template_parameters` | ~420ms |
| 6. Template Population | `step6_template_population.py` | `query_type, parameters` | `complete SQL query` | ~60ms |
| 7. Security Validation | `step7_security_validation.py` | `sql, user_context` | `validated: true, audit_entry` | ~95ms |
| 8. Query Execution | `step8_execution.py` | `validated SQL` | `results: 15 rows` | ~342ms |
| 9. Response Formatting | `step9_response_formatting.py` | `results, original_query` | `natural language response` | ~580ms |
| **TOTAL** | | | | **~2.6s** |
