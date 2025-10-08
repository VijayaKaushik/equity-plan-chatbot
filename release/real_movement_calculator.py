# =================================================================
# FILE: builders/real_movement_calculator.py
# Movement Calculator for bi_fact_movement + bi_movement_balance_mapping
# =================================================================
"""
Real MovementCalculator for Star Schema

Schema:
- bi_fact_movement (fact table) with share_units
- bi_movement_balance_mapping (dimension) with balance type coefficients
- Join on (movement_type, movement_sub_type, movement_sub_sub_type)
- Calculate: share_units * balance_type_coefficient
"""

import yaml
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BalanceType:
    """Represents a balance type column from bi_movement_balance_mapping"""
    column_name: str
    description: str
    typical_use: str


@dataclass
class MovementFilter:
    """Filters for movement queries"""
    participant_hub_key: Optional[str] = None
    participant_hub_keys: Optional[List[str]] = None
    grant_award_hub_key: Optional[str] = None
    grant_award_hub_keys: Optional[List[str]] = None
    client_hub_key: Optional[str] = None
    accessible_client_keys: Optional[List[str]] = None
    movement_type: Optional[str] = None
    movement_types: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    has_retirement_eligibility: Optional[bool] = None
    retirement_date_range: Optional[Dict[str, str]] = None


class RealMovementCalculator:
    """
    SQL builder for bi_fact_movement + bi_movement_balance_mapping schema
    
    Key pattern:
        SUM(fm.share_units * mbm.[balance_type_column])
    """
    
    def __init__(self, config_path: str = 'config'):
        """
        Initialize calculator with config files
        
        Args:
            config_path: Path to config directory
        """
        self.config_path = Path(config_path)
        self.entity_schema = self._load_entity_schema()
        self.metrics_schema = self._load_metrics_schema()
        self.balance_types = self._parse_balance_types()
    
    def _load_entity_schema(self) -> Dict:
        """Load entity schema from YAML"""
        schema_file = self.config_path / 'entity_schema.yaml'
        with open(schema_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_metrics_schema(self) -> Dict:
        """Load metrics schema from YAML"""
        metrics_file = self.config_path / 'metrics_schema.yaml'
        with open(metrics_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _parse_balance_types(self) -> List[BalanceType]:
        """Parse balance types from entity schema"""
        balance_config = self.entity_schema.get('balance_types', {}).get('common_balance_types', [])
        
        return [
            BalanceType(
                column_name=bt['column'],
                description=bt['description'],
                typical_use=bt['typical_use']
            )
            for bt in balance_config
        ]
    
    def get_balance_type_columns(self, balance_types: List[str]) -> List[str]:
        """
        Get column names for specific balance types
        
        Args:
            balance_types: List of balance type names (e.g., ['unveiled', 'vested'])
        
        Returns:
            List of column names
        """
        return [
            bt.column_name 
            for bt in self.balance_types 
            if bt.column_name in balance_types
        ]
    
    def build_balance_calculation(
        self, 
        balance_types: List[str],
        table_alias_fact: str = 'fm',
        table_alias_mapping: str = 'mbm'
    ) -> str:
        """
        Build SQL expression for calculating shares from movements
        
        Args:
            balance_types: List of balance types ['unveiled', 'vested', 'granted']
            table_alias_fact: Alias for bi_fact_movement table
            table_alias_mapping: Alias for bi_movement_balance_mapping table
        
        Returns:
            SQL expression: SUM(fm.share_units * mbm.balance_column)
        
        Example:
            >>> calc = RealMovementCalculator()
            >>> calc.build_balance_calculation(['unveiled'])
            'SUM(fm.share_units * mbm.unveiled)'
        """
        if len(balance_types) == 1:
            # Single balance type
            return f"SUM({table_alias_fact}.share_units * {table_alias_mapping}.{balance_types[0]})"
        else:
            # Multiple balance types - sum them
            balance_sum = ' + '.join([
                f"COALESCE({table_alias_mapping}.{bt}, 0)"
                for bt in balance_types
            ])
            return f"SUM({table_alias_fact}.share_units * ({balance_sum}))"
    
    def build_composite_join(
        self,
        fact_alias: str = 'fm',
        mapping_alias: str = 'mbm'
    ) -> str:
        """
        Build the composite key join between fact and mapping tables
        
        Returns:
            JOIN clause string
        """
        return f"""INNER JOIN bi_movement_balance_mapping {mapping_alias}
    ON {fact_alias}.movement_type = {mapping_alias}.movement_type
    AND {fact_alias}.movement_sub_type = {mapping_alias}.movement_sub_type
    AND {fact_alias}.movement_sub_sub_type = {mapping_alias}.movement_sub_sub_type"""
    
    def build_where_clause(self, filters: MovementFilter) -> str:
        """
        Build WHERE clause from filters
        
        Args:
            filters: MovementFilter object
        
        Returns:
            WHERE clause string
        """
        conditions = []
        
        # Participant filters
        if filters.participant_hub_key:
            conditions.append(f"fm.participant_hub_key = '{filters.participant_hub_key}'")
        elif filters.participant_hub_keys:
            keys = "', '".join(filters.participant_hub_keys)
            conditions.append(f"fm.participant_hub_key IN ('{keys}')")
        
        # Grant filters
        if filters.grant_award_hub_key:
            conditions.append(f"fm.grant_award_hub_key = '{filters.grant_award_hub_key}'")
        elif filters.grant_award_hub_keys:
            keys = "', '".join(filters.grant_award_hub_keys)
            conditions.append(f"fm.grant_award_hub_key IN ('{keys}')")
        
        # Client filters
        if filters.client_hub_key:
            conditions.append(f"fm.client_hub_key = '{filters.client_hub_key}'")
        elif filters.accessible_client_keys:
            keys = "', '".join(filters.accessible_client_keys)
            conditions.append(f"fm.client_hub_key IN ('{keys}')")
        
        # Movement type filters
        if filters.movement_type:
            conditions.append(f"fm.movement_type = '{filters.movement_type}'")
        elif filters.movement_types:
            types = "', '".join(filters.movement_types)
            conditions.append(f"fm.movement_type IN ('{types}')")
        
        # Date range filters
        if filters.date_range:
            if filters.date_range.get('start'):
                conditions.append(f"fm.movement_date >= '{filters.date_range['start']}'")
            if filters.date_range.get('end'):
                conditions.append(f"fm.movement_date <= '{filters.date_range['end']}'")
        
        # Retirement eligibility filter
        if filters.has_retirement_eligibility:
            conditions.append("gal.retirement_eligibility_dt IS NOT NULL")
        
        if filters.retirement_date_range:
            if filters.retirement_date_range.get('start'):
                conditions.append(f"gal.retirement_eligibility_dt >= '{filters.retirement_date_range['start']}'")
            if filters.retirement_date_range.get('end'):
                conditions.append(f"gal.retirement_eligibility_dt <= '{filters.retirement_date_range['end']}'")
        
        if conditions:
            return "WHERE " + "\n    AND ".join(conditions)
        return ""
    
    def build_unvested_shares_sql(
        self,
        filters: Optional[MovementFilter] = None
    ) -> str:
        """
        Build SQL for unvested shares calculation
        
        Args:
            filters: MovementFilter with criteria
        
        Returns:
            Complete SQL query
        """
        filters = filters or MovementFilter()
        
        calc_expr = self.build_balance_calculation(['unveiled'])
        join_clause = self.build_composite_join()
        where_clause = self.build_where_clause(filters)
        
        sql = f"""SELECT {calc_expr} as unveiled_shares
FROM bi_fact_movement fm
{join_clause}"""
        
        if where_clause:
            sql += f"\n{where_clause}"
        
        return sql
    
    def build_vested_shares_sql(
        self,
        filters: Optional[MovementFilter] = None
    ) -> str:
        """Build SQL for vested shares"""
        filters = filters or MovementFilter()
        
        calc_expr = self.build_balance_calculation(['vested'])
        join_clause = self.build_composite_join()
        where_clause = self.build_where_clause(filters)
        
        sql = f"""SELECT {calc_expr} as vested_shares
FROM bi_fact_movement fm
{join_clause}"""
        
        if where_clause:
            sql += f"\n{where_clause}"
        
        return sql
    
    def build_participant_balance_sql(
        self,
        balance_types: List[str],
        filters: Optional[MovementFilter] = None,
        include_details: bool = True
    ) -> str:
        """
        Build SQL for participant balances
        
        Args:
            balance_types: Which balance types to calculate
            filters: MovementFilter with criteria
            include_details: Include participant name, email, etc.
        
        Returns:
            SQL query grouped by participant
        """
        filters = filters or MovementFilter()
        
        calc_expr = self.build_balance_calculation(balance_types)
        join_clause = self.build_composite_join()
        where_clause = self.build_where_clause(filters)
        
        # Build SELECT fields
        select_fields = ["pd.participant_hub_key"]
        if include_details:
            select_fields.extend([
                "pd.participant_name",
                "pd.email",
                "pd.department",
                "pd.country"
            ])
        
        balance_name = '_'.join(balance_types) + '_shares'
        select_fields.append(f"{calc_expr} as {balance_name}")
        
        sql = f"""SELECT 
    {',\n    '.join(select_fields)}
FROM bi_fact_movement fm
{join_clause}
INNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'"""
        
        if where_clause:
            sql += f"\n{where_clause}"
        
        # GROUP BY
        group_fields = ["pd.participant_hub_key"]
        if include_details:
            group_fields.extend([
                "pd.participant_name",
                "pd.email",
                "pd.department",
                "pd.country"
            ])
        sql += f"\nGROUP BY {', '.join(group_fields)}"
        sql += f"\nORDER BY {balance_name} DESC"
        
        return sql
    
    def build_multi_balance_sql(
        self,
        balance_types_list: List[str],
        filters: Optional[MovementFilter] = None,
        group_by_participant: bool = False
    ) -> str:
        """
        Build SQL with multiple balance calculations
        
        Args:
            balance_types_list: List of balance types ['unveiled', 'vested', 'granted']
            filters: MovementFilter
            group_by_participant: Group by participant or aggregate
        
        Returns:
            SQL with multiple balance columns
        """
        filters = filters or MovementFilter()
        
        join_clause = self.build_composite_join()
        where_clause = self.build_where_clause(filters)
        
        # Build SELECT fields
        select_fields = []
        
        if group_by_participant:
            select_fields.extend([
                "pd.participant_hub_key",
                "pd.participant_name",
                "pd.email"
            ])
        
        # Add each balance type calculation
        for balance_type in balance_types_list:
            calc_expr = self.build_balance_calculation([balance_type])
            select_fields.append(f"{calc_expr} as {balance_type}_shares")
        
        sql = f"""SELECT 
    {',\n    '.join(select_fields)}
FROM bi_fact_movement fm
{join_clause}"""
        
        if group_by_participant:
            sql += """\nINNER JOIN bi_participant_detail pd
    ON fm.participant_hub_key = pd.participant_hub_key
    AND pd.is_latest = 'b1'"""
        
        if where_clause:
            sql += f"\n{where_clause}"
        
        if group_by_participant:
            sql += "\nGROUP BY pd.participant_hub_key, pd.participant_name, pd.email"
            sql += "\nORDER BY unveiled_shares DESC"
        
        return sql
    
    def build_retirement_acceleration_sql(
        self,
        filters: Optional[MovementFilter] = None
    ) -> str:
        """
        Build SQL for retirement acceleration eligibility
        Matches the pattern from your example query
        
        Returns:
            Complete CTE-based query
        """
        filters = filters or MovementFilter()
        
        # Build WHERE clause for main CTE
        where_conditions = []
        if filters.client_hub_key:
            where_conditions.append(f"fm.client_hub_key = '{filters.client_hub_key}'")
        elif filters.accessible_client_keys:
            keys = "', '".join(filters.accessible_client_keys)
            where_conditions.append(f"fm.client_hub_key IN ('{keys}')")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        sql = f"""WITH participant_movements AS (
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
    {where_clause}
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
    up.participant_hub_key,
    up.retirement_eligibility_dt,
    up.unveiled_shares,
    pd.participant_name,
    pd.email,
    pd.department,
    pd.country
FROM unveiled_participant up
INNER JOIN bi_participant_detail pd
    ON pd.participant_hub_key = up.participant_hub_key
    AND pd.is_latest = 'b1'
WHERE up.unveiled_shares > 0
ORDER BY up.unveiled_shares DESC"""
        
        return sql
    
    def build_movement_breakdown_sql(
        self,
        filters: Optional[MovementFilter] = None
    ) -> str:
        """
        Build SQL showing breakdown by movement type
        
        Returns:
            SQL with movement type breakdown
        """
        filters = filters or MovementFilter()
        
        join_clause = self.build_composite_join()
        where_clause = self.build_where_clause(filters)
        
        sql = f"""SELECT 
    fm.movement_type,
    fm.movement_sub_type,
    fm.movement_sub_sub_type,
    COUNT(*) as movement_count,
    SUM(fm.share_units * mbm.granted) as granted_shares,
    SUM(fm.share_units * mbm.unveiled) as unveiled_shares,
    SUM(fm.share_units * mbm.vested) as vested_shares,
    SUM(fm.share_units * mbm.exercisable) as exercisable_shares,
    SUM(fm.share_units * mbm.forfeited) as forfeited_shares
FROM bi_fact_movement fm
{join_clause}"""
        
        if where_clause:
            sql += f"\n{where_clause}"
        
        sql += """
GROUP BY 
    fm.movement_type,
    fm.movement_sub_type,
    fm.movement_sub_sub_type
ORDER BY movement_count DESC"""
        
        return sql


# =================================================================
# Usage Examples
# =================================================================

def example_usage():
    """Examples using RealMovementCalculator"""
    
    calc = RealMovementCalculator(config_path='config')
    
    print("=" * 70)
    print("EXAMPLE 1: Unvested shares for specific participant")
    print("=" * 70)
    
    filters = MovementFilter(
        participant_hub_key='PRT00000000000000000042',
        client_hub_key='CLNT00000000000000000002'
    )
    sql = calc.build_unvested_shares_sql(filters)
    print(sql)
    print()
    
    print("=" * 70)
    print("EXAMPLE 2: Multiple balances by participant")
    print("=" * 70)
    
    filters = MovementFilter(
        client_hub_key='CLNT00000000000000000002'
    )
    sql = calc.build_multi_balance_sql(
        balance_types_list=['unveiled', 'vested', 'exercisable'],
        filters=filters,
        group_by_participant=True
    )
    print(sql)
    print()
    
    print("=" * 70)
    print("EXAMPLE 3: Retirement acceleration eligibility")
    print("=" * 70)
    
    filters = MovementFilter(
        client_hub_key='CLNT00000000000000000002'
    )
    sql = calc.build_retirement_acceleration_sql(filters)
    print(sql)
    print()
    
    print("=" * 70)
    print("EXAMPLE 4: Movement type breakdown")
    print("=" * 70)
    
    filters = MovementFilter(
        participant_hub_key='PRT00000000000000000042'
    )
    sql = calc.build_movement_breakdown_sql(filters)
    print(sql)
    print()


if __name__ == "__main__":
    example_usage()
