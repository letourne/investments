"""
Utility functions for saving/loading scenarios and data formatting.
"""

import json
import pandas as pd
from typing import Dict
from retirement_inputs import RetirementInputs


def save_scenario(inputs: RetirementInputs, filename: str):
    """
    Save retirement scenario to JSON file.
    
    Parameters:
    -----------
    inputs : RetirementInputs
        Retirement planning inputs
    filename : str
        Path to save file
    """
    scenario_dict = {
        'current_age': inputs.current_age,
        'retirement_age': inputs.retirement_age,
        'death_age': inputs.death_age,
        'is_married': inputs.is_married,
        'pretax_401k': inputs.pretax_401k,
        'roth_ira': inputs.roth_ira,
        'cash': inputs.cash,
        'social_security_monthly': inputs.social_security_monthly,
        'social_security_start_age': inputs.social_security_start_age,
        'pension_monthly': inputs.pension_monthly,
        'annual_spending': inputs.annual_spending,
        'final_estate_goal': inputs.final_estate_goal,
        'inflation_rate': inputs.inflation_rate,
        'market_model': inputs.market_model,
        'allocation_strategy': inputs.allocation_strategy
    }
    
    with open(filename, 'w') as f:
        json.dump(scenario_dict, f, indent=2)


def load_scenario(filename: str) -> RetirementInputs:
    """
    Load retirement scenario from JSON file.
    
    Parameters:
    -----------
    filename : str
        Path to load file
        
    Returns:
    --------
    RetirementInputs
    """
    with open(filename, 'r') as f:
        scenario_dict = json.load(f)
    
    return RetirementInputs(**scenario_dict)


def format_currency(amount: float) -> str:
    """Format number as currency."""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:.0f}"


def format_percentage(value: float) -> str:
    """Format decimal as percentage."""
    return f"{value*100:.1f}%"


def create_summary_dataframe(results) -> pd.DataFrame:
    """
    Create a summary DataFrame from simulation results.
    
    Parameters:
    -----------
    results : SimulationResults
        Results from run_monte_carlo_simulation()
        
    Returns:
    --------
    pd.DataFrame
    """
    years = results.years
    percentiles = results.percentiles
    
    df = pd.DataFrame({
        'Age': years,
        '10th Percentile': percentiles[10],
        '25th Percentile': percentiles[25],
        'Median (50th)': percentiles[50],
        '75th Percentile': percentiles[75],
        '90th Percentile': percentiles[90]
    })
    
    return df


def calculate_retirement_readiness(current_savings: float, 
                                   annual_spending: float,
                                   years_to_retirement: int,
                                   expected_return: float = 0.07) -> Dict:
    """
    Calculate retirement readiness metrics.
    
    Parameters:
    -----------
    current_savings : float
        Total current savings
    annual_spending : float
        Expected annual spending in retirement
    years_to_retirement : int
        Years until retirement
    expected_return : float
        Expected annual return
        
    Returns:
    --------
    dict with readiness metrics
    """
    # Rule of thumb: Need 25x annual spending (4% withdrawal rule)
    target_savings = annual_spending * 25
    
    # Project savings at retirement
    projected_savings = current_savings * (1 + expected_return) ** years_to_retirement
    
    # Calculate gap
    savings_gap = target_savings - projected_savings
    
    return {
        'current_savings': current_savings,
        'target_savings': target_savings,
        'projected_savings': projected_savings,
        'savings_gap': savings_gap,
        'on_track': savings_gap <= 0,
        'percent_of_goal': (projected_savings / target_savings) * 100 if target_savings > 0 else 0
    }
