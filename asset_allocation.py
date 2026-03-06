"""
Asset allocation strategies for retirement portfolio management.
"""

import numpy as np
from typing import Dict, Tuple

class AssetAllocation:
    """
    Manages portfolio asset allocation strategies.
    """
    
    def __init__(self, strategy_type='glide_path'):
        """
        Parameters:
        -----------
        strategy_type : str
            'glide_path' or 'optimized'
        """
        self.strategy_type = strategy_type
        
    def get_allocation(self, age: int, retirement_age: int, 
                      current_portfolio: Dict[str, float],
                      years_in_retirement: int = 0) -> Dict[str, float]:
        """
        Determine asset allocation (stocks/bonds/cash) based on strategy.
        
        Parameters:
        -----------
        age : int
            Current age
        retirement_age : int
            Planned retirement age
        current_portfolio : dict
            Current balances in each account type
        years_in_retirement : int
            Years since retirement (0 if not retired)
            
        Returns:
        --------
        dict : {'stocks': float, 'bonds': float, 'cash': float} as percentages (0-1)
        """
        if self.strategy_type == 'glide_path':
            return self._glide_path_allocation(age, retirement_age, years_in_retirement)
        elif self.strategy_type == 'optimized':
            return self._optimized_allocation(age, retirement_age, current_portfolio, years_in_retirement)
        else:
            raise ValueError(f"Unknown strategy type: {self.strategy_type}")
    
    def _glide_path_allocation(self, age: int, retirement_age: int, 
                               years_in_retirement: int) -> Dict[str, float]:
        """
        Implement a traditional glide path strategy.
        Rule of thumb: stocks = 110 - age, adjusted for retirement phase.
        """
        if age < retirement_age:
            # Pre-retirement: More aggressive
            stock_pct = min(0.90, max(0.40, (110 - age) / 100))
        else:
            # Post-retirement: Gradual shift to conservative
            # Start at 60/40, move to 30/70 over 20 years
            start_stock = 0.60
            end_stock = 0.30
            transition_years = 20
            
            if years_in_retirement < transition_years:
                stock_pct = start_stock - (start_stock - end_stock) * (years_in_retirement / transition_years)
            else:
                stock_pct = end_stock
        
        # Keep small cash allocation for immediate needs
        cash_pct = 0.05 if age >= retirement_age else 0.02
        bond_pct = 1.0 - stock_pct - cash_pct
        
        return {
            'stocks': stock_pct,
            'bonds': max(0, bond_pct),
            'cash': cash_pct
        }
    
    def _optimized_allocation(self, age: int, retirement_age: int,
                             current_portfolio: Dict[str, float],
                             years_in_retirement: int) -> Dict[str, float]:
        """
        Optimize allocation to maximize probability of success.
        Uses a dynamic approach based on portfolio size and withdrawal needs.
        """
        total_portfolio = sum(current_portfolio.values())
        
        if age < retirement_age:
            # Pre-retirement: Growth focus
            stock_pct = 0.80
            bond_pct = 0.18
            cash_pct = 0.02
        else:
            # Post-retirement: Balance growth and stability
            # Adjust based on years in retirement and portfolio health
            
            if years_in_retirement < 10:
                # Early retirement: Maintain growth
                stock_pct = 0.65
                bond_pct = 0.30
                cash_pct = 0.05
            elif years_in_retirement < 20:
                # Mid retirement: Balanced
                stock_pct = 0.50
                bond_pct = 0.45
                cash_pct = 0.05
            else:
                # Late retirement: Conservative
                stock_pct = 0.35
                bond_pct = 0.60
                cash_pct = 0.05
        
        return {
            'stocks': stock_pct,
            'bonds': bond_pct,
            'cash': cash_pct
        }
    
    def rebalance_portfolio(self, current_balances: Dict[str, float],
                           target_allocation: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate how to rebalance portfolio to target allocation.
        
        Parameters:
        -----------
        current_balances : dict
            Current dollar amounts in each asset class
        target_allocation : dict
            Target percentages for each asset class
            
        Returns:
        --------
        dict : Target dollar amounts for each asset class
        """
        total = sum(current_balances.values())
        
        return {
            'stocks': total * target_allocation['stocks'],
            'bonds': total * target_allocation['bonds'],
            'cash': total * target_allocation['cash']
        }
    
    def apply_returns(self, balances: Dict[str, float],
                     stock_return: float, bond_return: float,
                     cash_return: float = 0.02) -> Dict[str, float]:
        """
        Apply returns to portfolio balances.
        
        Parameters:
        -----------
        balances : dict
            Current balances by asset class
        stock_return : float
            Annual stock return (e.g., 0.10 for 10%)
        bond_return : float
            Annual bond return
        cash_return : float
            Annual cash return (default 2%)
            
        Returns:
        --------
        dict : New balances after applying returns
        """
        return {
            'stocks': balances.get('stocks', 0) * (1 + stock_return),
            'bonds': balances.get('bonds', 0) * (1 + bond_return),
            'cash': balances.get('cash', 0) * (1 + cash_return)
        }
