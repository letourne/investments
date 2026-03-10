"""
Retirement Planning - Data Structures
Pure data classes with no business logic.
"""

from dataclasses import dataclass
import numpy as np
from typing import Dict, List


@dataclass
class RetirementInputs:
    """
    Container for all retirement planning inputs.
    Pure data - no methods, no logic.
    """
    # Personal information (required)
    current_age: int
    retirement_age: int
    death_age: int
    is_married: bool
    
    # Current assets (required)
    pretax_401k: float
    roth_ira: float
    cash: float
    
    # Income streams (required)
    social_security_monthly: float
    social_security_start_age: int
    pension_monthly: float
    
    # Expenses (required)
    annual_spending: float
    final_estate_goal: float
    
    # Assumptions (required)
    inflation_rate: float
    market_model: str  # 'conservative', 'average', 'managed'
    allocation_strategy: str  # 'glide_path', 'optimized'
    
    # HSA (optional)
    hsa_balance: float = 0.0
    hsa_contribution: float = 0.0
    
    # Healthcare costs (optional)
    healthcare_annual_pre_medicare: float = 12000.0  # Per person or couple
    healthcare_annual_medicare: float = 9600.0       # Per person or couple
    
    # Pre-retirement income & savings (optional)
    current_salary: float = 0.0
    salary_growth_rate: float = 0.03
    annual_401k_contribution: float = 0.0
    annual_roth_contribution: float = 0.0
    annual_taxable_contribution: float = 0.0
    employer_match_percent: float = 0.0
    
    # Spouse info (optional, if married)
    spouse_age: int = 0
    spouse_retirement_age: int = 0
    spouse_death_age: int = 0
    spouse_current_salary: float = 0.0
    spouse_salary_growth_rate: float = 0.03
    spouse_annual_401k_contribution: float = 0.0
    spouse_social_security_monthly: float = 0.0
    spouse_social_security_start_age: int = 67
    spouse_pension_monthly: float = 0.0


@dataclass
class SimulationResults:
    """
    Results from a Monte Carlo simulation.
    Pure data structure for returning results.
    """
    success_rate: float
    portfolio_paths: np.ndarray  # Shape: (n_simulations, n_years)
    final_balances: np.ndarray   # Shape: (n_simulations,)
    percentiles: Dict[int, np.ndarray]  # Keys: 10, 25, 50, 75, 90
    years: List[int]  # List of ages from current_age to death_age
    
    def __post_init__(self):
        """Validate results after creation."""
        assert 0.0 <= self.success_rate <= 1.0, "Success rate must be between 0 and 1"
        assert len(self.years) == self.portfolio_paths.shape[1], "Years must match portfolio paths"


@dataclass
class OptimizationResult:
    """
    Results from an optimization run.
    """
    optimal_value: float  # The optimized variable (age, savings, spending)
    success_rate: float   # Achieved success rate
    iterations: int       # Number of simulations run
    portfolio_at_retirement: float
    median_final_balance: float
    percentile_10_final: float
    variable_name: str    # 'retirement_age', 'annual_savings', 'annual_spending'
    target_success_rate: float
    
    def __str__(self):
        """Human-readable output."""
        if self.variable_name == 'retirement_age':
            years = int(self.optimal_value)
            months = int((self.optimal_value - years) * 12)
            return f"Retire at age {years} years, {months} months with {self.success_rate:.1%} success"
        elif 'savings' in self.variable_name or 'spending' in self.variable_name:
            return f"Optimal {self.variable_name}: ${self.optimal_value:,.0f}/year with {self.success_rate:.1%} success"
        else:
            return f"Optimal {self.variable_name}: {self.optimal_value:.2f} with {self.success_rate:.1%} success"


@dataclass
class ComparisonScenario:
    """
    Single scenario in a comparison analysis.
    """
    label: str  # e.g., "Retire at 60", "Save $40K/year"
    inputs: RetirementInputs
    results: SimulationResults = None
    
    def __str__(self):
        if self.results:
            return f"{self.label}: {self.results.success_rate:.1%} success"
        else:
            return f"{self.label}: Not yet simulated"
