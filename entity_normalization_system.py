"""
Entity Normalization System
Converts natural language entities to database values using YAML configuration
"""

import yaml
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncpg
from fuzzywuzzy import fuzz


# =============================================================================
# YAML CONFIGURATION FILE: config/normalization_rules.yaml
# =============================================================================

NORMALIZATION_RULES_YAML = """
# =============================================================================
# Entity Normalization Rules Configuration
# Defines how to convert natural language terms to database values
# =============================================================================

# -----------------------------------------------------------------------------
# STATUS MAPPINGS
# Maps user input terms to database enum values
# -----------------------------------------------------------------------------
status_mappings:
  participant_status:
    canonical_values:
      - active
      - terminated
      - on_leave
      - retired
    
    mappings:
      # Active variations
      active: active
      employed: active
      current: active
      working: active
      
      # Terminated variations
      terminated: terminated
      former: terminated
      ex-employee: terminated
      left: terminated
      departed: terminated
      quit: terminated
      fired: terminated
      
      # On leave variations
      on_leave: on_leave
      on leave: on_leave
      leave: on_leave
      maternity: on_leave
      paternity: on_leave
      sabbatical: on_leave
      
      # Retired variations
      retired: retired
      retirement: retired
  
  vesting_status:
    canonical_values:
      - pending
      - vested
      - forfeited
      - exercised
      - expired
    
    mappings:
      # Pending/Unvested
      pending: pending
      unvested: pending
      not vested: pending
      waiting: pending
      future: pending
      upcoming: pending
      
      # Vested
      vested: vested
      vest: vested
      released: vested
      available: vested
      
      # Forfeited
      forfeited: forfeited
      forfeit: forfeited
      lost: forfeited
      cancelled: forfeited
      canceled: forfeited
      
      # Exercised
      exercised: exercised
      exercise: exercised
      executed: exercised
      
      # Expired
      expired: expired
      lapsed: expired
  
  grant_status:
    canonical_values:
      - active
      - forfeited
      - exercised
      - expired
      - cancelled
    
    mappings:
      active: active
      forfeited: forfeited
      exercised: exercised
      expired: expired
      cancelled: cancelled
      canceled: cancelled

  plan_status:
    canonical_values:
      - active
      - closed
      - suspended
      - pending
    
    mappings:
      active: active
      open: active
      current: active
      closed: closed
      terminated: closed
      ended: closed
      suspended: suspended
      paused: suspended
      pending: pending
      draft: pending

# -----------------------------------------------------------------------------
# PLAN TYPE MAPPINGS
# Maps various ways users refer to plan types
# -----------------------------------------------------------------------------
plan_type_mappings:
  canonical_values:
    - RSU
    - ISO
    - NSO
    - ESPP
    - PSU
    - SAR
    - RSA
  
  mappings:
    # RSU variations
    RSU: RSU
    rsu: RSU
    rsus: RSU
    restricted stock unit: RSU
    restricted stock units: RSU
    restricted stock: RSU
    
    # ISO variations
    ISO: ISO
    iso: ISO
    isos: ISO
    incentive stock option: ISO
    incentive stock options: ISO
    incentive option: ISO
    incentive options: ISO
    
    # NSO variations
    NSO: NSO
    nso: NSO
    nsos: NSO
    NQSO: NSO
    nqso: NSO
    non-qualified stock option: NSO
    non qualified stock option: NSO
    nonqualified stock option: NSO
    non-qualified option: NSO
    
    # ESPP variations
    ESPP: ESPP
    espp: ESPP
    employee stock purchase plan: ESPP
    stock purchase plan: ESPP
    purchase plan: ESPP
    
    # PSU variations
    PSU: PSU
    psu: PSU
    psus: PSU
    performance stock unit: PSU
    performance stock units: PSU
    performance unit: PSU
    performance share: PSU
    
    # SAR variations
    SAR: SAR
    sar: SAR
    sars: SAR
    stock appreciation right: SAR
    stock appreciation rights: SAR
    appreciation right: SAR
    
    # RSA variations
    RSA: RSA
    rsa: RSA
    restricted stock award: RSA
    restricted award: RSA

# -----------------------------------------------------------------------------
# COUNTRY MAPPINGS
# Handles different country name formats and codes
# -----------------------------------------------------------------------------
country_mappings:
  # UK variations
  UK:
    canonical: United Kingdom
    variations:
      - UK
      - uk
      - U.K.
      - United Kingdom
      - GB
      - Great Britain
      - England
      - Scotland
      - Wales
      - Northern Ireland
    db_values: ['United Kingdom', 'UK', 'GB']
  
  # US variations
  US:
    canonical: United States
    variations:
      - US
      - us
      - U.S.
      - USA
      - U.S.A.
      - United States
      - United States of America
      - America
    db_values: ['United States', 'US', 'USA']
  
  # Germany variations
  DE:
    canonical: Germany
    variations:
      - Germany
      - DE
      - Deutschland
    db_values: ['Germany', 'DE']
  
  # France variations
  FR:
    canonical: France
    variations:
      - France
      - FR
    db_values: ['France', 'FR']
  
  # India variations
  IN:
    canonical: India
    variations:
      - India
      - IN
    db_values: ['India', 'IN']
  
  # Canada variations
  CA:
    canonical: Canada
    variations:
      - Canada
      - CA
    db_values: ['Canada', 'CA']

# -----------------------------------------------------------------------------
# REGION MAPPINGS
# Maps countries to regions
# -----------------------------------------------------------------------------
region_mappings:
  EMEA:
    name: Europe, Middle East, and Africa
    countries:
      - United Kingdom
      - Germany
      - France
      - Spain
      - Italy
      - Netherlands
      - Sweden
      - Switzerland
      - Poland
      - UAE
      - Saudi Arabia
      - South Africa
  
  APAC:
    name: Asia Pacific
    countries:
      - India
      - China
      - Japan
      - Singapore
      - Australia
      - New Zealand
      - South Korea
      - Hong Kong
      - Taiwan
      - Thailand
      - Malaysia
  
  AMER:
    name: Americas
    countries:
      - United States
      - Canada
      - Mexico
      - Brazil
      - Argentina
      - Chile
      - Colombia

# -----------------------------------------------------------------------------
# DATE EXPRESSION PATTERNS
# Converts natural language time expressions to date ranges
# -----------------------------------------------------------------------------
date_expression_patterns:
  # Relative expressions (from current date)
  relative:
    - pattern: "next (\\d+) days?"
      type: future_days
      example: "next 30 days"
    
    - pattern: "next (\\d+) weeks?"
      type: future_weeks
      example: "next 4 weeks"
    
    - pattern: "next (\\d+) months?"
      type: future_months
      example: "next 6 months"
    
    - pattern: "past (\\d+) days?"
      type: past_days
      example: "past 90 days"
    
    - pattern: "last (\\d+) days?"
      type: past_days
      example: "last 30 days"
    
    - pattern: "upcoming"
      type: future_months
      value: 12
      example: "upcoming releases"
    
    - pattern: "recent"
      type: past_months
      value: 3
      example: "recent grants"
  
  # Fiscal periods
  fiscal:
    - pattern: "q1 (\\d{4})"
      months: [1, 2, 3]
      example: "Q1 2025"
    
    - pattern: "q2 (\\d{4})"
      months: [4, 5, 6]
      example: "Q2 2025"
    
    - pattern: "q3 (\\d{4})"
      months: [7, 8, 9]
      example: "Q3 2025"
    
    - pattern: "q4 (\\d{4})"
      months: [10, 11, 12]
      example: "Q4 2025"
    
    - pattern: "fy(\\d{4})"
      type: fiscal_year
      example: "FY2025"
  
  # Named periods
  named:
    - pattern: "this year"
      type: current_year
    
    - pattern: "last year"
      type: previous_year
    
    - pattern: "ytd|year to date"
      type: year_to_date
    
    - pattern: "this quarter"
      type: current_quarter
    
    - pattern: "last quarter"
      type: previous_quarter
    
    - pattern: "this month"
      type: current_month
    
    - pattern: "last month"
      type: previous_month

# -----------------------------------------------------------------------------
# METRIC SYNONYMS
# Maps different ways users ask for metrics
# -----------------------------------------------------------------------------
metric_mappings:
  # Count-related
  count:
    variations: [count, number, total number, how many, quantity]
    sql_function: COUNT
  
  participant_count:
    variations:
      - participant count
      - number of participants
      - participant volume
      - employee count
      - headcount
    canonical: participant_count
  
  plan_count:
    variations:
      - plan count
      - number of plans
      - how many plans
    canonical: plan_count
  
  grant_count:
    variations:
      - grant count
      - number of grants
      - award count
      - how many grants
    canonical: grant_count
  
  # Value-related
  total_value:
    variations:
      - total value
      - equity value
      - worth
      - value at current price
    canonical: total_value
  
  # Shares-related
  vested_shares:
    variations:
      - vested shares
      - vested equity
      - released shares
      - available shares
    canonical: vested_shares
  
  unvested_shares:
    variations:
      - unvested shares
      - pending shares
      - future shares
      - shares waiting to vest
    canonical: unvested_shares

# -----------------------------------------------------------------------------
# FUZZY MATCHING SETTINGS
# Controls how closely user input must match to be normalized
# -----------------------------------------------------------------------------
fuzzy_matching:
  enabled: true
  
  # Minimum similarity scores (0-100)
  thresholds:
    company_name: 85    # "TechCorp" vs "Tech Corp Inc"
    person_name: 90     # Higher threshold for people
    department: 80      # "Engineering" vs "Enginering"
    plan_name: 85       # "2023 Equity Plan" vs "2023 Equity Incentive Plan"
  
  # Method: ratio, partial_ratio, token_sort_ratio, token_set_ratio
  method: token_sort_ratio

# -----------------------------------------------------------------------------
# DATABASE LOOKUP STRATEGIES
# Defines how to look up entities in the database
# -----------------------------------------------------------------------------
lookup_strategies:
  clients:
    primary_key: id
    search_fields: [name]
    fuzzy_match: true
    cache_enabled: true
    cache_ttl_seconds: 3600
    
  participants:
    primary_key: id
    search_fields: [name, email, employee_id]
    fuzzy_match: true
    cache_enabled: true
    cache_ttl_seconds: 1800
    
  plans:
    primary_key: id
    search_fields: [plan_name]
    fuzzy_match: true
    cache_enabled: true
    cache_ttl_seconds: 3600

# -----------------------------------------------------------------------------
# IMPLICIT FILTERS
# Default filters applied when not explicitly specified
# -----------------------------------------------------------------------------
implicit_filters:
  # When querying participants without status specified
  default_participant_status: active
  
  # When querying plans without status specified
  default_plan_status: active
  
  # When asking about "grants" without context
  default_grant_status: active
  
  # When asking about vesting without status
  default_vesting_status: pending
  
  # Apply these unless user says "all", "everything", "including terminated"
  override_keywords: [all, everything, including terminated, including closed]
"""


# =============================================================================
# AUTOMATED NORMALIZER CODE
# =============================================================================

@dataclass
class NormalizedValue:
    """Result of normalization"""
    original: str
    normalized: Any
    confidence: float  # 0.0 to 1.0
    method: str  # 'exact', 'fuzzy', 'pattern', 'database_lookup'
    metadata: Dict = None


class EntityNormalizer:
    """Automated entity normalizer using YAML configuration"""
    
    def __init__(self, config_path: str, db_connection: asyncpg.Connection):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.db = db_connection
        self._cache = {}
    
    # -------------------------------------------------------------------------
    # STATUS NORMALIZATION
    # -------------------------------------------------------------------------
    
    def normalize_status(self, status_value: str, status_type: str) -> NormalizedValue:
        """
        Normalize status values (participant_status, vesting_status, etc.)
        
        Args:
            status_value: User input like "active", "vested", "former employee"
            status_type: Type of status - "participant_status", "vesting_status", etc.
        
        Returns:
            NormalizedValue with canonical status
        """
        status_config = self.config['status_mappings'].get(status_type, {})
        mappings = status_config.get('mappings', {})
        
        # Normalize input
        status_lower = status_value.lower().strip()
        
        # Try exact match
        if status_lower in mappings:
            return NormalizedValue(
                original=status_value,
                normalized=mappings[status_lower],
                confidence=1.0,
                method='exact',
                metadata={'status_type': status_type}
            )
        
        # Try fuzzy match
        if self.config['fuzzy_matching']['enabled']:
            best_match = None
            best_score = 0
            
            for key, value in mappings.items():
                score = fuzz.ratio(status_lower, key)
                if score > best_score:
                    best_score = score
                    best_match = value
            
            if best_score >= 80:  # Threshold for status matching
                return NormalizedValue(
                    original=status_value,
                    normalized=best_match,
                    confidence=best_score / 100.0,
                    method='fuzzy',
                    metadata={'status_type': status_type, 'score': best_score}
                )
        
        # No match found - return original
        return NormalizedValue(
            original=status_value,
            normalized=status_value,
            confidence=0.0,
            method='none',
            metadata={'error': 'no_match_found'}
        )
    
    # -------------------------------------------------------------------------
    # PLAN TYPE NORMALIZATION
    # -------------------------------------------------------------------------
    
    def normalize_plan_type(self, plan_type_value: str) -> NormalizedValue:
        """Normalize plan type (RSU, ISO, NSO, etc.)"""
        mappings = self.config['plan_type_mappings']['mappings']
        
        plan_type_lower = plan_type_value.lower().strip()
        
        # Try exact match
        if plan_type_lower in mappings:
            return NormalizedValue(
                original=plan_type_value,
                normalized=mappings[plan_type_lower],
                confidence=1.0,
                method='exact'
            )
        
        # Try fuzzy match
        best_match = None
        best_score = 0
        
        for key, value in mappings.items():
            score = fuzz.ratio(plan_type_lower, key.lower())
            if score > best_score:
                best_score = score
                best_match = value
        
        if best_score >= 85:
            return NormalizedValue(
                original=plan_type_value,
                normalized=best_match,
                confidence=best_score / 100.0,
                method='fuzzy',
                metadata={'score': best_score}
            )
        
        return NormalizedValue(
            original=plan_type_value,
            normalized=plan_type_value,
            confidence=0.0,
            method='none',
            metadata={'error': 'unknown_plan_type'}
        )
    
    # -------------------------------------------------------------------------
    # COUNTRY NORMALIZATION
    # -------------------------------------------------------------------------
    
    def normalize_country(self, country_value: str) -> NormalizedValue:
        """
        Normalize country names and codes
        Returns all possible DB values for SQL IN clause
        """
        country_lower = country_value.lower().strip()
        
        # Search through all country mappings
        for code, country_config in self.config['country_mappings'].items():
            variations = [v.lower() for v in country_config['variations']]
            
            if country_lower in variations:
                return NormalizedValue(
                    original=country_value,
                    normalized=country_config['db_values'],
                    confidence=1.0,
                    method='exact',
                    metadata={
                        'canonical': country_config['canonical'],
                        'code': code
                    }
                )
        
        # Try fuzzy match
        best_match = None
        best_score = 0
        best_config = None
        
        for code, country_config in self.config['country_mappings'].items():
            for variation in country_config['variations']:
                score = fuzz.ratio(country_lower, variation.lower())
                if score > best_score:
                    best_score = score
                    best_match = country_config['db_values']
                    best_config = country_config
        
        if best_score >= 85:
            return NormalizedValue(
                original=country_value,
                normalized=best_match,
                confidence=best_score / 100.0,
                method='fuzzy',
                metadata={
                    'canonical': best_config['canonical'],
                    'score': best_score
                }
            )
        
        # Return original if no match
        return NormalizedValue(
            original=country_value,
            normalized=[country_value],
            confidence=0.0,
            method='none'
        )
    
    # -------------------------------------------------------------------------
    # DATE NORMALIZATION
    # -------------------------------------------------------------------------
    
    def normalize_date_expression(self, date_expr: str) -> NormalizedValue:
        """
        Convert natural language date expressions to ISO date ranges
        
        Examples:
            "next 30 days" → {"start": "2025-09-30", "end": "2025-10-30"}
            "Q4 2025" → {"start": "2025-10-01", "end": "2025-12-31"}
            "this year" → {"start": "2025-01-01", "end": "2025-12-31"}
        """
        date_lower = date_expr.lower().strip()
        today = datetime.now().date()
        
        # Try relative patterns
        for pattern_config in self.config['date_expression_patterns']['relative']:
            pattern = pattern_config['pattern']
            match = re.search(pattern, date_lower)
            
            if match:
                pattern_type = pattern_config['type']
                
                if pattern_type == 'future_days':
                    days = int(match.group(1))
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': today.isoformat(),
                            'end': (today + timedelta(days=days)).isoformat()
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'relative_future', 'days': days}
                    )
                
                elif pattern_type == 'future_weeks':
                    weeks = int(match.group(1))
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': today.isoformat(),
                            'end': (today + timedelta(weeks=weeks)).isoformat()
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'relative_future', 'weeks': weeks}
                    )
                
                elif pattern_type == 'future_months':
                    months = int(match.group(1)) if match.groups() else pattern_config.get('value', 12)
                    end_date = today.replace(month=today.month + months) if today.month + months <= 12 else \
                                today.replace(year=today.year + 1, month=(today.month + months) - 12)
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': today.isoformat(),
                            'end': end_date.isoformat()
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'relative_future', 'months': months}
                    )
                
                elif pattern_type == 'past_days':
                    days = int(match.group(1))
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': (today - timedelta(days=days)).isoformat(),
                            'end': today.isoformat()
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'relative_past', 'days': days}
                    )
        
        # Try fiscal patterns
        for pattern_config in self.config['date_expression_patterns']['fiscal']:
            pattern = pattern_config['pattern']
            match = re.search(pattern, date_lower)
            
            if match:
                year = int(match.group(1))
                months = pattern_config['months']
                
                start_date = datetime(year, months[0], 1).date()
                
                # Last day of last month in quarter
                if months[-1] == 12:
                    end_date = datetime(year, 12, 31).date()
                else:
                    end_date = datetime(year, months[-1] + 1, 1).date() - timedelta(days=1)
                
                return NormalizedValue(
                    original=date_expr,
                    normalized={
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    confidence=1.0,
                    method='pattern',
                    metadata={'pattern_type': 'fiscal_quarter', 'year': year, 'months': months}
                )
        
        # Try named patterns
        for pattern_config in self.config['date_expression_patterns']['named']:
            pattern = pattern_config['pattern']
            if re.search(pattern, date_lower):
                pattern_type = pattern_config['type']
                
                if pattern_type == 'current_year':
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': f"{today.year}-01-01",
                            'end': f"{today.year}-12-31"
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'current_year'}
                    )
                
                elif pattern_type == 'year_to_date':
                    return NormalizedValue(
                        original=date_expr,
                        normalized={
                            'start': f"{today.year}-01-01",
                            'end': today.isoformat()
                        },
                        confidence=1.0,
                        method='pattern',
                        metadata={'pattern_type': 'year_to_date'}
                    )
                
                # Add more named patterns as needed...
        
        # No match found
        return NormalizedValue(
            original=date_expr,
            normalized=None,
            confidence=0.0,
            method='none',
            metadata={'error': 'unrecognized_date_expression'}
        )
    
    # -------------------------------------------------------------------------
    # DATABASE LOOKUPS
    # -------------------------------------------------------------------------
    
    async def normalize_client_name(self, client_name: str, accessible_clients: List[int]) -> NormalizedValue:
        """
        Look up client ID from company name
        Uses fuzzy matching if exact match fails
        """
        # Check cache
        cache_key = f"client:{client_name}:{','.join(map(str, accessible_clients))}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try exact match
        query = """
            SELECT id, name
            FROM clients
            WHERE name ILIKE $1
              AND id = ANY($2)
        """
        result = await self.db.fetchrow(query, client_name, accessible_clients)
        
        if result:
            normalized = NormalizedValue(
                original=client_name,
                normalized=result['id'],
                confidence=1.0,
                method='database_lookup_exact',
                metadata={'matched_name': result['name']}
            )
            self._cache[cache_key] = normalized
            return normalized
        
        # Try fuzzy match
        if self.config['fuzzy_matching']['enabled']:
            query = """
                SELECT id, name
                FROM clients
                WHERE id = ANY($1)
            """
            results = await self.db.fetch(query, accessible_clients)
            
            best_match = None
            best_score = 0
            threshold = self.config['fuzzy_matching']['thresholds']['company_name']
            
            for row in results:
                score = fuzz.token_sort_ratio(client_name.lower(), row['name'].lower())
                if score > best_score:
                    best_score = score
                    best_match = row
            
            if best_match and best_score >= threshold:
                normalized = NormalizedValue(
                    original=client_name,
                    normalized=best_match['id'],
                    confidence=best_score / 100.0,
                    method='database_lookup_fuzzy',
                    metadata={'matched_name': best_match['name'], 'score': best_score}
                )
                self._cache[cache_key] = normalized
                return normalized
        
        # No match
        return NormalizedValue(
            original=client_name,
            normalized=None,
            confidence=0.0,
            method='none',
            metadata={'error': 'client_not_found'}
        )
    
    async def normalize_participant_name(self, participant_name: str, accessible_clients: List[int]) -> List[NormalizedValue]:
        """
        Look up participant ID(s) from name
        May return multiple matches if name is ambiguous
        """
        # Try exact match
        query = """
            SELECT p.id, p.name, p.email, c.name as company_name
            FROM participants p
            JOIN clients c ON p.client_id = c.id
            WHERE p.name ILIKE $1
              AND p.client_id = ANY($2)
            LIMIT 10
        """
        results = await self.db.fetch(query, f"%{participant_name}%", accessible_clients)
        
        if results:
            matches = []
            for row in results:
                matches.append(NormalizedValue(
                    original=participant_name,
                    normalized=row['id'],
                    confidence=1.0 if row['name'].lower() == participant_name.lower() else 0.9,
                    method='database_lookup',
                    metadata={
                        'name': row['name'],
                        'email': row['email'],
                        'company': row['company_name']
                    }
                ))
            return matches
        
        # Try fuzzy match
        if self.config['fuzzy_matching']['enabled']:
            query = """
                SELECT p.id, p.name, p.email, c.name as company_name
                FROM participants p
                JOIN clients c ON p.client_id = c.id
                WHERE p.client_id = ANY($1)
                LIMIT 100
            """
            all_results = await self.db.fetch(query, accessible_clients)
            
            matches = []
            threshold = self.config['fuzzy_matching']['thresholds']['person_name']
            
            for row in all_results:
                score = fuzz.ratio(participant_name.lower(), row['name'].lower())
                if score >= threshold:
                    matches.append(NormalizedValue(
                        original=participant_name,
                        normalized=row['id'],
                        confidence=score / 100.0,
                        method='database_lookup_fuzzy',
                        metadata={
                            'name': row['name'],
                            'email': row['email'],
                            'company': row['company_name'],
                            'score': score
                        }
                    ))
            
            # Sort by confidence
            matches.sort(key=lambda x: x.confidence, reverse=True)
            return matches[:5]  # Return top 5 matches
        
        return []
    
    # -------------------------------------------------------------------------
    # METRIC NORMALIZATION
    # -------------------------------------------------------------------------
    
    def normalize_metric(self, metric_expr: str) -> NormalizedValue:
        """Normalize metric expressions to canonical metric names"""
        metric_lower = metric_expr.lower().strip()
        
        for metric_name, metric_config in self.config['metric_mappings'].items():
            if 'variations' in metric_config:
                variations = [v.lower() for v in metric_config['variations']]
                if metric_lower in variations:
                    return NormalizedValue(
                        original=metric_expr,
                        normalized=metric_config.get('canonical', metric_name),
                        confidence=1.0,
                        method='exact',
                        metadata={'metric_type': metric_name}
                    )
        
        # Try fuzzy match
        best_match = None
        best_score = 0
        
        for metric_name, metric_config in self.config['metric_mappings'].items():
            if 'variations' in metric_config:
                for variation in metric_config['variations']:
                    score = fuzz.ratio(metric_lower, variation.lower())
                    if score > best_score:
                        best_score = score
                        best_match = metric_config.get('canonical', metric_name)
        
        if best_score >= 85:
            return NormalizedValue(
                original=metric_expr,
                normalized=best_match,
                confidence=best_score / 100.0,
                method='fuzzy',
                metadata={'score': best_score}
            )
        
        return NormalizedValue(
            original=metric_expr,
            normalized=metric_expr,
            confidence=0.0,
            method='none'
        )
    
    # -------------------------------------------------------------------------
    # BATCH NORMALIZATION
    # -------------------------------------------------------------------------
    
    async def normalize_entities(self, raw_entities: Dict, user_context: Dict) -> Dict:
        """
        Normalize all entities in one pass
        
        Args:
            raw_entities: Dict from Step 3 (Entity Extraction)
            user_context: User context with accessible_clients, etc.
        
        Returns:
            Dict of normalized entities ready for SQL generation
        """
        normalized = {}
        
        # Normalize statuses
        if raw_entities.get('statuses'):
            normalized['status_filters'] = {}
            for status in raw_entities['statuses']:
                # Infer status type from context
                result = self.normalize_status(status, 'participant_status')
                if result.confidence > 0.7:
                    normalized['status_filters']['participant_status'] = result.normalized
        
        # Normalize countries
        if raw_entities.get('countries'):
            country_values = []
            for country in raw_entities['countries']:
                result = self.normalize_country(country)
                if result.confidence > 0.8:
                    country_values.extend(result.normalized)
            normalized['country_filter'] = list(set(country_values))
        
        # Normalize date expressions
        if raw_entities.get('date_expressions'):
            for date_expr in raw_entities['date_expressions']:
                result = self.normalize_date_expression(date_expr)
                if result.confidence > 0.9:
                    normalized['date_range'] = result.normalized
        
        # Normalize plan types
        if raw_entities.get('plan_types'):
            plan_types = []
            for plan_type in raw_entities['plan_types']:
                result = self.normalize_plan_type(plan_type)
                if result.confidence > 0.8:
                    plan_types.append(result.normalized)
            normalized['plan_types'] = list(set(plan_types))
        
        # Lookup client IDs
        if raw_entities.get('client_names'):
            client_ids = []
            for client_name in raw_entities['client_names']:
                result = await self.normalize_client_name(
                    client_name,
                    user_context['accessible_clients']
                )
                if result.confidence > 0.8:
                    client_ids.append(result.normalized)
            normalized['client_ids'] = client_ids
        
        # Lookup participant IDs
        if raw_entities.get('participant_names'):
            participant_matches = []
            for participant_name in raw_entities['participant_names']:
                matches = await self.normalize_participant_name(
                    participant_name,
                    user_context['accessible_clients']
                )
                if len(matches) == 1 and matches[0].confidence > 0.9:
                    participant_matches.append(matches[0].normalized)
                elif len(matches) > 1:
                    # Ambiguous - need clarification
                    normalized['needs_clarification'] = True
                    normalized['clarification_options'] = [
                        f"{m.metadata['name']} ({m.metadata['email']}) at {m.metadata['company']}"
                        for m in matches
                    ]
            if participant_matches:
                normalized['participant_ids'] = participant_matches
        
        # Normalize metrics
        if raw_entities.get('metrics'):
            metric_names = []
            for metric in raw_entities['metrics']:
                result = self.normalize_metric(metric)
                if result.confidence > 0.8:
                    metric_names.append(result.normalized)
            normalized['metrics'] = metric_names
        
        # Add accessible clients from user context
        normalized['accessible_clients'] = user_context['accessible_clients']
        
        # Apply implicit filters
        self._apply_implicit_filters(normalized, raw_entities)
        
        return normalized
    
    def _apply_implicit_filters(self, normalized: Dict, raw_entities: Dict):
        """Apply default filters based on configuration"""
        implicit = self.config['implicit_filters']
        
        # Check for override keywords
        query_text = str(raw_entities).lower()
        override_keywords = implicit['override_keywords']
        has_override = any(kw in query_text for kw in override_keywords)
        
        if not has_override:
            # Apply defaults if not already set
            if 'status_filters' not in normalized:
                normalized['status_filters'] = {}
            
            if 'participant_status' not in normalized.get('status_filters', {}):
                normalized['status_filters']['participant_status'] = implicit['default_participant_status']
            
            if 'plan_status' not in normalized.get('status_filters', {}):
                normalized['status_filters']['plan_status'] = implicit['default_plan_status']


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example of how to use the normalizer"""
    
    # 1. Save YAML config
    with open('config/normalization_rules.yaml', 'w') as f:
        f.write(NORMALIZATION_RULES_YAML)
    
    # 2. Initialize normalizer
    db = await asyncpg.connect("postgresql://localhost/equity_db")
    normalizer = EntityNormalizer('config/normalization_rules.yaml', db)
    
    # 3. Example: Normalize various entities
    
    # Status normalization
    result = normalizer.normalize_status("former employee", "participant_status")
    print(f"Status: {result.original} → {result.normalized} (confidence: {result.confidence})")
    
    # Date normalization
    result = normalizer.normalize_date_expression("next 30 days")
    print(f"Date: {result.original} → {result.normalized}")
    
    # Country normalization
    result = normalizer.normalize_country("UK")
    print(f"Country: {result.original} → {result.normalized}")
    
    # Client lookup
    result = await normalizer.normalize_client_name("TechCorp", [1, 5, 12, 18, 23])
    print(f"Client: {result.original} → ID {result.normalized}")
    
    # 4. Full batch normalization (as used in Step 4)
    raw_entities = {
        'client_names': ['TechCorp Inc'],
        'statuses': ['active', 'vested'],
        'date_expressions': ['next 30 days'],
        'countries': ['UK'],
        'plan_types': ['RSU', 'stock options'],
        'metrics': ['participant count', 'number of plans']
    }
    
    user_context = {
        'accessible_clients': [1, 5, 12, 18, 23, 29, 31, 44, 52, 67, 71, 88, 93, 99, 101]
    }
    
    normalized = await normalizer.normalize_entities(raw_entities, user_context)
    
    print("\nFull normalization result:")
    print(yaml.dump(normalized, default_flow_style=False))
    
    await db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
