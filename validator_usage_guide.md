# Schema Auto-Generator & SQL Validator - Usage Guide

## Installation

```bash
pip install asyncpg pyyaml sqlglot
```

## Part 1: Auto-Generate YAML Files from PostgreSQL

### Quick Start

```python
import asyncio
from schema_generator_validator import PostgresSchemaExtractor, YAMLConfigGenerator

async def generate_configs():
    # Your database connection
    connection_string = "postgresql://user:password@localhost:5432/equity_db"
    
    # Initialize
    extractor = PostgresSchemaExtractor(connection_string)
    generator = YAMLConfigGenerator(extractor)
    
    try:
        await extractor.connect()
        
        # Generate all 4 YAML files
        await generator.generate_all_configs(output_dir='config')
        
        print("✓ Generated:")
        print("  - config/database_schema.yaml")
        print("  - config/entity_schema.yaml")
        print("  - config/metrics_schema.yaml")
        print("  - config/business_vocabulary.yaml")
        
    finally:
        await extractor.disconnect()

# Run it
asyncio.run(generate_configs())
```

### What Gets Generated

#### `config/database_schema.yaml`
```yaml
tables:
  clients:
    columns:
      id:
        type: integer
        primary_key: true
        nullable: false
      name:
        type: character varying
        nullable: false
        max_length: 255
      industry:
        type: character varying
        max_length: 100
    indexes:
      - name: idx_clients_name
        columns: [name]
        unique: false
        type: btree
    foreign_keys: []

  participants:
    columns:
      id:
        type: integer
        primary_key: true
      client_id:
        type: integer
        foreign_key: clients.id
        nullable: false
      name:
        type: character varying
        nullable: false
      status:
        type: character varying
        default: 'active'
    indexes:
      - name: idx_participants_client
        columns: [client_id]
    foreign_keys:
      - column: client_id
        references: clients(id)
        on_delete: RESTRICT
        on_update: CASCADE
```

#### `config/entity_schema.yaml`
```yaml
entity_types:
  clients:
    description: Companies/organizations in the system
    attributes: [name, industry, country, legal_entity, status]
    can_filter_by: [name, industry, country]
    
  participants:
    description: Employees receiving equity compensation
    attributes: [employee_id, name, email, department, country, status]
    can_filter_by: [name, department, country, status]
    belongs_to: clients

relationships:
  - clients have many participants
  - clients have many plans
  - participants have many grants
```

## Part 2: Validate SQL with SQLGlot

### Basic Validation

```python
from schema_generator_validator import SQLSchemaValidator

# Initialize validator with generated schema
validator = SQLSchemaValidator('config/database_schema.yaml')

# Validate a query
sql = """
    SELECT 
        c.id,
        c.name,
        COUNT(DISTINCT p.id) as participant_count
    FROM clients c
    LEFT JOIN participants p ON c.id = p.client_id
    WHERE c.id IN (1, 5, 12, 18, 23)
    GROUP BY c.id, c.name
"""

result = validator.validate(sql)

if result.valid:
    print("✅ Query is valid!")
else:
    print("❌ Query has errors:")
    for error in result.errors:
        print(f"  {error.error_type}: {error.message}")

if result.warnings:
    print("⚠️  Warnings:")
    for warning in result.warnings:
        print(f"  {warning.error_type}: {warning.message}")
```

### Security Validation

```python
# Validate that query includes proper security filters
sql = """
    SELECT p.name, p.email
    FROM participants p
    WHERE p.department = 'Engineering'
"""

result = validator.validate_security(
    sql=sql,
    accessible_client_ids=[1, 5, 12, 18, 23]
)

if not result.valid:
    print("❌ Security validation failed:")
    for error in result.errors:
        print(f"  {error.message}")
    # Output: Query missing client_id security filter
```

### Index Suggestions

```python
sql = """
    SELECT *
    FROM grants g
    WHERE g.grant_date > '2024-01-01'
      AND g.status = 'active'
"""

suggestions = validator.suggest_indexes(sql)

print("💡 Index suggestions:")
for suggestion in suggestions:
    print(f"  {suggestion}")

# Output:
#   Consider adding index on grants(grant_date) - used in WHERE clause
#   Consider adding index on grants(status) - used in WHERE clause
```

## Integration with Chatbot Pipeline

### Step 6: Validate Generated SQL

```python
# step6_template_population.py

class TemplatePopulationStep:
    def __init__(self):
        self.validator = SQLSchemaValidator('config/database_schema.yaml')
    
    def execute(self, query_type: str, params: Dict, entities: Dict) -> Dict:
        # Generate SQL
        sql = self._populate_template(query_type, params, entities)
        
        # VALIDATE before returning
        validation_result = self.validator.validate(sql)
        
        if not validation_result.valid:
            # Log errors
            for error in validation_result.errors:
                logger.error(f"SQL Validation Error: {error.message}")
            
            raise SQLValidationError(
                f"Generated SQL is invalid: {validation_result.errors[0].message}"
            )
        
        # Check warnings
        if validation_result.warnings:
            for warning in validation_result.warnings:
                logger.warning(f"SQL Warning: {warning.message}")
        
        return {
            'sql': sql,
            'validation': {
                'valid': True,
                'warnings': [w.message for w in validation_result.warnings]
            }
        }
```

### Step 7: Security Validation

```python
# step7_security_validation.py

class SecurityValidationStep:
    def __init__(self):
        self.validator = SQLSchemaValidator('config/database_schema.yaml')
    
    def execute(self, sql: str, user_context: Dict) -> Dict:
        # Validate security
        result = self.validator.validate_security(
            sql=sql,
            accessible_client_ids=user_context['accessible_clients']
        )
        
        if not result.valid:
            return {
                'validated': False,
                'errors': [e.message for e in result.errors]
            }
        
        return {
            'validated': True,
            'warnings': [w.message for w in result.warnings]
        }
```

## Validation Error Types

| Error Type | Severity | Description |
|-----------|----------|-------------|
| `unknown_table` | error | Table doesn't exist in schema |
| `unknown_column` | error | Column doesn't exist in table |
| `missing_join_condition` | warning | JOIN without ON clause |
| `non_fk_join` | info | JOIN not using foreign key |
| `select_star` | info | Using SELECT * |
| `delete_without_where` | warning | DELETE without WHERE |
| `update_without_where` | warning | UPDATE without WHERE |
| `dangerous_operation` | error | DROP TABLE, TRUNCATE, etc. |
| `missing_security_filter` | error | Missing client_id filter |
| `parse_error` | error | SQL syntax error |

## Advanced Usage

### Custom Validation Rules

```python
class CustomSQLValidator(SQLSchemaValidator):
    def validate(self, sql: str) -> ValidationResult:
        # Run base validation
        result = super().validate(sql)
        
        # Add custom rules
        result.errors.extend(self._check_custom_rules(sql))
        
        return result
    
    def _check_custom_rules(self, sql: str) -> List[ValidationError]:
        errors = []
        
        # Example: Require LIMIT on SELECT queries
        parsed = parse_one(sql)
        for select in parsed.find_all(exp.Select):
            if not select.args.get('limit'):
                errors.append(ValidationError(
                    error_type='missing_limit',
                    message="SELECT query should include LIMIT clause",
                    severity='warning'
                ))
        
        return errors
```

### Validate Multiple Queries

```python
def validate_pipeline_queries(queries: Dict[str, str]) -> Dict[str, ValidationResult]:
    """Validate all queries in the pipeline"""
    validator = SQLSchemaValidator('config/database_schema.yaml')
    
    results = {}
    for query_name, sql in queries.items():
        result = validator.validate(sql)
        results[query_name] = result
        
        print(f"\n{query_name}:")
        if result.valid:
            print("  ✅ Valid")
        else:
            print("  ❌ Invalid")
            for error in result.errors:
                print(f"    - {error.message}")
    
    return results

# Usage
queries = {
    'client_level': "SELECT c.id, c.name FROM clients c WHERE c.id IN (1,5,12)",
    'participant_level': "SELECT p.name FROM participants p JOIN clients c ON p.client_id = c.id",
    'vesting_schedule': "SELECT vs.vest_date FROM vesting_schedules vs"
}

results = validate_pipeline_queries(queries)
```

## Testing

### Unit Tests Example

```python
import pytest
from schema_generator_validator import SQLSchemaValidator

@pytest.fixture
def validator():
    return SQLSchemaValidator('config/database_schema.yaml')

def test_valid_query(validator):
    sql = "SELECT id, name FROM clients WHERE id = 1"
    result = validator.validate(sql)
    assert result.valid == True

def test_invalid_table(validator):
    sql = "SELECT * FROM nonexistent_table"
    result = validator.validate(sql)
    assert result.valid == False
    assert any(e.error_type == 'unknown_table' for e in result.errors)

def test_invalid_column(validator):
    sql = "SELECT id, fake_column FROM clients"
    result = validator.validate(sql)
    assert result.valid == False
    assert any(e.error_type == 'unknown_column' for e in result.errors)

def test_missing_security_filter(validator):
    sql = "SELECT * FROM participants"
    result = validator.validate_security(sql, [1, 5, 12])
    assert result.valid == False
    assert any(e.error_type == 'missing_security_filter' for e in result.errors)
```

## Performance Tips

1. **Cache the validator** - Initialize once, reuse for all queries
2. **Validate before execution** - Catch errors early in the pipeline
3. **Use async/await** - Schema extraction is I/O bound
4. **Batch validations** - Validate multiple queries together
5. **Monitor validation times** - Add logging for slow validations

## Troubleshooting

### Schema extraction fails
```python
# Check connection
try:
    await extractor.connect()
    tables = await extractor.get_all_tables()
    print(f"Found {len(tables)} tables")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Validation gives false positives
```python
# Check schema was loaded correctly
validator = SQLSchemaValidator('config/database_schema.yaml')
print(f"Loaded {len(validator.table_names)} tables")
print(f"Tables: {validator.table_names}")
```

### SQLGlot parse errors
```python
# Try different dialects
from sqlglot import parse_one

sql = "SELECT * FROM clients"
try:
    parsed = parse_one(sql, dialect='postgres')
except Exception as e:
    print(f"Parse error: {e}")
    # Try without dialect
    parsed = parse_one(sql)
```

## Best Practices

1. **Regenerate configs after schema changes** - Run generator after migrations
2. **Version control YAML files** - Track schema changes
3. **Validate in CI/CD** - Add validation tests to your pipeline
4. **Monitor validation errors** - Log and alert on validation failures
5. **Document custom rules** - Keep validation rules documented
6. **Test edge cases** - Complex queries, CTEs, subqueries

## Complete Example

```python
import asyncio
from schema_generator_validator import (
    PostgresSchemaExtractor, 
    YAMLConfigGenerator,
    SQLSchemaValidator
)

async def setup_and_validate():
    # 1. Generate schema files (do this once, or after schema changes)
    connection_string = "postgresql://user:password@localhost/equity_db"
    extractor = PostgresSchemaExtractor(connection_string)
    generator = YAMLConfigGenerator(extractor)
    
    await extractor.connect()
    await generator.generate_all_configs()
    await extractor.disconnect()
    
    print("✓ Schema files generated\n")
    
    # 2. Initialize validator
    validator = SQLSchemaValidator('config/database_schema.yaml')
    
    # 3. Validate your chatbot's generated SQL
    sql = """
        SELECT 
            c.id,
            c.name,
            COUNT(DISTINCT p.id) as participant_count,
            COUNT(DISTINCT pl.id) as plan_count
        FROM clients c
        LEFT JOIN participants p ON c.id = p.client_id AND p.status = 'active'
        LEFT JOIN plans pl ON c.id = pl.client_id AND pl.status = 'active'
        WHERE c.id IN (1,5,12,18,23,29,31,44,52,67,71,88,93,99,101)
        GROUP BY c.id, c.name
        ORDER BY participant_count DESC
        LIMIT 100
    """
    
    # Validate structure
    result = validator.validate(sql)
    print(f"Valid: {result.valid}")
    
    # Validate security
    security_result = validator.validate_security(sql, accessible_client_ids=[1,5,12,18,23])
    print(f"Security: {security_result.valid}")
    
    # Get index suggestions
    suggestions = validator.suggest_indexes(sql)
    if suggestions:
        print("Index suggestions:", suggestions)

asyncio.run(setup_and_validate())
```
