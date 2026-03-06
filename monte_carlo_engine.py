"""
Monte Carlo Simulation Engine - Standalone Module
Pure simulation logic with no external dependencies beyond data structures.

This module can be imported and used by ANY other module.
All simulation logic is contained here.
"""

import numpy as np
from typing import Tuple

from retirement_inputs import RetirementInputs, SimulationResults
from historical_data import HistoricalReturns
from tax_strategy import TaxWithdrawalStrategy
from asset_allocation import AssetAllocation


def run_monte_carlo_simulation(
    inputs: RetirementInputs,
    n_simulations: int = 5000,
    random_seed: int = None
) -> SimulationResults:
    """
    Main entry point for Monte Carlo simulation.
    
    This is THE function to call for running simulations.
    Completely standalone - no UI dependencies.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        All retirement planning parameters
    n_simulations : int
        Number of Monte Carlo runs (default: 5000)
    random_seed : int
        Random seed for reproducibility (optional)
        
    Returns:
    --------
    SimulationResults
        Complete simulation results with all metrics
        
    Example:
    --------
    >>> from retirement_inputs import RetirementInputs
    >>> inputs = RetirementInputs(...)
    >>> results = run_monte_carlo_simulation(inputs, n_simulations=1000)
    >>> print(f"Success rate: {results.success_rate:.1%}")
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Initialize components
    historical_data = HistoricalReturns()
    tax_strategy = TaxWithdrawalStrategy()
    allocation = AssetAllocation(strategy_type=inputs.allocation_strategy)
    
    # Calculate simulation parameters
    n_years = inputs.death_age - inputs.current_age + 1
    
    # Arrays to store results
    portfolio_paths = np.zeros((n_simulations, n_years))
    final_balances = np.zeros(n_simulations)
    success_count = 0
    
    # Run all simulations
    for sim in range(n_simulations):
        path = _run_single_simulation_path(
            inputs, 
            n_years, 
            historical_data, 
            tax_strategy, 
            allocation
        )
        portfolio_paths[sim, :] = path
        final_balances[sim] = path[-1]
        
        # Count as success if final balance >= goal
        if path[-1] >= inputs.final_estate_goal:
            success_count += 1
    
    # Calculate metrics
    success_rate = success_count / n_simulations
    
    # Calculate percentiles
    percentiles = {
        10: np.percentile(portfolio_paths, 10, axis=0),
        25: np.percentile(portfolio_paths, 25, axis=0),
        50: np.percentile(portfolio_paths, 50, axis=0),
        75: np.percentile(portfolio_paths, 75, axis=0),
        90: np.percentile(portfolio_paths, 90, axis=0),
    }
    
    # Create years list
    years = list(range(inputs.current_age, inputs.death_age + 1))
    
    return SimulationResults(
        success_rate=success_rate,
        portfolio_paths=portfolio_paths,
        final_balances=final_balances,
        percentiles=percentiles,
        years=years
    )


def run_single_simulation_path(
    inputs: RetirementInputs,
    seed: int = None
) -> np.ndarray:
    """
    Run a single Monte Carlo simulation path.
    
    Useful for debugging, testing, or custom analysis.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Retirement planning parameters
    seed : int
        Random seed for this path
        
    Returns:
    --------
    np.ndarray
        Portfolio values over time (length = n_years)
    """
    if seed is not None:
        np.random.seed(seed)
    
    n_years = inputs.death_age - inputs.current_age + 1
    
    historical_data = HistoricalReturns()
    tax_strategy = TaxWithdrawalStrategy()
    allocation = AssetAllocation(strategy_type=inputs.allocation_strategy)
    
    return _run_single_simulation_path(
        inputs, n_years, historical_data, tax_strategy, allocation
    )


def _run_single_simulation_path(
    inputs: RetirementInputs,
    n_years: int,
    historical_data: HistoricalReturns,
    tax_strategy: TaxWithdrawalStrategy,
    allocation: AssetAllocation
) -> np.ndarray:
    """
    Internal function to run a single simulation path.
    
    Contains the core simulation logic.
    """
    # Initialize portfolio by account type
    pretax_balance = inputs.pretax_401k
    roth_balance = inputs.roth_ira
    cash_balance = inputs.cash
    hsa_balance = inputs.hsa_balance
    
    # Track total portfolio over time
    portfolio_values = np.zeros(n_years)
    
    # Healthcare inflation rate (typically higher than general inflation)
    healthcare_inflation = 0.04  # 4% annual increase for healthcare costs
    
    # Generate market returns for all years
    stock_returns, bond_returns = historical_data.sample_returns(
        n_years, inputs.market_model
    )
    
    for year_idx in range(n_years):
        current_age = inputs.current_age + year_idx
        spouse_age = inputs.spouse_age + year_idx if inputs.is_married else 0
        years_retired = max(0, current_age - inputs.retirement_age)
        
        # Calculate total portfolio (excluding HSA - it's separate for healthcare)
        total_portfolio = pretax_balance + roth_balance + cash_balance
        portfolio_values[year_idx] = total_portfolio + hsa_balance  # Include HSA in total net worth display
        
        # If portfolio depleted, it stays at 0
        if total_portfolio <= 0:
            continue
        
        # Determine asset allocation
        alloc = allocation.get_allocation(
            current_age, 
            inputs.retirement_age,
            {'pretax': pretax_balance, 'roth': roth_balance, 'cash': cash_balance},
            years_retired
        )
        
        # Allocate total portfolio to asset classes
        stock_balance = total_portfolio * alloc['stocks']
        bond_balance = total_portfolio * alloc['bonds']
        cash_asset_balance = total_portfolio * alloc['cash']
        
        # Apply market returns
        stock_balance *= (1 + stock_returns[year_idx])
        bond_balance *= (1 + bond_returns[year_idx])
        cash_asset_balance *= (1 + 0.02)  # Cash earns ~2%
        
        # New total after growth
        total_after_growth = stock_balance + bond_balance + cash_asset_balance
        
        # HSA grows with same allocation as portfolio
        if hsa_balance > 0:
            hsa_stock = hsa_balance * alloc['stocks']
            hsa_bonds = hsa_balance * alloc['bonds']
            hsa_cash = hsa_balance * alloc['cash']
            
            hsa_stock *= (1 + stock_returns[year_idx])
            hsa_bonds *= (1 + bond_returns[year_idx])
            hsa_cash *= (1 + 0.02)
            
            hsa_balance = hsa_stock + hsa_bonds + hsa_cash
        
        # Before retirement: Add salary and contributions
        if current_age < inputs.retirement_age:
            # Calculate current year's salary with growth
            years_working = current_age - inputs.current_age
            current_year_salary = inputs.current_salary * ((1 + inputs.salary_growth_rate) ** years_working)
            
            # Primary earner contributions
            if inputs.current_salary > 0:
                # Employer match on 401k
                employer_match = inputs.annual_401k_contribution * inputs.employer_match_percent
                pretax_balance += inputs.annual_401k_contribution + employer_match
                roth_balance += inputs.annual_roth_contribution
                cash_balance += inputs.annual_taxable_contribution
                
                # HSA contributions (can only contribute while working with HDHP)
                hsa_balance += inputs.hsa_contribution
            
            # Spouse contributions (if married and spouse hasn't retired)
            if inputs.is_married and spouse_age < inputs.spouse_retirement_age:
                if inputs.spouse_current_salary > 0:
                    pretax_balance += inputs.spouse_annual_401k_contribution
            
            # Distribute growth back to accounts proportionally
            if total_after_growth > 0 and total_portfolio > 0:
                growth_ratio = total_after_growth / total_portfolio
                pretax_balance = pretax_balance * growth_ratio
                roth_balance = roth_balance * growth_ratio
                cash_balance = cash_balance * growth_ratio
        
        # If in retirement, handle withdrawals and income
        if current_age >= inputs.retirement_age:
            # Calculate income
            income = 0
            if current_age >= inputs.social_security_start_age:
                income += inputs.social_security_monthly * 12
            income += inputs.pension_monthly * 12
            
            # Spouse income (if applicable and spouse is retired)
            if inputs.is_married and spouse_age >= inputs.spouse_retirement_age:
                if spouse_age >= inputs.spouse_social_security_start_age:
                    income += inputs.spouse_social_security_monthly * 12
                income += inputs.spouse_pension_monthly * 12
            
            # Adjust spending for inflation
            years_since_retirement = current_age - inputs.retirement_age
            inflation_factor = (1 + inputs.inflation_rate) ** years_since_retirement
            adjusted_spending = inputs.annual_spending * inflation_factor
            
            # Calculate healthcare costs (separate from general spending)
            healthcare_inflation_factor = (1 + healthcare_inflation) ** years_since_retirement
            if current_age < 65:  # Pre-Medicare
                healthcare_cost = inputs.healthcare_annual_pre_medicare * healthcare_inflation_factor
            else:  # Medicare (65+)
                healthcare_cost = inputs.healthcare_annual_medicare * healthcare_inflation_factor
            
            # Use HSA for healthcare costs FIRST (tax-free!)
            healthcare_from_hsa = min(healthcare_cost, hsa_balance)
            hsa_balance -= healthcare_from_hsa
            hsa_balance = max(0, hsa_balance)  # Can't go negative
            
            # Remaining healthcare costs come from regular portfolio
            healthcare_from_portfolio = healthcare_cost - healthcare_from_hsa
            
            # Total withdrawal needed = spending + remaining healthcare - income
            total_needed = adjusted_spending + healthcare_from_portfolio
            net_needed = max(0, total_needed - income)
            
            # Distribute portfolio back to account types proportionally
            if total_after_growth > 0:
                pretax_balance = total_after_growth * (pretax_balance / total_portfolio)
                roth_balance = total_after_growth * (roth_balance / total_portfolio)
                cash_balance = total_after_growth * (cash_balance / total_portfolio)
            
            # Optimize withdrawal
            withdrawal = tax_strategy.optimize_withdrawal(
                net_needed,
                pretax_balance,
                roth_balance,
                cash_balance,
                current_age,
                inputs.is_married
            )
            
            # Apply withdrawals
            pretax_balance -= withdrawal['pretax']
            roth_balance -= withdrawal['roth']
            cash_balance -= withdrawal['cash']
            
            # If there's a shortage, set balances to zero
            if withdrawal['shortage'] > 0:
                pretax_balance = max(0, pretax_balance)
                roth_balance = max(0, roth_balance)
                cash_balance = max(0, cash_balance)
    
    return portfolio_values


def calculate_success_rate_at_age(
    inputs: RetirementInputs,
    retirement_age: int,
    n_simulations: int = 1000
) -> float:
    """
    Calculate success rate for a specific retirement age.
    
    Helper function for optimization routines.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Base inputs (retirement_age will be overridden)
    retirement_age : int
        Age to test
    n_simulations : int
        Number of simulations (default: 1000 for speed)
        
    Returns:
    --------
    float
        Success rate (0.0 to 1.0)
    """
    # Create modified inputs
    from copy import deepcopy
    test_inputs = deepcopy(inputs)
    test_inputs.retirement_age = retirement_age
    
    # Run simulation
    results = run_monte_carlo_simulation(test_inputs, n_simulations)
    
    return results.success_rate


# Export main functions
__all__ = [
    'run_monte_carlo_simulation',
    'run_single_simulation_path',
    'calculate_success_rate_at_age'
]
