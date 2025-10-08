# Complete Project Setup Guide
## Equity Chatbot with Movement Schema Support

---

## Directory Structure

```
equity-chatbot/
│
├── config/                              # Configuration files
│   ├── entity_schema.yaml              # ★ Table definitions
│   ├── metrics_schema.yaml             # ★ Metric calculations
│   ├── business_vocabulary.yaml         # Terminology mappings
│   ├── normalization_rules.yaml         # Data normalization rules
│   └── query_types.yaml                 # Query type definitions
│
├── builders/                            # SQL Builders
│   ├── __init__.py
│   ├── real_movement_calculator.py     # ★ NEW: Movement schema builder
│   ├── metric_builder.py               # Original builder
│   ├── join_builder.py                  # JOIN clause builder
│   └── filter_builder.py                # WHERE clause builder
│
├── steps/                               # Pipeline steps
│   ├── __init__.py
│   ├── step01_combined_processing.py    # ★ Step 0+1 merged
│   ├── step2_classification.py          # Query type classification
│   ├── step3_entity_extraction.py       # Entity extraction
│   ├── step4_normalization.py           # Entity normalization
│   ├── step5_parameter_extraction.py    # Parameter extraction
│   ├── step6_template_population.py     # ★ UPDATED: SQL generation
│   ├── step7_security_validation.py     # Security checks
│   ├── step8_execution.py               # Query execution
│   └── step9_response_formatting.py     # Response formatting
│
├── storage/                             # Chat history storage
│   ├── __init__.py
│   ├── chat_history.py                  # History manager
│   └── conversation_context.py          # Context extractor
│
├── prompts/                             # LLM prompts
│   ├── combined_processing_prompt.txt   # ★ Step 0+1 prompt
│   ├── classification_prompt.txt        # Step 2 prompt
│   ├── entity_extraction_prompt.txt     # Step 3 prompt
│   ├── response_formatting_prompt.txt   # Step 9 prompt
│   └── param_extraction/                # Step 5 prompts by query type
│       ├── client_level.txt
│       ├── participant_level.txt
│       └── vesting_schedule.txt
│
├── security/                            # Security modules
│   ├── __init__.py
│   ├── rls_validator.py                 # Row-level security
│   ├── sql_injection_detector.py        # SQL injection detection
│   └── audit_logger.py                  # Audit logging
│
├── tests/                               # Unit tests
│   ├── test_real_movement_calculator.py # ★ Movement calculator tests
│   ├── test_step01.py
│   ├── test_step2.py
│   ├── test_step3.py
│   ├── test_step4.py
│   ├── test_step5.py
│   ├── test_step6.py                   # ★ UPDATED
│   ├── test_step7.py
│   ├── test_step8.py
│   └── test_step9.py
│
├── docs/                                # Documentation
│   ├── shares_info_guide.md            # ★ Balance types reference
│   ├── movement_schema.md               # ★ Schema documentation
│   └── api_reference.md                 # API documentation
│
├── orchestrator.py                      # ★ UPDATED: Main pipeline
├── context.py                           # QueryContext data class
├── config.py                            # Configuration management
├── exceptions.py                        # Custom exceptions
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment variables template
└── README.md                            # Project README
```

---

## Installation Steps

### 1. Prerequisites

```bash
# Python 3.9+
python --version

# PostgreSQL 13+
psql --version

# Git
git --version
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd equity-chatbot
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
# LLM
openai>=1.0.0
anthropic>=0.7.0

# Database
asyncpg>=0.29.0
psycopg2-binary>=2.9.9

# Data Processing
pandas>=2.1.0
numpy>=1.24.0
pyyaml>=6.0

# SQL
sqlparse>=0.4.4
sqlglot>=20.0.0

# Web Framework (if building API)
fastapi>=0.104.0
uvicorn>=0.24.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.4.0
```

### 5. Configure Environment

```bash
cp .env.example .env
nano .env
```

**.env**:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/equity_db
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20

# LLM API
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0.1

# Configuration
CONFIG_PATH=config
SCHEMA_TYPE=movement  # 'movement' or 'traditional'

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/equity_chatbot.log
```

### 6. Set Up Database

```bash
# Create database
createdb equity_db

# Run migrations (if using)
alembic upgrade head

# Or load schema directly
psql equity_db < schema/bi_fact_movement_schema.sql
```

**schema/bi_fact_movement_schema.sql** (simplified):
```sql
-- Tables for movement-based schema

CREATE TABLE bi_fact_movement (
    movement_hub_key VARCHAR(50) PRIMARY KEY,
    participant_hub_key VARCHAR(50) NOT NULL,
    grant_award_hub_key VARCHAR(50) NOT NULL,
    client_hub_key VARCHAR(50) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    movement_sub_type VARCHAR(50),
    movement_sub_sub_type VARCHAR(50),
    share_units DECIMAL(15,4) NOT NULL,
    movement_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fm_participant ON bi_fact_movement(participant_hub_key);
CREATE INDEX idx_fm_client ON bi_fact_movement(client_hub_key);
CREATE INDEX idx_fm_movement_type ON bi_fact_movement(movement_type, movement_sub_type, movement_sub_sub_type);

CREATE TABLE bi_movement_balance_mapping (
    movement_balance_mapping_key VARCHAR(50) PRIMARY KEY,
    movement_type VARCHAR(50) NOT NULL,
    movement_sub_type VARCHAR(50),
    movement_sub_sub_type VARCHAR(50),
    granted DECIMAL(5,2),
    unveiled DECIMAL(5,2),
    vested DECIMAL(5,2),
    exercisable DECIMAL(5,2),
    exercised DECIMAL(5,2),
    forfeited DECIMAL(5,2),
    outstanding DECIMAL(5,2),
    -- Add other balance columns...
    UNIQUE(movement_type, movement_sub_type, movement_sub_sub_type)
);

CREATE TABLE bi_participant_detail (
    participant_hub_key VARCHAR(50) NOT NULL,
    participant_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    department VARCHAR(100),
    country VARCHAR(100),
    is_latest VARCHAR(2) DEFAULT 'b1',
    employment_status VARCHAR(50),
    PRIMARY KEY (participant_hub_key, is_latest)
);

CREATE TABLE bi_grant_award_latest (
    grant_award_hub_key VARCHAR(50) PRIMARY KEY,
    participant_hub_key VARCHAR(50) NOT NULL,
    grant_date DATE NOT NULL,
    plan_type VARCHAR(50),
    retirement_eligibility_dt DATE
);

CREATE TABLE conversation_turns (
    turn_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_query TEXT NOT NULL,
    rephrased_query TEXT,
    was_rephrased BOOLEAN DEFAULT FALSE,
    query_type VARCHAR(50),
    entities_mentioned JSONB,
    response TEXT,
    results_summary JSONB
);
```

### 7. Load Sample Data

```bash
# Load movement balance mapping
psql equity_db < data/movement_balance_mapping.sql

# Load sample participants
psql equity_db < data/sample_participants.sql

# Load sample movements
psql equity_db < data/sample_movements.sql
```

### 8. Configure Schema Files

Edit `config/entity_schema.yaml` to match your database:

```yaml
# Verify table names match your database
tables:
  bi_fact_movement:
    table_name: "bi_fact_movement"  # ← Must match DB table name
    # ...
  
  bi_movement_balance_mapping:
    table_name: "bi_movement_balance_mapping"  # ← Must match DB table name
    # ...
```

---

## Quick Start

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_real_movement_calculator.py -v

# Run with coverage
pytest --cov=builders --cov-report=html
```

### Test Integration

```python
# test_integration.py
import asyncio
from orchestrator import EquityChatbotOrchestrator
from config import Config

async def test_complete_flow():
    # Initialize
    config = Config()
    orchestrator = EquityChatbotOrchestrator(config)
    
    # User context
    user_context = {
        'user_id': 'user_123',
        'client_hub_key': 'CLNT00000000000000000002',
        'accessible_client_keys': ['CLNT00000000000000000002']
    }
    
    # Test query
    result = await orchestrator.process(
        user_query="How many unveiled shares does John Smith have?",
        user_context=user_context,
        session_id="session_456"
    )
    
    print("Result:", result)
    assert result['type'] == 'success'
    assert 'unveiled_shares' in result['response']

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
```

Run it:
```bash
python test_integration.py
```

---

## Usage Examples

### Example 1: Simple Query

```python
from orchestrator import EquityChatbotOrchestrator

orchestrator = EquityChatbotOrchestrator(config)

result = await orchestrator.process(
    user_query="How many unveiled shares does John have?",
    user_context={'client_hub_key': 'CLNT00000000000000000002'},
    session_id="session_123"
)

print(result['response'])
# Output: "John Smith has 5,000 unveiled shares."
```

### Example 2: Using RealMovementCalculator Directly

```python
from builders.real_movement_calculator import RealMovementCalculator, MovementFilter

# Initialize
calc = RealMovementCalculator(config_path='config')

# Build filter
filters = MovementFilter(
    participant_hub_key='PRT00000000000000000042',
    client_hub_key='CLNT00000000000000000002'
)

# Generate SQL
sql = calc.build_unvested_shares_sql(filters)
print(sql)

# Execute (using your DB connection)
result = await db.fetchrow(sql)
print(f"Unveiled shares: {result['unveiled_shares']}")
```

### Example 3: Multiple Balance Types

```python
# Generate multi-balance query
sql = calc.build_multi_balance_sql(
    balance_types_list=['unveiled', 'vested', 'granted'],
    filters=filters,
    group_by_participant=False  # Company-wide aggregate
)

result = await db.fetchrow(sql)
print(f"""
Unveiled: {result['unveiled_shares']}
Vested:   {result['vested_shares']}
Granted:  {result['granted_shares']}
""")
```

---

## Configuration

### Switching Schema Types

To switch between movement and traditional schemas:

**Option 1: Environment Variable**
```bash
# .env
SCHEMA_TYPE=movement  # or 'traditional'
```

**Option 2: Config File**
```python
# config.py
class Config:
    SCHEMA_TYPE = 'movement'  # or 'traditional'
```

**Option 3: Auto-Detection** (Recommended)
```python
# Step 6 auto-detects based on tables in entity_schema.yaml
# No manual configuration needed!
```

### Adding New Balance Types

1. **Add to database table**:
```sql
ALTER TABLE bi_movement_balance_mapping 
ADD COLUMN new_balance_type DECIMAL(5,2);
```

2. **Add to entity_schema.yaml**:
```yaml
tables:
  bi_movement_balance_mapping:
    columns:
      - name: new_balance_type
        type: decimal
        is_balance_type: true
        description: "Description of new balance type"
```

3. **Add to metrics_schema.yaml**:
```yaml
movement_balance_metrics:
  new_balance_shares:
    description: "Description"
    sql: "SUM(fm.share_units * mbm.new_balance_type)"
    balance_type_column: "new_balance_type"
```

4. **Use immediately**:
```python
sql = calc.build_participant_balance_sql(
    balance_types=['new_balance_type'],
    filters=filters
)
```

---

## Troubleshooting

### Issue: "No module named 'builders'"

**Solution**:
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

### Issue: "Table 'bi_fact_movement' does not exist"

**Solution**:
```bash
# Check database connection
psql $DATABASE_URL -c "\dt"

# Verify table names in entity_schema.yaml match database
```

### Issue: "Movement calculator not being used"

**Solution**:
```python
# Check schema detection
step6 = TemplatePopulationStep()
print(f"Detected schema: {step6.schema_type}")

# Should output: "Detected schema: movement"
```

### Issue: "Incorrect balance calculations"

**Solution**:
```sql
-- Verify mapping table has correct coefficients
SELECT * FROM bi_movement_balance_mapping 
WHERE movement_type = 'YourMovementType';

-- Should show -1, 0, or 1 in balance columns
```

---

## Deployment

### Docker Setup

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "orchestrator.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/equity_db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
    ports:
      - "8000:8000"
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=equity_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Logging configured
- [ ] Monitoring set up (e.g., Sentry)
- [ ] Rate limiting enabled
- [ ] Backup strategy in place
- [ ] Security audit completed

---

## Next Steps

1. ✅ **Test with your data**: Load your actual movement data
2. ✅ **Customize prompts**: Edit prompts in `prompts/` to match your terminology
3. ✅ **Add balance types**: Extend schema with your specific balance types
4. ✅ **Build API**: Add FastAPI endpoints for web access
5. ✅ **Add authentication**: Implement user authentication
6. ✅ **Deploy**: Deploy to production environment

---

## Support

- **Documentation**: `docs/` folder
- **Issues**: GitHub Issues
- **Email**: support@your-domain.com

---

## License

[Your License Here]
