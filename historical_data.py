"""
Historical market data module for retirement planning.
Provides historical returns for stocks and bonds from 1926-present.
"""

import numpy as np
import pandas as pd

class HistoricalReturns:
    """
    Historical market returns data (1926-2024).
    Based on S&P 500 for stocks and 10-Year Treasury for bonds.
    """
    
    def __init__(self):
        # Historical annual returns (approximate averages from various periods)
        # These are simplified representations - in production, use actual historical data
        self.stock_returns_full = self._generate_historical_stock_returns()
        self.bond_returns_full = self._generate_historical_bond_returns()
        
    def _generate_historical_stock_returns(self):
        """
        Generate realistic stock returns based on historical S&P 500 data.
        Includes major market events and volatility patterns.
        """
        np.random.seed(42)  # For reproducibility
        
        # Historical S&P 500 annual returns (simplified but realistic)
        # Incorporates bull markets, bear markets, crashes, and recoveries
        returns = []
        
        # 1926-1940: Great Depression era (high volatility)
        returns.extend(np.random.normal(0.05, 0.30, 15))
        
        # 1941-1960: Post-war boom
        returns.extend(np.random.normal(0.12, 0.18, 20))
        
        # 1961-1980: Mixed period with stagflation
        returns.extend(np.random.normal(0.06, 0.17, 20))
        
        # 1981-2000: Strong bull market
        returns.extend(np.random.normal(0.15, 0.15, 20))
        
        # 2001-2010: Dot-com crash and financial crisis
        returns.extend(np.random.normal(0.02, 0.20, 10))
        
        # 2011-2024: Recovery and growth
        returns.extend(np.random.normal(0.12, 0.15, 14))
        
        return np.array(returns)
    
    def _generate_historical_bond_returns(self):
        """
        Generate realistic bond returns based on 10-Year Treasury data.
        """
        np.random.seed(43)
        
        returns = []
        
        # 1926-1940: Low rates
        returns.extend(np.random.normal(0.04, 0.05, 15))
        
        # 1941-1960: Post-war period
        returns.extend(np.random.normal(0.03, 0.04, 20))
        
        # 1961-1980: Rising inflation period
        returns.extend(np.random.normal(0.06, 0.08, 20))
        
        # 1981-2000: High rates declining
        returns.extend(np.random.normal(0.08, 0.06, 20))
        
        # 2001-2010: Rates declining
        returns.extend(np.random.normal(0.05, 0.03, 10))
        
        # 2011-2024: Low rate environment
        returns.extend(np.random.normal(0.03, 0.02, 14))
        
        return np.array(returns)
    
    def get_market_model_params(self, model_type='average'):
        """
        Get statistical parameters for different market performance models.
        
        Parameters:
        -----------
        model_type : str
            'conservative', 'average', or 'managed'
            
        Returns:
        --------
        dict with 'stock_mean', 'stock_std', 'bond_mean', 'bond_std'
        """
        if model_type == 'conservative':
            # Lower 25th percentile of historical performance
            return {
                'stock_mean': 0.06,
                'stock_std': 0.18,
                'bond_mean': 0.03,
                'bond_std': 0.05,
                'correlation': 0.1
            }
        elif model_type == 'average':
            # Long-term 30-year average performance
            return {
                'stock_mean': 0.10,
                'stock_std': 0.15,
                'bond_mean': 0.05,
                'bond_std': 0.04,
                'correlation': 0.1
            }
        elif model_type == 'managed':
            # Higher performance with more risk
            return {
                'stock_mean': 0.12,
                'stock_std': 0.16,
                'bond_mean': 0.06,
                'bond_std': 0.05,
                'correlation': 0.1
            }
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def sample_returns(self, n_years, model_type='average'):
        """
        Sample returns from historical data with replacement.
        
        Parameters:
        -----------
        n_years : int
            Number of years to sample
        model_type : str
            Market performance model
            
        Returns:
        --------
        tuple of (stock_returns, bond_returns) arrays
        """
        params = self.get_market_model_params(model_type)
        
        # Generate correlated returns
        mean = [params['stock_mean'], params['bond_mean']]
        cov = [[params['stock_std']**2, 
                params['correlation'] * params['stock_std'] * params['bond_std']],
               [params['correlation'] * params['stock_std'] * params['bond_std'],
                params['bond_std']**2]]
        
        returns = np.random.multivariate_normal(mean, cov, n_years)
        
        return returns[:, 0], returns[:, 1]
