How Pattern Detection Works Now
Looking at the original documents, pattern detection happens entirely through LLM prompts:
Step 1: Understanding Prompt
txt# From: prompts/understanding_prompt.txt

You are an expert at understanding natural language queries...

BUSINESS CONTEXT - Equity Compensation Terminology:
{vocabulary}

USER QUERY: "{query}"

INSTRUCTIONS:
1. CORRECT TYPOS AND GRAMMAR
2. DETERMINE QUERY CATEGORY
3. IDENTIFY INTENT
4. ASSESS COMPLEXITY

OUTPUT FORMAT (JSON only):
{
  "corrected_query": "...",
  "intent": "...",
  "query_category": "AGGREGATE|DETAIL",
  "complexity": "simple|medium|complex",
  "requires_clarification": false
}
Notice: No special_query_type field in the original!
Step 3: Entity Extraction
txt# From: prompts/entity_extraction_prompt.txt

Extract entities from query.

ENTITY TYPES TO EXTRACT:
- client_names
- participant_names
- plan_types
- statuses
- date_expressions
- metrics

OUTPUT:
{
  "entities": {...},
  "reasoning": "..."
}
Notice: No query_keywords field for special patterns!
Step 6: SQL Generation
The original step6_template_population.py has some routing logic, but it's based on query_type, not special patterns:
python# Current routing (simplified)
if query_type == "CLIENT_LEVEL":
    return self.build_client_level_query(...)
elif query_type == "PARTICIPANT_LEVEL":
    return self.build_participant_level_query(...)
elif query_type == "VESTING_SCHEDULE":
    return self.build_vesting_schedule_query(...)
Problem: No explicit handling for "retirement acceleration" pattern!

Proposed Enhancement: Add Pattern Detection
To handle special patterns like "retirement acceleration", you need to ADD:
New Files to Create
equity-chatbot/
├── utils/
│   └── pattern_detector.py        # ← NEW FILE
│
├── config/
│   └── special_query_patterns.yaml # ← NEW FILE
│
└── prompts/
    └── understanding_prompt.txt    # ← ENHANCE EXISTING

File 1: utils/pattern_detector.py (NEW)
Purpose
Pre-process queries to detect special patterns BEFORE the LLM call
Location
equity-chatbot/
└── utils/
    ├── __init__.py
    └── pattern_detector.py  # ← Create this
Code
python"""
Pattern Detector for Special Query Types

Detects patterns that require specialized SQL templates:
- Retirement acceleration
- Blackout periods
- Insider trading compliance
- Performance vesting
"""

from typing import Dict, List, Optional
import re


class SpecialPatternDetector:
    """
    Detects special query patterns using keyword matching
    """
    
    PATTERNS = {
        'retirement_acceleration': {
            'keywords': [
                'retirement acceleration',
                'retirement eligible',
                'retirement eligibility',
                'retire early vesting',
                'accelerate upon retirement'
            ],
            'context_words': [
                'eligible', 'eligibility', 'acceleration', 'vest', 'unvested'
            ],
            'template_name': 'retirement_acceleration',
            'requires_tables': ['bi_grant_award_latest'],
            'requires_fields': ['retirement_eligibility_dt']
        },
        
        'blackout_period': {
            'keywords': [
                'blackout period',
                'trading window',
                'blackout',
                'cannot trade',
                "can't trade"
            ],
            'context_words': ['trade', 'sell', 'exercise'],
            'template_name': 'blackout_period_check',
            'requires_tables': ['blackout_periods']
        },
        
        'insider_compliance': {
            'keywords': [
                'insider',
                'section 16',
                'beneficial ownership',
                '10% owner',
                'form 4'
            ],
            'context_words': ['insider', 'compliance', 'reporting'],
            'template_name': 'insider_compliance',
            'requires_tables': ['insider_designations']
        }
    }
    
    def detect(self, query: str) -> Dict:
        """
        Detect special patterns in query
        
        Args:
            query: User's natural language query
            
        Returns:
            {
                'pattern_detected': bool,
                'pattern_type': str | None,
                'confidence': float,
                'matched_keywords': List[str],
                'reasoning': str,
                'template_name': str | None
            }
        """
        query_lower = query.lower()
        
        for pattern_type, pattern_config in self.PATTERNS.items():
            # Check for keyword matches
            matched_keywords = []
            
            for keyword in pattern_config['keywords']:
                if keyword in query_lower:
                    matched_keywords.append(keyword)
            
            # If keywords found, calculate confidence
            if matched_keywords:
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
                    'reasoning': f"Detected '{pattern_type}' pattern. Matched: {', '.join(matched_keywords)}",
                    'template_name': pattern_config['template_name'],
                    'requires_tables': pattern_config.get('requires_tables', []),
                    'requires_fields': pattern_config.get('requires_fields', [])
                }
        
        # No pattern detected
        return {
            'pattern_detected': False,
            'pattern_type': None,
            'confidence': 0.0,
            'matched_keywords': [],
            'reasoning': 'No special patterns detected',
            'template_name': None
        }
    
    def _calculate_confidence(self, query: str, pattern_config: Dict, 
                             matched_keywords: List[str]) -> float:
        """Calculate confidence score for pattern match"""
        
        confidence = 0.0
        
        # Base confidence from keyword matches
        # Each exact keyword match = 0.40
        confidence += 0.40 * len(matched_keywords)
        
        # Bonus for context words
        context_words = pattern_config.get('context_words', [])
        context_matches = sum(1 for word in context_words if word in query)
        confidence += 0.10 * context_matches
        
        # Bonus for exact phrase match (not just word match)
        for keyword in matched_keywords:
            if keyword in query:  # Exact phrase
                confidence += 0.20
                break
        
        # Cap at 0.99
        return min(confidence, 0.99)

File 2: config/special_query_patterns.yaml (NEW)
Purpose
Configuration for special patterns (cleaner than hardcoding in Python)
Location
equity-chatbot/
└── config/
    ├── entity_schema.yaml
    ├── business_vocabulary.yaml
    └── special_query_patterns.yaml  # ← Create this
Code
yaml# Special Query Patterns Configuration
# Defines patterns that require specialized SQL templates

patterns:
  
  retirement_acceleration:
    description: "Participants eligible for retirement acceleration"
    
    keywords:
      - "retirement acceleration"
      - "retirement eligible"
      - "retirement eligibility"
      - "retire early vesting"
      - "accelerate upon retirement"
    
    context_words:
      - "eligible"
      - "eligibility" 
      - "acceleration"
      - "vest"
      - "unvested"
    
    database_requirements:
      tables:
        - bi_grant_award_latest
        - bi_fact_movement
        - bi_movement_balance_mapping
      
      critical_fields:
        - retirement_eligibility_dt
      
      filters:
        - "retirement_eligibility_dt IS NOT NULL"
        - "unvested_shares > 0"
    
    sql_template: "retirement_acceleration.sql"
    query_type_override: "PARTICIPANT_LEVEL"
    expected_execution_time_ms: 700
    
    example_queries:
      - "Which participants are eligible for retirement acceleration?"
      - "Show retirement eligible employees at Lenovo"
      - "Who can retire and vest their shares early?"
  
  blackout_period:
    description: "Trading blackout period checks"
    
    keywords:
      - "blackout period"
      - "trading window"
      - "blackout"
      - "cannot trade"
      - "can't trade"
    
    database_requirements:
      tables:
        - blackout_periods
    
    sql_template: "blackout_period_check.sql"
    
  insider_compliance:
    description: "Insider trading compliance queries"
    
    keywords:
      - "insider"
      - "section 16"
      - "beneficial ownership"
      - "10% owner"
    
    database_requirements:
      tables:
        - insider_designations
    
    sql_template: "insider_compliance.sql"

# Detection Configuration
detection:
  method: "keyword_matching"  # Could add: llm_only, hybrid
  
  confidence_thresholds:
    high: 0.85    # Automatically use special template
    medium: 0.60  # Ask user for confirmation
    low: 0.40     # Ignore pattern
  
  keyword_weights:
    exact_phrase: 0.40
    context_word: 0.10
    phrase_bonus: 0.20

How to Integrate: Modify Step 1
File: steps/step1_understanding.py (MODIFY EXISTING)
Current Code (Simplified):
pythonclass QueryUnderstandingStep:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def execute(self, user_query: str) -> Dict:
        prompt = self._build_prompt(user_query)
        response = await self.llm.call(prompt)
        return response
Enhanced Code (Add Pattern Detection):
pythonfrom utils.pattern_detector import SpecialPatternDetector  # ← NEW IMPORT

class QueryUnderstandingStep:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.pattern_detector = SpecialPatternDetector()  # ← NEW
    
    async def execute(self, user_query: str) -> Dict:
        # ============================================
        # NEW: Detect special patterns BEFORE LLM call
        # ============================================
        pattern_result = self.pattern_detector.detect(user_query)
        
        # Build prompt (include pattern hint for LLM)
        prompt = self._build_prompt(user_query, pattern_result)
        
        # Call LLM
        response = await self.llm.call(prompt)
        
        # ============================================
        # NEW: Merge pattern detection with LLM output
        # ============================================
        if pattern_result['pattern_detected']:
            response['special_query_type'] = pattern_result['pattern_type']
            response['special_pattern_confidence'] = pattern_result['confidence']
            response['matched_keywords'] = pattern_result['matched_keywords']
            response['template_name'] = pattern_result['template_name']
        
        return response
    
    def _build_prompt(self, user_query: str, pattern_result: Dict = None) -> str:
        """Build prompt with optional pattern hint"""
        
        prompt = f"""
You are an expert at understanding equity compensation queries.

USER QUERY: "{user_query}"
"""
        
        # ============================================
        # NEW: Add pattern hint if detected
        # ============================================
        if pattern_result and pattern_result['pattern_detected']:
            prompt += f"""

PATTERN PRE-DETECTION:
A special query pattern was detected by keyword analysis:
- Pattern Type: {pattern_result['pattern_type']}
- Confidence: {pattern_result['confidence']}
- Matched Keywords: {pattern_result['matched_keywords']}

Please confirm or correct this pattern detection in your output.
"""
        
        prompt += """

INSTRUCTIONS:
1. Correct typos and grammar
2. Determine query category (AGGREGATE or DETAIL)
3. If special pattern detected, include in output

OUTPUT (JSON):
{
  "corrected_query": "...",
  "query_category": "AGGREGATE|DETAIL",
  "intent": "...",
  "special_query_type": "retirement_acceleration|blackout_period|insider_compliance|null",
  "special_pattern_confidence": 0.95
}
"""
        
        return prompt

Which Step Uses It?
Answer: Step 1 (Query Understanding)
Query Flow with Pattern Detector:

USER INPUT: "Which participants for lenevo are eligible for retirement acceleration?"
    ↓
┌─────────────────────────────────────────────┐
│ STEP 1: Query Understanding                 │
│                                             │
│ 1a. Pattern Detector (NEW)                 │
│     └─ utils/pattern_detector.py           │
│     └─ Keyword match: "retirement..."      │
│     └─ Returns: pattern_detected=True      │
│                                             │
│ 1b. Build LLM Prompt                        │
│     └─ Include pattern hint                 │
│                                             │
│ 1c. Call LLM                                │
│     └─ LLM confirms pattern                 │
│                                             │
│ 1d. Merge Results                           │
│     └─ Code detection + LLM output         │
│                                             │
│ OUTPUT: {                                   │
│   "special_query_type": "retirement_...",   │
│   "confidence": 0.95                        │
│ }                                           │
└─────────────────────────────────────────────┘
    ↓
Step 2: Classification (uses special_query_type)
    ↓
Step 3: Entity Extraction (preserves pattern)
    ↓
Step 5: Parameter Extraction (sets template flag)
    ↓
Step 6: SQL Generation (routes to special template)

Summary
QuestionAnswerIs pattern_detector.py new?YES - Not in original docs, needs to be createdWhere does it go?equity-chatbot/utils/pattern_detector.pyWhich step uses it?Step 1: Query UnderstandingWhen is it called?BEFORE the LLM call in Step 1Why add it?Pre-filter patterns for efficiency, provide hints to LLMIs it required?NO - You could do all detection in LLM prompts, but pattern_detector is faster and more explicit

Alternative: LLM-Only Detection
If you DON'T want to create pattern_detector.py, you can do ALL detection in the LLM prompt:
Option 1: With Pattern Detector (Recommended)

✅ Fast keyword pre-screening
✅ Deterministic pattern matching
✅ Clear audit trail
✅ Less LLM token usage
❌ More code to maintain

Option 2: LLM-Only (Simpler)

✅ Simpler architecture
✅ Less code
✅ LLM handles all edge cases
❌ Slower (every query calls LLM)
❌ Less deterministic
❌ Higher token costs

For retirement queries specifically, either approach works. The pattern detector is beneficial when you have many special patterns to detect.2 / 2RetryClaude can make mistakes. Please double-check responses.
