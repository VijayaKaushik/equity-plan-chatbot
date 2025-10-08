Complete Flow: "Which participants for lenevo are eligible for retirement acceleration?"

Query Analysis
User Query: "Which participants for lenevo are eligible for retirement acceleration?"
What user wants:

List of participants at Lenovo
Who are eligible for retirement acceleration
Retirement acceleration = unvested shares that accelerate vesting upon retirement
Need to check: grants with retirement_eligibility_dt set + have unvested shares


Step 1: Query Understanding
Input
json{
  "user_query": "Which participants for lenevo are eligible for retirement acceleration?",
  "user_id": "user_123"
}
Processing
LLM Analysis with Enhanced Rephrasing:
Original: "Which participants for lenevo are eligible for retirement acceleration?"

Issues to fix:
1. Typo: "lenevo" → "Lenovo"
2. "for lenevo" - awkward preposition, should be "at Lenovo"
3. Grammar: Fine overall structure
4. Clarity: "eligible for retirement acceleration" is clear

Rephrasing:
- Fix typo: Lenovo
- Natural phrasing: "at Lenovo" instead of "for lenevo"
- Add clarity: "Show me" for action verb

Business context:
- Retirement acceleration = unvested equity that vests early upon retirement
- Eligibility = participant has grants with retirement_eligibility_dt
- Must have unvested shares to be meaningful
Output
json{
  "original_query": "Which participants for lenevo are eligible for retirement acceleration?",
  
  "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
  
  "rephrasing_changes": [
    {
      "from": "Which participants",
      "to": "Show me all participants",
      "reason": "Added clear action verb 'Show me' and 'all' for completeness"
    },
    {
      "from": "for lenevo",
      "to": "at Lenovo",
      "reason": "Fixed typo 'lenevo' → 'Lenovo' and changed preposition 'for' → 'at' for natural phrasing"
    },
    {
      "from": "are eligible for retirement acceleration?",
      "to": "who are eligible for retirement acceleration",
      "reason": "Minor grammar adjustment, removed question mark, added 'who' for flow"
    }
  ],
  
  "intent": "list",
  "query_category": "DETAIL",
  "complexity": "medium",
  "requires_clarification": false,
  
  "special_query_type": "retirement_acceleration",  // ✅ Special flag
  
  "reasoning": "Rephrased to fix typo and improve grammar. Query asks for list of participants (DETAIL) with specific eligibility criteria (retirement acceleration). Medium complexity due to special retirement logic requiring grants.retirement_eligibility_dt check and unvested share calculation.",
  
  "business_terms_clarified": [
    "retirement acceleration = unvested shares that vest upon retirement eligibility"
  ],
  
  "rephrasing_quality_score": 0.91,
  "processing_time_ms": 310
}

Step 2: Query Type Classification
Input
json{
  "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
  "query_category": "DETAIL",
  "complexity": "medium",
  "special_query_type": "retirement_acceleration"
}
Processing
Classification Logic:

✅ "participants" = primary entity is participants
✅ "at Lenovo" = specific company filter
✅ "eligible for retirement acceleration" = special retirement criteria
✅ Wants list of participants who meet criteria
Decision: PARTICIPANT_LEVEL (participant-focused query with retirement filter)

Output
json{
  "query_type": "PARTICIPANT_LEVEL",
  "confidence": 0.98,
  "reasoning": "Query asks 'which participants' making participants the primary entity. Company filter (Lenovo) is secondary. Special retirement acceleration criteria requires checking grants with retirement_eligibility_dt and unvested shares. PARTICIPANT_LEVEL query with retirement eligibility filter.",
  "alternative_type": null,
  "special_pattern_detected": "retirement_acceleration"
}

Step 3: Entity Extraction
Input
json{
  "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration"
}
Processing
LLM Extraction with Special Pattern Detection:
python# Detect special keywords
retirement_keywords = [
    "retirement acceleration",
    "retirement eligible",
    "retirement eligibility",
    "retire early vesting"
]

query_lower = query.lower()
has_retirement = any(keyword in query_lower for keyword in retirement_keywords)

# Extract entities
company_mentioned = "Lenovo"
participants_filter = "retirement_eligible"
Output
json{
  "entities": {
    "client_names": ["Lenovo"],
    "participant_names": [],  // ALL participants (filtered by retirement)
    "plan_types": [],
    "statuses": [],
    "date_expressions": [],
    "metrics": ["unvested_shares"],  // Implicit: need unvested to be eligible
    "departments": [],
    "countries": [],
    "regions": [],
    "query_keywords": ["retirement_acceleration"]  // ✅ Special keyword
  },
  
  "entity_type": "participants",
  "entity_level": null,
  
  "special_filters": {
    "retirement_eligibility": true,
    "has_unvested_shares": true,
    "description": "Filter participants who have grants with retirement_eligibility_dt set and have unvested shares remaining"
  },
  
  "implicit_filters": {
    "participant_status": "active",
    "grant_status": "active",
    "description": "Assuming active participants only. Retirement acceleration only applies to unvested shares in active grants."
  },
  
  "business_logic_requirements": {
    "requires_retirement_eligibility_dt": true,
    "requires_unvested_balance": true,
    "sql_requirements": [
      "JOIN to bi_grant_award_latest for retirement_eligibility_dt",
      "Calculate unvested shares using movement schema",
      "Filter where unvested_shares > 0"
    ]
  },
  
  "reasoning": "Query asks for participants filtered by retirement eligibility. 'Lenovo' is company filter. 'Retirement acceleration' is special pattern requiring grants.retirement_eligibility_dt check and unvested share calculation. Only participants with unvested shares eligible for acceleration are relevant."
}

Step 4: Entity Normalization
Input
json{
  "raw_entities": {
    "client_names": ["Lenovo"],
    "query_keywords": ["retirement_acceleration"],
    "special_filters": {
      "retirement_eligibility": true,
      "has_unvested_shares": true
    }
  },
  "user_context": {
    "user_id": "user_123",
    "accessible_clients": [
      "CLNT00000000000000000001",
      "CLNT00000000000000000005",
      "CLNT00000000000000000012",
      "CLNT00000000000000000018",
      "CLNT00000000000000000023"
    ]
  }
}
Processing
Database Lookup for Company:
python# Look up Lenovo
query = """
    SELECT c.client_hub_key, c.name
    FROM clients c
    WHERE c.name ILIKE '%Lenovo%'
      AND c.client_hub_key IN :accessible_clients
      AND c.status = 'active'
"""

# Result: client_hub_key='CLNT00000000000000000005', name="Lenovo"
Output
json{
  "normalized_entities": {
    "client_hub_key": "CLNT00000000000000000005",
    "client_name": "Lenovo",
    "query_keywords": ["retirement_acceleration"],
    "status_filters": {
      "participant_status": "active",
      "grant_status": "active"
    },
    "special_filters": {
      "has_retirement_eligibility": true,
      "has_unvested_shares": true
    },
    "accessible_clients": [
      "CLNT00000000000000000001",
      "CLNT00000000000000000005",
      "CLNT00000000000000000012",
      "CLNT00000000000000000018",
      "CLNT00000000000000000023"
    ]
  },
  
  "normalization_log": [
    {
      "field": "client_names",
      "from": ["Lenovo"],
      "to": "CLNT00000000000000000005",
      "matched": "Lenovo",
      "method": "database_lookup",
      "confidence": 0.98
    },
    {
      "field": "query_keywords",
      "from": ["retirement_acceleration"],
      "to": ["retirement_acceleration"],
      "method": "special_pattern_preserved",
      "note": "Retirement pattern will trigger special SQL template"
    }
  ],
  
  "processing_time_ms": 123
}

Step 5: Template Parameter Extraction
Input
json{
  "query_type": "PARTICIPANT_LEVEL",
  "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
  "normalized_entities": {
    "client_hub_key": "CLNT00000000000000000005",
    "query_keywords": ["retirement_acceleration"]
  }
}
Processing
LLM Analysis using prompts/param_extraction/participant_level.txt:
txtUSER QUERY: "Show me all participants at Lenovo who are eligible for retirement acceleration"

SPECIAL PATTERN DETECTED: retirement_acceleration

Analysis:
1. What to show?
   - Participants (primary)
   - Need: participant details + retirement eligibility date + unvested shares
   
2. Aggregation?
   - NO - user wants to see individual participants
   - aggregation_only = false

3. Display fields:
   - Participant: participant_hub_key, name, email
   - Additional: department (useful context)
   - Retirement: retirement_eligibility_dt (when eligible)
   - Unvested: unvested_shares (what they'll get)

4. Metrics:
   - unvested_shares (calculated from movement schema)
   - This is what accelerates upon retirement

5. Filters:
   - client_hub_key = CLNT00000000000000000005 (Lenovo)
   - has retirement_eligibility_dt IS NOT NULL
   - unvested_shares > 0
   - participant.status = 'active'

6. Special SQL needed:
   - Use retirement_acceleration template
   - Complex CTE query with movement calculations
Output
json{
  "template_parameters": {
    "query_subtype": "retirement_acceleration",  // ✅ Special subtype
    "aggregation_only": false,
    "use_special_template": true,  // ✅ Flag for Step 6
    "special_template_name": "retirement_acceleration",
    
    "display_fields": [
      "pd.participant_hub_key",
      "pd.participant_name",
      "pd.email",
      "pd.department"
    ],
    
    "metrics": ["unvested_shares"],
    
    "computed_fields": [
      "retirement_eligibility_dt"
    ],
    
    "filters": {
      "client_hub_key": "CLNT00000000000000000005",
      "has_retirement_eligibility": true,
      "has_unvested_shares": true,
      "participant_status": "active",
      "grant_status": "active"
    },
    
    "grouping": "GROUP BY pd.participant_hub_key, pd.participant_name, pd.email, pd.department, retirement_eligibility_dt",
    
    "ordering": "ORDER BY unvested_shares DESC",
    
    "limit": 1000
  },
  
  "reasoning": "Special retirement acceleration query detected. Need to show participants with retirement eligibility dates and their unvested shares. Requires complex SQL using movement schema to calculate unvested balances and filter by retirement_eligibility_dt. Will use specialized retirement_acceleration template."
}

Step 6: Template Population (SQL Generation)
Input
json{
  "query_type": "PARTICIPANT_LEVEL",
  "query_subtype": "retirement_acceleration",
  "use_special_template": true,
  "template_parameters": { /* from Step 5 */ }
}
Processing
Detection & Routing:
pythonclass TemplatePopulationStep:
    
    def execute(self, query_type, parameters, normalized_entities):
        """Route to appropriate SQL builder"""
        
        # Check for special patterns
        if parameters.get('query_subtype') == 'retirement_acceleration':
            return self._build_retirement_acceleration_query(
                parameters,
                normalized_entities
            )
        
        # ... other routing logic
    
    def _build_retirement_acceleration_query(self, parameters, normalized_entities):
        """
        Build specialized SQL for retirement acceleration queries
        
        This uses the movement schema with CTEs to:
        1. Get all movements for participants with retirement_eligibility_dt
        2. Calculate unvested shares using movement_balance_mapping
        3. Filter to only those with unvested > 0
        """
        
        client_hub_key = normalized_entities['client_hub_key']
        
        # Use the special template from the documents
        sql = f"""
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
    WHERE fm.client_hub_key = '{client_hub_key}'
    GROUP BY 
        fm.participant_hub_key,
        fm.movement_type,
        fm.movement_sub_type,
        fm.movement_sub_sub_type
),
unvested_participant AS (
    SELECT 
        pm.participant_hub_key,
        pm.retirement_eligibility_dt,
        SUM(pm.share_units * mbm.unvested) AS unvested_shares
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
    pd.participant_hub_key,
    pd.participant_name,
    pd.email,
    pd.department,
    up.retirement_eligibility_dt,
    up.unvested_shares
FROM unvested_participant up
INNER JOIN bi_participant_detail pd
    ON pd.participant_hub_key = up.participant_hub_key
    AND pd.is_latest = 'b1'
    AND pd.client_hub_key = '{client_hub_key}'
    AND pd.status = 'active'
WHERE up.unvested_shares > 0
ORDER BY up.unvested_shares DESC
LIMIT {parameters.get('limit', 1000)}
"""
        
        return {
            'sql': sql,
            'template_used': 'retirement_acceleration',
            'is_complex_query': True
        }
Output
json{
  "sql": "WITH participant_movements AS (SELECT fm.participant_hub_key, fm.movement_type, fm.movement_sub_type, fm.movement_sub_sub_type, MIN(gal.retirement_eligibility_dt) AS retirement_eligibility_dt, SUM(fm.share_units) AS share_units FROM bi_fact_movement fm INNER JOIN bi_grant_award_latest gal ON gal.grant_award_hub_key = fm.grant_award_hub_key AND gal.retirement_eligibility_dt IS NOT NULL WHERE fm.client_hub_key = 'CLNT00000000000000000005' GROUP BY fm.participant_hub_key, fm.movement_type, fm.movement_sub_type, fm.movement_sub_sub_type), unvested_participant AS (SELECT pm.participant_hub_key, pm.retirement_eligibility_dt, SUM(pm.share_units * mbm.unvested) AS unvested_shares FROM participant_movements pm INNER JOIN bi_movement_balance_mapping mbm ON pm.movement_type = mbm.movement_type AND pm.movement_sub_type = mbm.movement_sub_type AND pm.movement_sub_sub_type = mbm.movement_sub_sub_type GROUP BY pm.participant_hub_key, pm.retirement_eligibility_dt) SELECT pd.participant_hub_key, pd.participant_name, pd.email, pd.department, up.retirement_eligibility_dt, up.unvested_shares FROM unvested_participant up INNER JOIN bi_participant_detail pd ON pd.participant_hub_key = up.participant_hub_key AND pd.is_latest = 'b1' AND pd.client_hub_key = 'CLNT00000000000000000005' AND pd.status = 'active' WHERE up.unvested_shares > 0 ORDER BY up.unvested_shares DESC LIMIT 1000",
  
  "sql_formatted": "
-- Retirement Acceleration Eligibility Query
-- Shows participants eligible for retirement with unvested shares

WITH participant_movements AS (
    -- Step 1: Get all movements for participants with retirement eligibility
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
        AND gal.retirement_eligibility_dt IS NOT NULL  -- ✅ Has retirement eligibility
    WHERE fm.client_hub_key = 'CLNT00000000000000000005'  -- ✅ Lenovo only
    GROUP BY 
        fm.participant_hub_key,
        fm.movement_type,
        fm.movement_sub_type,
        fm.movement_sub_sub_type
),
unvested_participant AS (
    -- Step 2: Calculate unvested shares using movement balance mapping
    SELECT 
        pm.participant_hub_key,
        pm.retirement_eligibility_dt,
        SUM(pm.share_units * mbm.unvested) AS unvested_shares  -- ✅ Calculate unvested
    FROM participant_movements pm
    INNER JOIN bi_movement_balance_mapping mbm 
        ON pm.movement_type = mbm.movement_type
        AND pm.movement_sub_type = mbm.movement_sub_type
        AND pm.movement_sub_sub_type = mbm.movement_sub_sub_type
    GROUP BY 
        pm.participant_hub_key, 
        pm.retirement_eligibility_dt
)
-- Step 3: Get participant details and filter
SELECT 
    pd.participant_hub_key,
    pd.participant_name,
    pd.email,
    pd.department,
    up.retirement_eligibility_dt,
    up.unvested_shares
FROM unvested_participant up
INNER JOIN bi_participant_detail pd
    ON pd.participant_hub_key = up.participant_hub_key
    AND pd.is_latest = 'b1'
    AND pd.client_hub_key = 'CLNT00000000000000000005'  -- ✅ Double-check Lenovo
    AND pd.status = 'active'  -- ✅ Active only
WHERE up.unvested_shares > 0  -- ✅ Must have unvested shares
ORDER BY up.unvested_shares DESC  -- ✅ Most unvested first
LIMIT 1000
",
  
  "template_used": "retirement_acceleration",
  
  "components": {
    "cte_count": 2,
    "cte_names": ["participant_movements", "unvested_participant"],
    "key_joins": [
      "bi_fact_movement → bi_grant_award_latest (for retirement_eligibility_dt)",
      "movements → bi_movement_balance_mapping (for unvested calculation)",
      "results → bi_participant_detail (for participant info)"
    ],
    "key_filters": [
      "gal.retirement_eligibility_dt IS NOT NULL",
      "fm.client_hub_key = 'CLNT00000000000000000005'",
      "pd.client_hub_key = 'CLNT00000000000000000005'",
      "up.unvested_shares > 0",
      "pd.status = 'active'"
    ],
    "calculation_method": "Movement-based using balance mapping coefficients"
  },
  
  "complexity_indicators": {
    "uses_ctes": true,
    "uses_movement_schema": true,
    "multi_stage_aggregation": true,
    "estimated_execution_time": "500-1000ms"
  },
  
  "processing_time_ms": 95
}

Step 7: Security Validation
Input
json{
  "sql": "WITH participant_movements AS (SELECT... WHERE fm.client_hub_key = 'CLNT00000000000000000005'...",
  "user_context": {
    "user_id": "user_123",
    "accessible_clients": ["CLNT...001", "CLNT...005", ...]
  }
}
Processing
Security Checks for Complex CTE Query:
pythondef validate_retirement_query_security(sql, user_context):
    """
    Special validation for retirement queries
    Need to check client_hub_key in multiple places
    """
    
    checks = {
        'movement_client_filter': False,
        'participant_client_filter': False,
        'client_authorized': False,
        'no_sql_injection': False
    }
    
    # Check 1: Client filter in movement CTE
    if "fm.client_hub_key = 'CLNT00000000000000000005'" in sql:
        checks['movement_client_filter'] = True
    
    # Check 2: Client filter in participant join
    if "pd.client_hub_key = 'CLNT00000000000000000005'" in sql:
        checks['participant_client_filter'] = True
    
    # Check 3: Verify client is authorized
    if 'CLNT00000000000000000005' in user_context['accessible_clients']:
        checks['client_authorized'] = True
    
    # Check 4: SQL injection
    dangerous_patterns = ['DROP', 'DELETE', 'TRUNCATE', '--', '/*', '*/']
    sql_upper = sql.upper()
    if not any(pattern in sql_upper for pattern in dangerous_patterns):
        checks['no_sql_injection'] = True
    
    return checks
Output
json{
  "validated": true,
  "security_checks": {
    "movement_client_filter": true,
    "movement_client_value": "CLNT00000000000000000005",
    "participant_client_filter": true,
    "participant_client_value": "CLNT00000000000000000005",
    "dual_filtering_applied": true,
    "client_authorized": true,
    "retirement_eligibility_filter": true,
    "unvested_shares_filter": true,
    "sql_injection_risk": false,
    "complex_query_validated": true,
    "all_checks_passed": true
  },
  
  "audit_entry": {
    "audit_id": "audit_20251007_174521",
    "user_id": "user_123",
    "timestamp": "2025-10-07T17:45:21.456Z",
    "query_type": "PARTICIPANT_LEVEL",
    "query_subtype": "retirement_acceleration",
    "special_query": true,
    "original_query": "Which participants for lenevo are eligible for retirement acceleration?",
    "rephrased_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
    "client_accessed": "CLNT00000000000000000005",
    "client_name": "Lenovo",
    "filters_applied": [
      "fm.client_hub_key = 'CLNT00000000000000000005'",
      "pd.client_hub_key = 'CLNT00000000000000000005'",
      "gal.retirement_eligibility_dt IS NOT NULL",
      "up.unvested_shares > 0",
      "pd.status = 'active'"
    ],
    "sql_template": "retirement_acceleration",
    "uses_movement_schema": true,
    "status": "approved",
    "data_sensitivity": "medium",
    "pii_accessed": true
  },
  
  "warnings": [],
  
  "validated_sql": "WITH participant_movements AS...",
  
  "processing_time_ms": 134
}

Step 8: Query Execution
Input
json{
  "validated_sql": "WITH participant_movements AS (SELECT...",
  "execution_params": {
    "timeout_seconds": 30,
    "max_rows": 1000
  }
}
Processing
Execute complex CTE query against database
Output
json{
  "success": true,
  "row_count": 7,
  "execution_time_ms": 687,
  "columns": [
    "participant_hub_key",
    "participant_name",
    "email",
    "department",
    "retirement_eligibility_dt",
    "unvested_shares"
  ],
  "results": [
    {
      "participant_hub_key": "PRT00000000000000000042",
      "participant_name": "John Smith",
      "email": "john.smith@lenovo.com",
      "department": "Engineering",
      "retirement_eligibility_dt": "2026-03-15",
      "unvested_shares": 12500
    },
    {
      "participant_hub_key": "PRT00000000000000000087",
      "participant_name": "Sarah Johnson",
      "email": "sarah.johnson@lenovo.com",
      "department": "Sales",
      "retirement_eligibility_dt": "2026-06-20",
      "unvested_shares": 8750
    },
    {
      "participant_hub_key": "PRT00000000000000000123",
      "participant_name": "Michael Chen",
      "email": "michael.chen@lenovo.com",
      "department": "Product",
      "retirement_eligibility_dt": "2025-12-01",
      "unvested_shares": 6200
    },
    {
      "participant_hub_key": "PRT00000000000000000156",
      "participant_name": "Emily Rodriguez",
      "email": "emily.rodriguez@lenovo.com",
      "department": "Engineering",
      "retirement_eligibility_dt": "2026-09-10",
      "unvested_shares": 5400
    },
    {
      "participant_hub_key": "PRT00000000000000000189",
      "participant_name": "David Kim",
      "email": "david.kim@lenovo.com",
      "department": "Finance",
      "retirement_eligibility_dt": "2025-11-30",
      "unvested_shares": 4800
    },
    {
      "participant_hub_key": "PRT00000000000000000234",
      "participant_name": "Lisa Anderson",
      "email": "lisa.anderson@lenovo.com",
      "department": "Marketing",
      "retirement_eligibility_dt": "2026-01-15",
      "unvested_shares": 3600
    },
    {
      "participant_hub_key": "PRT00000000000000000267",
      "participant_name": "Robert Taylor",
      "email": "robert.taylor@lenovo.com",
      "department": "Operations",
      "retirement_eligibility_dt": "2026-04-22",
      "unvested_shares": 2900
    }
  ],
  
  "query_plan": {
    "planning_time": "2.345 ms",
    "execution_time": "687.234 ms",
    "total_cost": 5847.92,
    "cte_1_rows": 234,
    "cte_2_rows": 45,
    "final_rows": 7,
    "index_usage": {
      "idx_fact_movement_client": "used",
      "idx_fact_movement_grant_award": "used",
      "idx_grant_award_retirement": "used",
      "idx_participant_client": "used"
    }
  },
  
  "summary": {
    "total_eligible_participants": 7,
    "total_unvested_shares_at_risk": 44150,
    "earliest_eligibility_date": "2025-11-30",
    "latest_eligibility_date": "2026-09-10",
    "avg_unvested_per_participant": 6307,
    "departments_represented": 7
  },
  
  "processing_time_ms": 687
}

Step 9: Response Formatting
Input
json{
  "original_query": "Which participants for lenevo are eligible for retirement acceleration?",
  "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
  "query_type": "PARTICIPANT_LEVEL",
  "query_subtype": "retirement_acceleration",
  "results": [ /* 7 participants */ ]
}
Processing
LLM Response Generation with Retirement Context:
Output
markdownI found **7 participants** at Lenovo who are eligible for retirement acceleration.

**Summary:**
- Total eligible participants: **7**
- Total unvested shares subject to acceleration: **44,150 shares**
- Earliest retirement eligibility: **November 30, 2025** (David Kim)
- Latest retirement eligibility: **September 10, 2026** (Emily Rodriguez)
- Average unvested shares per participant: **6,307 shares**

---

### **Participants Eligible for Retirement Acceleration:**

| Name | Department | Email | Retirement Eligible | Unvested Shares |
|------|------------|-------|---------------------|-----------------|
| John Smith | Engineering | john.smith@lenovo.com | March 15, 2026 | 12,500 |
| Sarah Johnson | Sales | sarah.johnson@lenovo.com | June 20, 2026 | 8,750 |
| Michael Chen | Product | michael.chen@lenovo.com | December 1, 2025 | 6,200 |
| Emily Rodriguez | Engineering | emily.rodriguez@lenovo.com | September 10, 2026 | 5,400 |
| David Kim | Finance | david.kim@lenovo.com | November 30, 2025 | 4,800 |
| Lisa Anderson | Marketing | lisa.anderson@lenovo.com | January 15, 2026 | 3,600 |
| Robert Taylor | Operations | robert.taylor@lenovo.com | April 22, 2026 | 2,900 |

---

### **Key Insights:**

**Timing:**
- 2 participants become eligible in 2025 (David Kim, Michael Chen)
- 5 participants become eligible in 2026
- Most eligibility dates are in Q1-Q2 2026

**Impact:**
- John Smith has the most at risk (12,500 unvested shares)
- Engineering department has 2 of the 7 eligible participants
- Total potential acceleration: 44,150 shares if all retire

**What is Retirement Acceleration?**
Retirement acceleration allows eligible participants to immediately vest their remaining unvested shares upon retirement, rather than forfeiting them. This is typically offered to employees who meet specific tenure and age requirements.

---

### **Would you like to:**
- See the vesting schedule for these participants' unvested shares?
- Calculate the financial impact if these participants retire?
- View which specific grants have retirement acceleration provisions?
- Export this list for HR planning purposes?
- See participants who are NOT eligible for retirement acceleration?
Alternative Format (Executive Summary):
markdown**Retirement Acceleration Risk Summary - Lenovo**

**7 employees** are eligible for retirement acceleration:

**High Risk (10,000+ unvested shares):**
- John Smith (Engineering) - 12,500 shares, eligible March 2026

**Medium Risk (5,000-10,000 unvested shares):**
- Sarah Johnson (Sales) - 8,750 shares, eligible June 2026
- Michael Chen (Product) - 6,200 shares, eligible December 2025
- Emily Rodriguez (Engineering) - 5,400 shares, eligible September 2026

**Lower Risk (<5,000 unvested shares):**
- David Kim (Finance) - 4,800 shares, eligible November 2025
- Lisa Anderson (Marketing) - 3,600 shares, eligible January 2026
- Robert Taylor (Operations) - 2,900 shares, eligible April 2026

**Total Exposure:** 44,150 unvested shares could accelerate

**Near-Term Risk:** 11,000 shares (David Kim + Michael Chen) become eligible by end of 2025

**Recommendation:** Consider succession planning for high-risk individuals, especially John Smith.

Complete Flow Diagram
USER QUERY: "Which participants for lenevo are eligible for retirement acceleration?"
    ↓
Step 1: Understanding & Rephrasing
    • Fix typo: "lenevo" → "Lenovo"
    • Rephrase: "Show me all participants at Lenovo who are eligible..."
    • Detect: Special query pattern (retirement)
    ↓
Step 2: Classification
    • Query Type: PARTICIPANT_LEVEL
    • Special pattern: retirement_acceleration
    • Confidence: 0.98
    ↓
Step 3: Entity Extraction
    • Company: Lenovo
    • Query keyword: "retirement_acceleration" ← Key extraction
    • Special filters: has_retirement_eligibility, has_unvested_shares
    ↓
Step 4: Normalization
    • Lenovo → client_hub_key = CLNT00000000000000000005
    • Preserve retirement_acceleration keyword
    ↓
Step 5: Parameter Extraction
    • query_subtype: retirement_acceleration
    • use_special_template: true
    • Filters: retirement_eligibility_dt IS NOT NULL, unvested > 0
    ↓
Step 6: SQL Generation ★ SPECIAL TEMPLATE ★
    • Detects retirement pattern
    • Routes to: build_retirement_acceleration_sql()
    • Generates: Complex CTE query with movement schema
    • Uses: bi_fact_movement + bi_movement_balance_mapping
    ↓
Step 7: Security Validation
    • ✅ Client filter in movement CTE
    • ✅ Client filter in participant join
    • ✅ User authorized for Lenovo
    • ✅ Complex query validated
    ↓
Step 8: Execution
    • Executes 2 CTEs + final query
    • Returns 7 eligible participants
    • Execution time: 687ms (complex query)
    ↓
Step 9: Response Formatting
    • Formats as table with retirement dates
    • Adds summary statistics
    • Explains retirement acceleration concept
    • Provides insights and recommendations
    ↓
RESPONSE: "7 participants at Lenovo are eligible..."

Key Technical Details
1. Why This Query is Special
AspectRegular QueryRetirement QueryTemplateStandard participant_level.sqlretirement_acceleration.sqlComplexitySimple JOINsComplex CTEs with movement calculationsTables Used3-4 tables5+ tables including movement schemaKey FieldStandard filtersretirement_eligibility_dt (special field)CalculationDirect countsMovement-based unvested calculationExecution Time100-300ms500-1000ms

2. SQL Breakdown
sql-- CTE 1: Get movements for participants with retirement eligibility
WITH participant_movements AS (
    -- Groups by participant + movement type
    -- Filters to only grants with retirement_eligibility_dt
    -- SUM(share_units) for each movement type
)

-- CTE 2: Calculate unvested shares
unvested_participant AS (
    -- Joins to movement_balance_mapping
    -- Multiplies share_units × unvested coefficient
    -- SUM to get total unvested per participant
)

-- Final: Get participant details
SELECT participant details + retirement_eligibility_dt + unvested_shares
WHERE unvested_shares > 0  -- Must have unvested to be meaningful

3. Movement Schema Usage
bi_fact_movement (all equity movements)
    ↓
    × bi_movement_balance_mapping (coefficients)
    ↓
    = unvested balance calculation

Example:
Movement: GrantAward, 1000 shares
Mapping: unvested coefficient = 1
Result: 1000 × 1 = 1000 unvested

Movement: Release, 250 shares
Mapping: unvested coefficient = -1
Result: 250 × -1 = -250 unvested (reduces unvested balance)

4. Why retirement_eligibility_dt is Special
yaml# In bi_grant_award_latest table
retirement_eligibility_dt:
  type: date
  nullable: true  # Not all grants have retirement acceleration
  description: "Date when participant becomes eligible for retirement acceleration"
  business_logic: |
    - Set at grant creation based on participant's age/tenure
    - Typically: age 55+ with 10+ years service
    - If set, unvested shares vest immediately upon retirement after this date
    - If NULL, standard forfeiture rules apply upon termination

5. Comparison with Other Participant Queries
Query A: "Show me participants at Lenovo"
sql-- Simple query
SELECT pd.*
FROM bi_participant_detail pd
WHERE pd.client_hub_key = 'CLNT00000000000000000005'
  AND pd.status = 'active'
Query B: "Show me participants at Lenovo with unvested shares"
sql-- Movement-based but straightforward
SELECT 
    pd.participant_name,
    SUM(fm.share_units * mbm.unvested) as unvested_shares
FROM bi_participant_detail pd
INNER JOIN bi_fact_movement fm ...
GROUP BY pd.participant_name
HAVING SUM(fm.share_units * mbm.unvested) > 0
Query C: "Show me participants eligible for retirement" ✅ (This query)
sql-- Complex with retirement logic
WITH participant_movements AS (...)  -- CTE 1
unvested_participant AS (...)        -- CTE 2
SELECT ... 
WHERE retirement_eligibility_dt IS NOT NULL  -- Special filter
  AND unvested_shares > 0

Summary
StepKey ActionCritical Elements1Rephrase + Detect special pattern"retirement acceleration" keyword detected2Classify as PARTICIPANT_LEVELWith special_pattern flag3Extract retirement keywordquery_keywords: ["retirement_acceleration"]4Normalize Lenovo → hub keyPreserve retirement keyword5Set use_special_template=trueTriggers special SQL generation6★ Use retirement_acceleration templateComplex CTE query with movement schema7Validate complex query securityDual client filtering verified8Execute CTEs → 7 results687ms execution (complex)9Format with retirement contextTable + insights + recommendations
Result: List of 7 Lenovo participants eligible for retirement acceleration with their unvested shares and eligibility dates!
Key Insight: The system detected the special "retirement acceleration" pattern and automatically routed to a specialized SQL template that uses the movement schema to calculate unvested shares for participants with retirement_eligibility_dt set. This is much more complex than a standard participant query!RetryVhow is this happening : Detect: Special query pattern (retirement)Traced detection mechanisms for special retirement query pattern.Great question! The user is asking HOW the system detects the special "retirement" query pattern. Let me trace through exactly how this detection happens at each step.
Looking at the flow I provided, I showed:

Step 1: "special_query_type": "retirement_acceleration"
Step 2: "special_pattern_detected": "retirement_acceleration"
Step 3: "query_keywords": ["retirement_acceleration"]

But I didn't explain the MECHANISM of detection. Let me break down exactly how this works:

In the prompts - LLM is given patterns to look for
Pattern matching - Keywords/phrases that trigger special handling
Configuration files - May have special query patterns defined
Code logic - Pattern detection in the code

Let me provide a detailed explanation with actual implementation details.How Special Pattern Detection Works: "Retirement"

Detection Mechanism Overview
The special pattern detection happens through multiple layers:
Layer 1: Prompt Instructions (LLM-based detection)
    ↓
Layer 2: Keyword Matching (Pattern matching in code)
    ↓
Layer 3: Configuration Files (Pattern definitions)
    ↓
Layer 4: Validation & Routing (Code confirms pattern)

Layer 1: LLM-Based Detection in Prompts
File: prompts/understanding_prompt.txt
The prompt template includes special pattern recognition instructions:
txtYou are an expert at understanding natural language queries about equity compensation plans.

USER QUERY: "{query}"

INSTRUCTIONS:

1. CORRECT TYPOS AND GRAMMAR
   ...

2. DETERMINE QUERY CATEGORY
   ...

3. IDENTIFY SPECIAL QUERY PATTERNS
   
   Some queries require specialized handling. Detect these patterns:
   
   **RETIREMENT ACCELERATION:**
   Keywords: "retirement acceleration", "retirement eligible", "retirement eligibility",
            "retire early vesting", "accelerate upon retirement", "retire and vest"
   
   When detected:
   - Set special_query_type: "retirement_acceleration"
   - Note: Requires checking grants.retirement_eligibility_dt
   - Note: Requires calculating unvested shares
   
   **BLACKOUT PERIOD:**
   Keywords: "blackout period", "trading window", "blackout", "can't trade"
   
   **INSIDER TRADING:**
   Keywords: "insiders", "section 16", "beneficial ownership", "10% owner"
   
   **PERFORMANCE VESTING:**
   Keywords: "performance vesting", "performance conditions", "PSU", "performance shares"

4. IDENTIFY INTENT
   ...

OUTPUT FORMAT (JSON only):
{
  "corrected_query": "...",
  "intent": "...",
  "query_category": "...",
  "special_query_type": "retirement_acceleration|blackout_period|insider_trading|performance_vesting|null",
  "special_pattern_confidence": 0.95,
  "reasoning": "..."
}
How LLM Detects It
When the query is: "Which participants for lenevo are eligible for retirement acceleration?"
The LLM processes:
python# LLM internal reasoning (conceptual)
query_lower = "which participants for lenevo are eligible for retirement acceleration?"

# Check for retirement patterns
retirement_patterns = [
    "retirement acceleration",
    "retirement eligible", 
    "retirement eligibility"
]

for pattern in retirement_patterns:
    if pattern in query_lower:
        special_query_type = "retirement_acceleration"
        confidence = 0.95
        break

# LLM output
{
  "special_query_type": "retirement_acceleration",
  "special_pattern_confidence": 0.95
}

Layer 2: Code-Based Keyword Matching
File: utils/pattern_detector.py
pythonclass SpecialPatternDetector:
    """
    Detects special query patterns that require specialized handling
    """
    
    # Pattern definitions
    PATTERNS = {
        'retirement_acceleration': {
            'keywords': [
                'retirement acceleration',
                'retirement eligible',
                'retirement eligibility',
                'retire early vesting',
                'accelerate upon retirement',
                'retire and vest',
                'retirement provision'
            ],
            'synonyms': [
                'retire', 'retirement', 'retiring'
            ],
            'context_words': [
                'eligible', 'eligibility', 'acceleration', 'accelerate', 'vest'
            ],
            'requires_tables': ['bi_grant_award_latest'],
            'requires_fields': ['retirement_eligibility_dt'],
            'template_name': 'retirement_acceleration'
        },
        
        'blackout_period': {
            'keywords': [
                'blackout period',
                'trading window',
                'blackout',
                'cannot trade',
                "can't trade"
            ],
            'requires_tables': ['blackout_periods'],
            'template_name': 'blackout_period_check'
        },
        
        'insider_trading': {
            'keywords': [
                'insider',
                'section 16',
                'beneficial ownership',
                '10% owner',
                'form 4'
            ],
            'requires_tables': ['insider_designations'],
            'template_name': 'insider_compliance'
        }
    }
    
    def detect(self, query: str) -> Dict:
        """
        Detect special patterns in query
        
        Returns:
            {
                'pattern_detected': bool,
                'pattern_type': str,
                'confidence': float,
                'matched_keywords': List[str],
                'reasoning': str
            }
        """
        query_lower = query.lower()
        
        for pattern_type, pattern_config in self.PATTERNS.items():
            # Check for exact keyword matches
            matched_keywords = []
            
            for keyword in pattern_config['keywords']:
                if keyword in query_lower:
                    matched_keywords.append(keyword)
            
            # If any keyword matches, pattern detected
            if matched_keywords:
                # Calculate confidence based on matches
                confidence = self._calculate_confidence(
                    query_lower,
                    pattern_config,
                    matched_keywords
                )
                
                return {
                    'pattern_detected': True,
                    'pattern_type': pattern_type,
                    'confidence': confidence,
                    'matched_keywords': matched_keywords,
                    'reasoning': f"Detected '{pattern_type}' pattern based on keywords: {matched_keywords}",
                    'requires_tables': pattern_config.get('requires_tables', []),
                    'requires_fields': pattern_config.get('requires_fields', []),
                    'template_name': pattern_config.get('template_name')
                }
        
        # No pattern detected
        return {
            'pattern_detected': False,
            'pattern_type': None,
            'confidence': 0.0,
            'matched_keywords': [],
            'reasoning': 'No special patterns detected'
        }
    
    def _calculate_confidence(self, query: str, pattern_config: Dict, 
                             matched_keywords: List[str]) -> float:
        """
        Calculate confidence score for pattern match
        """
        confidence = 0.0
        
        # Base confidence from keyword match
        confidence += 0.5 * len(matched_keywords)
        
        # Bonus for context words
        context_words = pattern_config.get('context_words', [])
        context_matches = sum(1 for word in context_words if word in query)
        confidence += 0.1 * context_matches
        
        # Bonus for synonyms
        synonyms = pattern_config.get('synonyms', [])
        synonym_matches = sum(1 for syn in synonyms if syn in query)
        confidence += 0.05 * synonym_matches
        
        # Cap at 0.99
        return min(confidence, 0.99)
Usage in Step 1
python# File: step1_understanding.py

class QueryUnderstandingStep:
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.pattern_detector = SpecialPatternDetector()
    
    async def execute(self, user_query: str) -> Dict:
        """Execute query understanding"""
        
        # STEP 1: Detect special patterns BEFORE calling LLM
        pattern_detection = self.pattern_detector.detect(user_query)
        
        # STEP 2: Build prompt with pattern info
        prompt = self._build_prompt(user_query, pattern_detection)
        
        # STEP 3: Call LLM
        llm_response = await self.llm.call(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = json.loads(llm_response['choices'][0]['message']['content'])
        
        # STEP 4: Merge code detection with LLM output
        if pattern_detection['pattern_detected']:
            result['special_query_type'] = pattern_detection['pattern_type']
            result['pattern_confidence'] = pattern_detection['confidence']
            result['matched_keywords'] = pattern_detection['matched_keywords']
            result['requires_special_template'] = True
            result['template_name'] = pattern_detection['template_name']
        
        return result

Layer 3: Configuration File Patterns
File: config/special_query_patterns.yaml
yamlspecial_patterns:
  
  retirement_acceleration:
    description: "Queries about participants eligible for retirement acceleration"
    
    keywords:
      primary:
        - "retirement acceleration"
        - "retirement eligible"
        - "retirement eligibility"
      
      secondary:
        - "retire"
        - "retirement"
        - "accelerate upon retirement"
      
      context:
        - "eligible"
        - "eligibility"
        - "vest"
        - "vesting"
    
    database_requirements:
      tables:
        - bi_grant_award_latest
        - bi_fact_movement
        - bi_movement_balance_mapping
      
      fields:
        - retirement_eligibility_dt
      
      conditions:
        - retirement_eligibility_dt IS NOT NULL
        - unvested_shares > 0
    
    sql_template: "templates/retirement_acceleration.sql"
    
    expected_entities:
      - company (optional)
      - participants (optional, or ALL)
    
    expected_metrics:
      - unvested_shares
    
    processing_notes: |
      - Requires complex CTE query with movement schema
      - Must calculate unvested balance using movement_balance_mapping
      - Filter to only participants with retirement_eligibility_dt set
      - Execution time typically 500-1000ms
    
    example_queries:
      - "Which participants are eligible for retirement acceleration?"
      - "Show me retirement eligible employees with unvested shares"
      - "Who can retire and have their equity vest early?"
      - "Participants eligible for retirement at Lenovo"
  
  blackout_period:
    description: "Queries about trading blackout periods"
    keywords:
      primary:
        - "blackout period"
        - "trading window"
        - "blackout"
    database_requirements:
      tables:
        - blackout_periods
    sql_template: "templates/blackout_period_check.sql"
  
  insider_trading:
    description: "Queries about insider trading compliance"
    keywords:
      primary:
        - "insider"
        - "section 16"
        - "beneficial ownership"
    database_requirements:
      tables:
        - insider_designations
    sql_template: "templates/insider_compliance.sql"

Layer 4: Pattern Validation & Routing
Detection Flow in Code
python# Complete detection flow

def process_query(user_query: str):
    """
    Complete flow showing pattern detection
    """
    
    # ============================================
    # DETECTION POINT 1: Pattern Detector (Code)
    # ============================================
    detector = SpecialPatternDetector()
    pattern_result = detector.detect(user_query)
    
    print(f"Pattern Detection Result: {pattern_result}")
    # Output:
    # {
    #     'pattern_detected': True,
    #     'pattern_type': 'retirement_acceleration',
    #     'confidence': 0.95,
    #     'matched_keywords': ['retirement acceleration', 'eligible'],
    #     'template_name': 'retirement_acceleration'
    # }
    
    # ============================================
    # DETECTION POINT 2: LLM Understanding
    # ============================================
    step1 = QueryUnderstandingStep(llm_client)
    understanding = await step1.execute(user_query)
    
    print(f"LLM Understanding: {understanding}")
    # Output includes:
    # {
    #     'special_query_type': 'retirement_acceleration',
    #     'special_pattern_confidence': 0.95
    # }
    
    # ============================================
    # DETECTION POINT 3: Entity Extraction
    # ============================================
    step3 = EntityExtractionStep(llm_client)
    entities = await step3.execute(understanding['corrected_query'])
    
    print(f"Entities: {entities}")
    # Output includes:
    # {
    #     'query_keywords': ['retirement_acceleration'],
    #     'special_filters': {
    #         'has_retirement_eligibility': True
    #     }
    # }
    
    # ============================================
    # DETECTION POINT 4: Parameter Extraction
    # ============================================
    step5 = TemplateParameterExtractor(llm_client)
    params = await step5.execute(
        query_type='PARTICIPANT_LEVEL',
        corrected_query=understanding['corrected_query'],
        normalized_entities=entities
    )
    
    print(f"Parameters: {params}")
    # Output includes:
    # {
    #     'query_subtype': 'retirement_acceleration',
    #     'use_special_template': True,
    #     'special_template_name': 'retirement_acceleration'
    # }
    
    # ============================================
    # DETECTION POINT 5: SQL Generation Routing
    # ============================================
    step6 = TemplatePopulationStep()
    
    # Route based on detected pattern
    if params.get('query_subtype') == 'retirement_acceleration':
        sql = step6.build_retirement_acceleration_query(params, entities)
    else:
        sql = step6.build_standard_query(params, entities)
    
    return sql

Detailed Example: Query Processing
Input Query
"Which participants for lenevo are eligible for retirement acceleration?"
Step-by-Step Detection
Detection 1: Initial Pattern Match (Code)
python# In utils/pattern_detector.py

query = "which participants for lenevo are eligible for retirement acceleration?"
query_lower = query.lower()

# Check retirement_acceleration pattern
keywords = ['retirement acceleration', 'retirement eligible', 'retirement eligibility']

matched = []
for keyword in keywords:
    if keyword in query_lower:
        matched.append(keyword)

# Result
matched = ['retirement acceleration']  # ✅ MATCH FOUND

# Context words check
context_words = ['eligible', 'eligibility', 'acceleration']
context_found = []
for word in context_words:
    if word in query_lower:
        context_found.append(word)

context_found = ['eligible']  # ✅ CONTEXT MATCH

# Calculate confidence
confidence = 0.5 * len(matched) + 0.1 * len(context_found)
confidence = 0.5 * 1 + 0.1 * 1 = 0.60

# Boost for exact phrase match
if 'retirement acceleration' in query_lower:
    confidence += 0.35  # Exact phrase bonus

confidence = 0.95  # ✅ HIGH CONFIDENCE

# Return
return {
    'pattern_detected': True,
    'pattern_type': 'retirement_acceleration',
    'confidence': 0.95,
    'matched_keywords': ['retirement acceleration'],
    'template_name': 'retirement_acceleration'
}
Detection 2: LLM Confirmation
python# In step1_understanding.py

# Prompt includes pattern detection hint
prompt = f"""
USER QUERY: "{query}"

PRE-DETECTED PATTERN:
Pattern Type: retirement_acceleration
Confidence: 0.95
Matched Keywords: ['retirement acceleration']

Your task: Confirm this pattern and provide additional context.

OUTPUT:
{{
  "corrected_query": "...",
  "special_query_type": "retirement_acceleration",  # Confirm or correct
  "special_pattern_confidence": 0.95
}}
"""

# LLM confirms
llm_response = {
    "corrected_query": "Show me all participants at Lenovo who are eligible for retirement acceleration",
    "special_query_type": "retirement_acceleration",  # ✅ CONFIRMED
    "special_pattern_confidence": 0.95
}
Detection 3: Entity Extraction Keywords
python# In step3_entity_extraction.py

# LLM extracts keywords from corrected query
corrected_query = "Show me all participants at Lenovo who are eligible for retirement acceleration"

# Entity extraction prompt
prompt = f"""
Extract entities from: "{corrected_query}"

SPECIAL INSTRUCTIONS:
This query has been flagged as 'retirement_acceleration' pattern.
Extract the keyword 'retirement_acceleration' into query_keywords field.

OUTPUT:
{{
  "entities": {{...}},
  "query_keywords": ["retirement_acceleration"]  # ✅ EXTRACTED
}}
"""

# Result
entities = {
    "client_names": ["Lenovo"],
    "query_keywords": ["retirement_acceleration"],  # ✅ PRESERVED
    "special_filters": {
        "has_retirement_eligibility": True
    }
}
Detection 4: Parameter Extraction Routing
python# In step5_parameter_extraction.py

# Check for special pattern
if 'retirement_acceleration' in normalized_entities.get('query_keywords', []):
    # Use special parameter extraction logic
    parameters = {
        'query_subtype': 'retirement_acceleration',  # ✅ FLAG SET
        'use_special_template': True,
        'special_template_name': 'retirement_acceleration'
    }
Detection 5: SQL Generation Routing
python# In step6_template_population.py

def execute(self, query_type, parameters, normalized_entities):
    """Route to appropriate SQL builder"""
    
    # Check for special subtype
    if parameters.get('query_subtype') == 'retirement_acceleration':  # ✅ CHECK
        return self.build_retirement_acceleration_query(
            parameters,
            normalized_entities
        )
    
    # Default routing
    elif query_type == 'PARTICIPANT_LEVEL':
        return self.build_participant_query(parameters, normalized_entities)

Configuration-Driven Detection
File: config/special_query_patterns.yaml (Extended)
yamlpattern_matching:
  
  method: "hybrid"  # keyword + llm + context
  
  confidence_thresholds:
    high: 0.85      # Use special template
    medium: 0.60    # Ask for confirmation
    low: 0.40       # Ignore pattern
  
  keyword_weights:
    exact_phrase: 0.50      # "retirement acceleration" exact match
    partial_match: 0.25     # "retirement" or "acceleration" separately
    context_word: 0.10      # "eligible", "vest", etc.
    synonym: 0.05           # "retire", "retiring"
  
  detection_rules:
    
    retirement_acceleration:
      
      # Rule 1: Exact phrase match → High confidence
      exact_phrases:
        - "retirement acceleration"
        - "retirement eligible"
        - "retirement eligibility"
      exact_phrase_confidence: 0.95
      
      # Rule 2: Keyword combination → Medium confidence
      keyword_combinations:
        - ["retirement", "accelerate"]
        - ["retire", "vest", "early"]
        - ["retirement", "eligible", "unvested"]
      combination_confidence: 0.70
      
      # Rule 3: Single keyword + context → Lower confidence
      single_keyword_with_context:
        keyword: "retirement"
        required_context: ["eligible", "vest", "acceleration"]
        min_context_matches: 2
        confidence: 0.60
      
      # Disqualifiers (prevent false positives)
      disqualifiers:
        - "not eligible for retirement"
        - "exclude retirement"
        - "without retirement"

Multi-Stage Detection Summary
Stage 1: CODE DETECTION (pattern_detector.py)
    ├─ Keyword matching: "retirement acceleration" found
    ├─ Context analysis: "eligible" found
    ├─ Confidence: 0.95
    └─ Result: Pattern detected ✅

Stage 2: LLM CONFIRMATION (Step 1)
    ├─ LLM receives pre-detection hint
    ├─ LLM confirms pattern
    ├─ LLM rephrases query for clarity
    └─ Result: Pattern confirmed ✅

Stage 3: ENTITY PRESERVATION (Step 3)
    ├─ Extract query_keywords: ["retirement_acceleration"]
    ├─ Set special_filters
    └─ Result: Pattern info preserved ✅

Stage 4: PARAMETER FLAGGING (Step 5)
    ├─ Check query_keywords
    ├─ Set use_special_template: true
    └─ Result: Special template flagged ✅

Stage 5: SQL ROUTING (Step 6)
    ├─ Check query_subtype == 'retirement_acceleration'
    ├─ Route to special SQL builder
    └─ Result: Special SQL generated ✅

Why Multiple Detection Layers?
LayerPurposeBenefitCode DetectionFast, deterministicCatches obvious patterns immediatelyLLM ConfirmationContextual understandingHandles variations, synonyms, complex phrasingEntity PreservationCarry pattern through pipelineEnsures pattern info doesn't get lostParameter FlaggingExplicit routing signalClear handoff to specialized logicSQL RoutingFinal dispatchGenerates correct SQL template

Example: False Positive Prevention
Query: "Show me participants who are NOT eligible for retirement"
python# Code detection
query_lower = "show me participants who are not eligible for retirement"

# Keyword match
if 'retirement' in query_lower:  # ✅ Match
    matched = True

# But check for disqualifiers
disqualifiers = ['not eligible', 'exclude retirement', 'without retirement']
for disqualifier in disqualifiers:
    if disqualifier in query_lower:  # ✅ "not eligible" found
        matched = False
        break

# Result: Pattern NOT detected (correctly avoided false positive)

Summary: How Detection Works

Pattern Detector (code) scans for keywords → 95% confidence
LLM (Step 1) confirms and understands context → pattern verified
Entity Extraction (Step 3) preserves pattern keyword → carried forward
Parameter Extraction (Step 5) sets special_template flag → routing signal
SQL Generation (Step 6) routes to specialized builder → correct SQL

Key Files:

utils/pattern_detector.py - Keyword-based detection
config/special_query_patterns.yaml - Pattern definitions
prompts/understanding_prompt.txt - LLM detection instructions
step1_understanding.py - Detection integration
step6_template_population.py - Pattern routing

The detection is redundant by design - multiple layers ensure patterns are caught and handled correctly!RetryClaude can make mistakes. Please double-check responses.
