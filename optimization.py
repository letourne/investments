"""
Retirement Plan Optimization Module
Goal-seeking and comparison functions.

Uses monte_carlo_engine for simulations but adds optimization logic.
"""

import numpy as np
from copy import deepcopy
from typing import List, Dict

from retirement_inputs import RetirementInputs, OptimizationResult, ComparisonScenario
from monte_carlo_engine import run_monte_carlo_simulation


def optimize_retirement_age(
    inputs: RetirementInputs,
    target_success_rate: float,
    min_age: int = None,
    max_age: int = None,
    n_simulations: int = 1000,
    tolerance: float = 0.005
) -> OptimizationResult:
    """
    Find optimal retirement age for target success rate using binary search.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Base retirement inputs (retirement_age will be optimized)
    target_success_rate : float
        Target success rate (e.g., 0.90 for 90%)
    min_age : int
        Minimum retirement age to consider (default: current_age)
    max_age : int
        Maximum retirement age to consider (default: 75)
    n_simulations : int
        Simulations per test (default: 1000 for speed)
    tolerance : float
        Success rate tolerance (default: 0.5%)
        
    Returns:
    --------
    OptimizationResult
        Optimal retirement age and associated metrics
        
    Example:
    --------
    >>> result = optimize_retirement_age(inputs, target_success_rate=0.90)
    >>> print(f"Retire at age {result.optimal_value:.1f}")
    """
    if min_age is None:
        min_age = inputs.current_age
    if max_age is None:
        max_age = 75
    
    iterations = 0
    best_age = None
    best_success = 0
    
    # Binary search for optimal age
    while max_age - min_age > 0.5:  # Within 6 months
        test_age = (min_age + max_age) / 2
        
        # Create test inputs
        test_inputs = deepcopy(inputs)
        test_inputs.retirement_age = int(np.round(test_age))
        
        # Run simulation
        results = run_monte_carlo_simulation(test_inputs, n_simulations)
        iterations += 1
        
        # Track best result
        if abs(results.success_rate - target_success_rate) < abs(best_success - target_success_rate):
            best_age = test_age
            best_success = results.success_rate
        
        # Adjust search range
        if results.success_rate < target_success_rate:
            # Need to work longer
            min_age = test_age
        else:
            # Can retire earlier
            max_age = test_age
        
        # Check if we're close enough
        if abs(results.success_rate - target_success_rate) < tolerance:
            best_age = test_age
            best_success = results.success_rate
            break
    
    # Run final simulation at optimal age
    final_inputs = deepcopy(inputs)
    final_inputs.retirement_age = int(np.round(best_age))
    final_results = run_monte_carlo_simulation(final_inputs, n_simulations=5000)
    
    # Calculate portfolio at retirement
    years_to_retirement = int(np.round(best_age)) - inputs.current_age
    portfolio_at_retirement = final_results.percentiles[50][years_to_retirement]
    
    return OptimizationResult(
        optimal_value=best_age,
        success_rate=final_results.success_rate,
        iterations=iterations,
        portfolio_at_retirement=portfolio_at_retirement,
        median_final_balance=final_results.percentiles[50][-1],
        percentile_10_final=final_results.percentiles[10][-1],
        variable_name='retirement_age',
        target_success_rate=target_success_rate
    )


def optimize_savings_amount(
    inputs: RetirementInputs,
    target_success_rate: float,
    min_savings: float = 0,
    max_savings: float = 100000,
    n_simulations: int = 1000,
    tolerance: float = 0.005
) -> OptimizationResult:
    """
    Find optimal annual savings for target success rate.
    
    Optimizes total annual contribution (401k + Roth + Taxable).
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Base inputs (annual contributions will be optimized)
    target_success_rate : float
        Target success rate
    min_savings : float
        Minimum annual savings
    max_savings : float
        Maximum annual savings
    n_simulations : int
        Simulations per test
    tolerance : float
        Success rate tolerance
        
    Returns:
    --------
    OptimizationResult
        Optimal savings amount and metrics
    """
    iterations = 0
    best_savings = None
    best_success = 0
    
    # Binary search for optimal savings
    while max_savings - min_savings > 100:  # Within $100
        test_savings = (min_savings + max_savings) / 2
        
        # Create test inputs (distribute savings across accounts)
        test_inputs = deepcopy(inputs)
        # Simple: all goes to 401k for now
        test_inputs.annual_401k_contribution = test_savings
        
        # Run simulation
        results = run_monte_carlo_simulation(test_inputs, n_simulations)
        iterations += 1
        
        # Track best
        if abs(results.success_rate - target_success_rate) < abs(best_success - target_success_rate):
            best_savings = test_savings
            best_success = results.success_rate
        
        # Adjust search
        if results.success_rate < target_success_rate:
            # Need to save more
            min_savings = test_savings
        else:
            # Can save less
            max_savings = test_savings
        
        if abs(results.success_rate - target_success_rate) < tolerance:
            best_savings = test_savings
            best_success = results.success_rate
            break
    
    # Final simulation
    final_inputs = deepcopy(inputs)
    final_inputs.annual_401k_contribution = best_savings
    final_results = run_monte_carlo_simulation(final_inputs, n_simulations=5000)
    
    years_to_retirement = inputs.retirement_age - inputs.current_age
    portfolio_at_retirement = final_results.percentiles[50][years_to_retirement]
    
    return OptimizationResult(
        optimal_value=best_savings,
        success_rate=final_results.success_rate,
        iterations=iterations,
        portfolio_at_retirement=portfolio_at_retirement,
        median_final_balance=final_results.percentiles[50][-1],
        percentile_10_final=final_results.percentiles[10][-1],
        variable_name='annual_savings',
        target_success_rate=target_success_rate
    )


def optimize_spending_amount(
    inputs: RetirementInputs,
    target_success_rate: float,
    min_spending: float = 20000,
    max_spending: float = 200000,
    n_simulations: int = 1000,
    tolerance: float = 0.005
) -> OptimizationResult:
    """
    Find optimal retirement spending for target success rate.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Base inputs (annual_spending will be optimized)
    target_success_rate : float
        Target success rate
    min_spending : float
        Minimum annual spending
    max_spending : float
        Maximum annual spending
    n_simulations : int
        Simulations per test
    tolerance : float
        Success rate tolerance
        
    Returns:
    --------
    OptimizationResult
        Optimal spending amount and metrics
    """
    iterations = 0
    best_spending = None
    best_success = 0
    
    # Binary search for optimal spending
    while max_spending - min_spending > 100:  # Within $100
        test_spending = (min_spending + max_spending) / 2
        
        # Create test inputs
        test_inputs = deepcopy(inputs)
        test_inputs.annual_spending = test_spending
        
        # Run simulation
        results = run_monte_carlo_simulation(test_inputs, n_simulations)
        iterations += 1
        
        # Track best
        if abs(results.success_rate - target_success_rate) < abs(best_success - target_success_rate):
            best_spending = test_spending
            best_success = results.success_rate
        
        # Adjust search
        if results.success_rate < target_success_rate:
            # Need to spend less
            max_spending = test_spending
        else:
            # Can spend more
            min_spending = test_spending
        
        if abs(results.success_rate - target_success_rate) < tolerance:
            best_spending = test_spending
            best_success = results.success_rate
            break
    
    # Final simulation
    final_inputs = deepcopy(inputs)
    final_inputs.annual_spending = best_spending
    final_results = run_monte_carlo_simulation(final_inputs, n_simulations=5000)
    
    years_to_retirement = inputs.retirement_age - inputs.current_age
    portfolio_at_retirement = final_results.percentiles[50][years_to_retirement]
    
    return OptimizationResult(
        optimal_value=best_spending,
        success_rate=final_results.success_rate,
        iterations=iterations,
        portfolio_at_retirement=portfolio_at_retirement,
        median_final_balance=final_results.percentiles[50][-1],
        percentile_10_final=final_results.percentiles[10][-1],
        variable_name='annual_spending',
        target_success_rate=target_success_rate
    )


def compare_retirement_ages(
    inputs: RetirementInputs,
    ages: List[int] = None,
    n_simulations: int = 1000
) -> List[ComparisonScenario]:
    """
    Compare multiple retirement ages side-by-side.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Base inputs
    ages : List[int]
        Ages to compare (default: [current, -2, +3, +5, +8])
    n_simulations : int
        Simulations per age
        
    Returns:
    --------
    List[ComparisonScenario]
        List of scenarios with results
        
    Example:
    --------
    >>> scenarios = compare_retirement_ages(inputs, ages=[60, 62, 65])
    >>> for scenario in scenarios:
    ...     print(f"{scenario.label}: {scenario.results.success_rate:.1%}")
    """
    if ages is None:
        # Default: current plan and variations
        current = inputs.retirement_age
        ages = [
            max(inputs.current_age, current - 2),
            current,
            current + 3,
            current + 5,
            current + 8
        ]
    
    scenarios = []
    
    for age in ages:
        # Create scenario
        test_inputs = deepcopy(inputs)
        test_inputs.retirement_age = age
        
        # Run simulation
        results = run_monte_carlo_simulation(test_inputs, n_simulations)
        
        # Create scenario object
        scenario = ComparisonScenario(
            label=f"Retire at {age}",
            inputs=test_inputs,
            results=results
        )
        scenarios.append(scenario)
    
    return scenarios


# Export main functions
__all__ = [
    'optimize_retirement_age',
    'optimize_savings_amount',
    'optimize_spending_amount',
    'compare_retirement_ages'
]
