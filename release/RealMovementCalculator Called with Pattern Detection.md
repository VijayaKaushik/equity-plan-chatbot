When is RealMovementCalculator Called with Pattern Detection?

The Connection: Pattern Detection → RealMovementCalculator
The RealMovementCalculator is called in Step 6 (Template Population) when BOTH conditions are met:

✅ Pattern detected: retirement_acceleration (from Steps 1-5)
✅ Schema type: movement (auto-detected in Step 6)


Step 6: The Decision Point
File: steps/step6_template_population.py
pythonclass TemplatePopulationStep:
    
    def __init__(self, config_path='config'):
        self.config_path = config_path
        
        # Detect schema type
        self.schema_type = self._detect_schema_type()  # ← Returns 'movement' or 'traditional'
        
        # Initialize appropriate calculator
        if self.schema_type == 'movement':
            from builders.real_movement_calculator import RealMovementCalculator
            self.movement_calc = RealMovementCalculator(config_path)  # ← Initialize
        else:
            from builders.traditional_calculator import TraditionalCalculator
            self.traditional_calc = TraditionalCalculator(config_path)
    
    async def execute(self, query_type, parameters, normalized_entities, user_context):
        """
        Main entry point for Step 6
        
        This is where pattern detection meets schema detection
        """
        
        # ============================================================
        # DECISION TREE: Schema Type × Query Pattern
        # ============================================================
        
        if self.schema_type == 'movement':
            # Using movement schema
            
            # ============================================================
            # CHECK FOR SPECIAL PATTERNS
            # ============================================================
            
            # Pattern 1: Retirement Acceleration
            if self._is_retirement_query(parameters):  # ← Check pattern
                # ✅ RETIREMENT PATTERN DETECTED + MOVEMENT SCHEMA
                return self._route_to_retirement_sql(
                    parameters,
                    normalized_entities,
                    user_context
                )
            
            # Pattern 2: Standard queries
            else:
                return self._route_to_standard_movement_sql(
                    parameters,
                    normalized_entities,
                    user_context
                )
        
        else:
            # Using traditional schema
            return self._route_to_traditional_sql(
                parameters,
                normalized_entities,
                user_context
            )
    
    def _is_retirement_query(self, parameters: Dict) -> bool:
        """
        Check if this is a retirement acceleration query
        
        Checks multiple sources for pattern detection:
        1. query_subtype from Step 5
        2. query_keywords from Step 3
        3. special_filters from Step 4
        """
        
        # Check 1: query_subtype (most explicit)
        if parameters.get('query_subtype') == 'retirement_acceleration':
            return True
        
        # Check 2: query_keywords (from entity extraction)
        query_keywords = parameters.get('query_keywords', [])
        if 'retirement_acceleration' in query_keywords:
            return True
        
        # Check 3: special_filters (from normalization)
        special_filters = parameters.get('filters', {}).get('special_filters', {})
        if special_filters.get('has_retirement_eligibility'):
            return True
        
        return False
    
    def _route_to_retirement_sql(self, parameters, normalized_entities, user_context):
        """
        Route to retirement acceleration SQL builder
        
        This is where RealMovementCalculator is called for retirement queries
        """
        
        # Build filter object
        from builders.real_movement_calculator import MovementFilter
        
        filters = MovementFilter(
            client_hub_key=normalized_entities.get('client_hub_key'),
            participant_hub_key=normalized_entities.get('participant_hub_key'),
            accessible_clients=user_context.get('accessible_clients', [])
        )
        
        # ============================================================
        # CALL REALMOVEMENTCALCULATOR - RETIREMENT METHOD
        # ============================================================
        sql = self.movement_calc.build_retirement_acceleration_sql(filters)
        # ✅ This is where RealMovementCalculator is called!
        
        return {
            'sql': sql,
            'sql_formatted': self._format_sql(sql),
            'template_used': 'retirement_acceleration',
            'schema_type': 'movement',
            'pattern_detected': 'retirement_acceleration',
            'calculator_used': 'RealMovementCalculator',
            'method_called': 'build_retirement_acceleration_sql'
        }

Complete Flow: Pattern Detection → RealMovementCalculator
┌────────────────────────────────────────────────────────────┐
│ STEP 1: Query Understanding                                │
├────────────────────────────────────────────────────────────┤
│ Input: "Which participants are eligible for retirement?"  │
│                                                            │
│ Pattern Detector:                                          │
│   └─ Keyword match: "retirement" → pattern detected       │
│                                                            │
│ Output: {                                                  │
│   "special_query_type": "retirement_acceleration",        │
│   "confidence": 0.95                                       │
│ }                                                          │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ STEP 2-4: Classification, Extraction, Normalization       │
├────────────────────────────────────────────────────────────┤
│ Pattern info preserved through:                            │
│ - Step 2: query_type classification                        │
│ - Step 3: query_keywords: ["retirement_acceleration"]     │
│ - Step 4: special_filters: {has_retirement_eligibility}   │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ STEP 5: Parameter Extraction                               │
├────────────────────────────────────────────────────────────┤
│ Output: {                                                  │
│   "query_subtype": "retirement_acceleration",  ← Flag set  │
│   "use_special_template": true,                           │
│   "filters": {...}                                         │
│ }                                                          │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ STEP 6: Template Population ★ DECISION POINT ★            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Step 6a: Detect Schema Type                               │
│   schema_type = _detect_schema_type()                     │
│   └─ Returns: 'movement'                                  │
│                                                            │
│ Step 6b: Initialize Calculator                            │
│   if schema_type == 'movement':                           │
│       movement_calc = RealMovementCalculator()  ← Init    │
│                                                            │
│ Step 6c: Check for Special Pattern                        │
│   if _is_retirement_query(parameters):  ← Check pattern   │
│       # ✅ PATTERN DETECTED!                              │
│                                                            │
│ Step 6d: Route to Retirement Method                       │
│   sql = movement_calc.build_retirement_acceleration_sql() │
│          ^^^^^^^^^^^^^^                                    │
│          THIS IS WHERE IT'S CALLED!                       │
│                                                            │
│ Output: Complex SQL with CTEs for retirement              │
└────────────────────────────────────────────────────────────┘

The Routing Decision Tree in Step 6
pythondef execute(self, query_type, parameters, normalized_entities, user_context):
    """Step 6 main routing logic"""
    
    # ====================================
    # BRANCH 1: Schema Detection
    # ====================================
    if self.schema_type == 'movement':
        
        # ====================================
        # BRANCH 2: Pattern Detection
        # ====================================
        
        # Sub-branch 2a: Retirement Pattern
        if self._is_retirement_query(parameters):
            filters = self._build_movement_filter(normalized_entities, user_context)
            
            # ✅ CALL: RealMovementCalculator.build_retirement_acceleration_sql()
            return self.movement_calc.build_retirement_acceleration_sql(filters)
        
        # Sub-branch 2b: Single Metric
        elif self._is_single_metric(parameters):
            metrics = parameters['metrics']
            filters = self._build_movement_filter(normalized_entities, user_context)
            
            if metrics[0] == 'unvested_shares':
                # ✅ CALL: RealMovementCalculator.build_unvested_shares_sql()
                return self.movement_calc.build_unvested_shares_sql(filters)
            
            elif metrics[0] == 'vested_shares':
                # ✅ CALL: RealMovementCalculator.build_vested_shares_sql()
                return self.movement_calc.build_vested_shares_sql(filters)
        
        # Sub-branch 2c: Multiple Metrics
        elif self._is_multi_metric(parameters):
            metrics = parameters['metrics']
            filters = self._build_movement_filter(normalized_entities, user_context)
            
            # ✅ CALL: RealMovementCalculator.build_multi_balance_sql()
            return self.movement_calc.build_multi_balance_sql(
                balance_types_list=metrics,
                filters=filters,
                group_by_participant=True
            )
        
        # Sub-branch 2d: Default
        else:
            filters = self._build_movement_filter(normalized_entities, user_context)
            # ✅ CALL: RealMovementCalculator.build_movement_breakdown_sql()
            return self.movement_calc.build_movement_breakdown_sql(filters)
    
    else:
        # Traditional schema - different calculator
        return self.traditional_calc.build_sql(...)

Pattern Detection Checkpoints
Where Pattern is Checked in Step 6
pythondef _is_retirement_query(self, parameters: Dict) -> bool:
    """
    Check if retirement pattern detected
    
    Checks 3 sources (redundant by design):
    """
    
    # ============================================
    # CHECKPOINT 1: Direct flag from Step 5
    # ============================================
    if parameters.get('query_subtype') == 'retirement_acceleration':
        logger.info("Retirement pattern detected via query_subtype")
        return True
    
    # ============================================
    # CHECKPOINT 2: Keywords from Step 3
    # ============================================
    query_keywords = parameters.get('query_keywords', [])
    if 'retirement_acceleration' in query_keywords:
        logger.info("Retirement pattern detected via query_keywords")
        return True
    
    # ============================================
    # CHECKPOINT 3: Special filters from Step 4
    # ============================================
    filters = parameters.get('filters', {})
    if filters.get('has_retirement_eligibility'):
        logger.info("Retirement pattern detected via special_filters")
        return True
    
    # ============================================
    # CHECKPOINT 4: Normalized entities
    # ============================================
    normalized = parameters.get('normalized_entities', {})
    if 'retirement_acceleration' in normalized.get('query_keywords', []):
        logger.info("Retirement pattern detected via normalized_entities")
        return True
    
    logger.info("No retirement pattern detected")
    return False

Example: Trace Through Retirement Query
Query: "Which participants for Lenovo are eligible for retirement acceleration?"
Data Flow
python# STEP 1 OUTPUT
step1_output = {
    "special_query_type": "retirement_acceleration",  # ← Pattern detected
    "confidence": 0.95
}

# STEP 3 OUTPUT
step3_output = {
    "entities": {
        "client_names": ["Lenovo"],
        "query_keywords": ["retirement_acceleration"]  # ← Pattern preserved
    }
}

# STEP 5 OUTPUT
step5_output = {
    "template_parameters": {
        "query_subtype": "retirement_acceleration",  # ← Pattern flagged
        "use_special_template": True,
        "filters": {
            "has_retirement_eligibility": True
        }
    }
}

# STEP 6 EXECUTION
def step6_execute():
    # Schema detection
    schema_type = 'movement'  # Detected
    
    # Initialize calculator
    movement_calc = RealMovementCalculator(config_path='config')
    
    # Check pattern
    is_retirement = _is_retirement_query(step5_output)
    # Returns: True (found in query_subtype)
    
    if is_retirement:
        # Build filters
        filters = MovementFilter(
            client_hub_key='CLNT00000000000000000005',
            participant_hub_key=None  # ALL participants
        )
        
        # ★ CALL REALMOVEMENTCALCULATOR ★
        sql = movement_calc.build_retirement_acceleration_sql(filters)
        
        return {
            'sql': sql,
            'template_used': 'retirement_acceleration',
            'calculator_method': 'build_retirement_acceleration_sql'
        }

RealMovementCalculator Methods Called Based on Pattern
Pattern DetectedStep 6 Routes ToRealMovementCalculator Methodretirement_acceleration_route_to_retirement_sql()build_retirement_acceleration_sql(filters)None (single metric: unvested)_route_to_single_metric()build_unvested_shares_sql(filters)None (single metric: vested)_route_to_single_metric()build_vested_shares_sql(filters)None (multiple metrics)_route_to_multi_metric()build_multi_balance_sql(balance_types, filters)None (default)_route_to_default()build_movement_breakdown_sql(filters)

When is Each Method Called?
Method 1: build_retirement_acceleration_sql()
Called When:
pythonif (
    schema_type == 'movement' AND
    query_subtype == 'retirement_acceleration'
):
    movement_calc.build_retirement_acceleration_sql(filters)
Example Queries:

"Which participants are eligible for retirement acceleration?"
"Show retirement eligible employees at Lenovo"
"Participants who can retire and vest early"


Method 2: build_unvested_shares_sql()
Called When:
pythonif (
    schema_type == 'movement' AND
    len(metrics) == 1 AND
    metrics[0] == 'unvested_shares'
):
    movement_calc.build_unvested_shares_sql(filters)
Example Queries:

"How many unvested shares does John have?"
"Show total unvested shares at Lenovo"


Method 3: build_multi_balance_sql()
Called When:
pythonif (
    schema_type == 'movement' AND
    len(metrics) > 1
):
    movement_calc.build_multi_balance_sql(
        balance_types_list=['unvested', 'vested'],
        filters=filters
    )
Example Queries:

"Show John's unveiled and vested shares"
"Give me unvested, vested, and exercisable for all participants"


Timing in the Pipeline
Time    Step    Action
───────────────────────────────────────────────────────────
0ms     Step 1  Pattern detected: "retirement_acceleration"
320ms   Step 2  Classified as PARTICIPANT_LEVEL
500ms   Step 3  Preserved: query_keywords = ["retirement_acceleration"]
650ms   Step 4  Normalized entities
1070ms  Step 5  Set: query_subtype = "retirement_acceleration"
1152ms  Step 6  ★ Call RealMovementCalculator ★
        │
        ├─ 1152ms: Detect schema_type = 'movement'
        ├─ 1153ms: Initialize RealMovementCalculator
        ├─ 1154ms: Check _is_retirement_query() → True
        ├─ 1155ms: Build MovementFilter
        └─ 1156ms: Call build_retirement_acceleration_sql()
                   │
                   ├─ Generate CTE 1 (participant_movements)
                   ├─ Generate CTE 2 (unvested_participant)
                   └─ Generate final SELECT
                   
1219ms  Return SQL (67ms in Step 6)

Summary
QuestionAnswerWhen is RealMovementCalculator called?In Step 6 when schema_type='movement'How does pattern detection connect?Step 6 checks query_subtype from Step 5Which method for retirement?build_retirement_acceleration_sql(filters)When exactly?After pattern check returns True in Step 6What triggers the call?_is_retirement_query(parameters) returns TrueMultiple ways to detect?Yes: query_subtype, query_keywords, special_filtersIs it guaranteed to be called?Only if BOTH schema='movement' AND pattern detected
Key Point: Pattern detection happens in Steps 1-5, but the actual call to RealMovementCalculator.build_retirement_acceleration_sql() happens in Step 6 when the routing logic detects the pattern.2 / 2RetryClaude can make mistakes. Please double-check responses.Equity plan chatbot oct2025 Sonnet 4.5
