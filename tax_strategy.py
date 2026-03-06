"""
Tax-efficient withdrawal strategy module.
Handles RMDs, tax optimization, and account prioritization.
"""

import numpy as np
from typing import Dict, Tuple

class TaxWithdrawalStrategy:
    """
    Manages tax-efficient withdrawals from multiple account types.
    """
    
    # IRS RMD divisors (Uniform Lifetime Table)
    RMD_TABLE = {
        73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
        80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
        87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
        94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
        101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.6, 106: 4.3, 107: 4.1,
        108: 3.9, 109: 3.7, 110: 3.5, 111: 3.4, 112: 3.3, 113: 3.1, 114: 3.0,
        115: 2.9, 116: 2.8, 117: 2.7, 118: 2.5, 119: 2.3, 120: 2.0
    }
    
    def __init__(self):
        self.rmd_start_age = 73
        
    def calculate_rmd(self, age: int, pretax_balance: float) -> float:
        """
        Calculate Required Minimum Distribution for a given age and balance.
        
        Parameters:
        -----------
        age : int
            Current age
        pretax_balance : float
            Current pre-tax account balance
            
        Returns:
        --------
        float : Required minimum distribution amount
        """
        if age < self.rmd_start_age or pretax_balance <= 0:
            return 0.0
        
        divisor = self.RMD_TABLE.get(age, 2.0)  # Default to 2.0 for ages beyond table
        return pretax_balance / divisor
    
    def optimize_withdrawal(self, 
                          needed_amount: float,
                          pretax_balance: float,
                          roth_balance: float,
                          cash_balance: float,
                          age: int,
                          is_married: bool = False) -> Dict[str, float]:
        """
        Determine optimal tax-efficient withdrawal strategy.
        
        Strategy:
        1. First, take RMD if required (from pre-tax)
        2. Then withdraw from cash (no tax impact)
        3. Then from Roth (no tax impact, preserve pre-tax for growth)
        4. Finally from pre-tax (taxable)
        
        Parameters:
        -----------
        needed_amount : float
            Total amount needed for the year
        pretax_balance : float
            Current 401k/traditional IRA balance
        roth_balance : float
            Current Roth IRA balance
        cash_balance : float
            Current cash/taxable account balance
        age : int
            Current age
        is_married : bool
            Marital status (affects tax calculations)
            
        Returns:
        --------
        dict : Withdrawal amounts from each account
        """
        withdrawals = {
            'pretax': 0.0,
            'roth': 0.0,
            'cash': 0.0,
            'total': 0.0,
            'rmd_required': 0.0,
            'shortage': 0.0
        }
        
        # Calculate RMD
        rmd = self.calculate_rmd(age, pretax_balance)
        withdrawals['rmd_required'] = rmd
        
        remaining_needed = needed_amount
        
        # Step 1: Take RMD if required
        if rmd > 0:
            pretax_withdrawal = min(rmd, pretax_balance)
            withdrawals['pretax'] += pretax_withdrawal
            remaining_needed -= pretax_withdrawal
            pretax_balance -= pretax_withdrawal
        
        if remaining_needed <= 0:
            withdrawals['total'] = needed_amount
            return withdrawals
        
        # Step 2: Withdraw from cash
        cash_withdrawal = min(remaining_needed, cash_balance)
        withdrawals['cash'] = cash_withdrawal
        remaining_needed -= cash_withdrawal
        cash_balance -= cash_withdrawal
        
        if remaining_needed <= 0:
            withdrawals['total'] = needed_amount
            return withdrawals
        
        # Step 3: Withdraw from Roth
        roth_withdrawal = min(remaining_needed, roth_balance)
        withdrawals['roth'] = roth_withdrawal
        remaining_needed -= roth_withdrawal
        roth_balance -= roth_withdrawal
        
        if remaining_needed <= 0:
            withdrawals['total'] = needed_amount
            return withdrawals
        
        # Step 4: Withdraw remaining from pre-tax
        pretax_withdrawal = min(remaining_needed, pretax_balance)
        withdrawals['pretax'] += pretax_withdrawal
        remaining_needed -= pretax_withdrawal
        
        # If we still can't meet the need, record the shortage
        if remaining_needed > 0:
            withdrawals['shortage'] = remaining_needed
        
        withdrawals['total'] = needed_amount - remaining_needed
        
        return withdrawals
    
    def estimate_tax_burden(self, pretax_withdrawal: float, is_married: bool = False) -> float:
        """
        Estimate federal tax on pre-tax withdrawals.
        Uses simplified 2024 tax brackets.
        
        Parameters:
        -----------
        pretax_withdrawal : float
            Amount withdrawn from pre-tax accounts
        is_married : bool
            Filing status
            
        Returns:
        --------
        float : Estimated tax amount
        """
        if is_married:
            # Married filing jointly brackets (2024, simplified)
            brackets = [
                (22000, 0.10),
                (89075, 0.12),
                (190750, 0.22),
                (364200, 0.24),
                (462500, 0.32),
                (693750, 0.35),
                (float('inf'), 0.37)
            ]
            standard_deduction = 29200
        else:
            # Single filer brackets (2024, simplified)
            brackets = [
                (11000, 0.10),
                (44725, 0.12),
                (95375, 0.22),
                (182100, 0.24),
                (231250, 0.32),
                (578125, 0.35),
                (float('inf'), 0.37)
            ]
            standard_deduction = 14600
        
        taxable_income = max(0, pretax_withdrawal - standard_deduction)
        
        tax = 0
        previous_bracket = 0
        
        for bracket_limit, rate in brackets:
            if taxable_income <= bracket_limit:
                tax += (taxable_income - previous_bracket) * rate
                break
            else:
                tax += (bracket_limit - previous_bracket) * rate
                previous_bracket = bracket_limit
        
        return tax
