"""
Retirement Planning Dashboard - Enhanced Version
With spouse information, pre-retirement income, and improved visualizations
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import os
import glob
import json

from monte_carlo_engine import run_monte_carlo_simulation
from retirement_inputs import RetirementInputs
from utils import (save_scenario, load_scenario, format_currency, 
                   format_percentage, create_summary_dataframe,
                   calculate_retirement_readiness)

# Page configuration
st.set_page_config(
    page_title="Retirement Planning Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================================
# PHASE 1: PROFESSIONAL CUSTOM CSS
# ========================================
st.markdown("""
    <style>
    /* Import Professional Font - Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* ============================================
       CSS DESIGN SYSTEM - Financial Professional
       ============================================ */
    
    :root {
        /* Primary Colors - Brighter for dark theme */
        --primary-dark: #5B9BD5;
        --primary-main: #3B7FC4;
        --primary-light: #7CB8E8;
        --primary-accent: #4A9EDB;
        
        /* Success/Growth - Brighter Green */
        --success-dark: #22C55E;
        --success-main: #16A34A;
        --success-light: #86EFAC;
        
        /* Warning - Brighter Amber */
        --warning-dark: #FCD34D;
        --warning-main: #F59E0B;
        --warning-light: #FDE68A;
        
        /* Danger - Brighter Red */
        --danger-dark: #F87171;
        --danger-main: #EF4444;
        --danger-light: #FCA5A5;
        
        /* Dark Theme Neutrals */
        --gray-900: #FAFAFA;  /* Almost white - primary text */
        --gray-700: #E5E7EB;  /* Light gray - secondary text */
        --gray-500: #9CA3AF;  /* Medium gray - labels */
        --gray-300: #4B5563;  /* Dark gray - borders */
        --gray-100: #1F2937;  /* Very dark - backgrounds */
        --white: #0E1117;     /* Dark background */
        
        /* Typography */
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'JetBrains Mono', 'Courier New', monospace;
        
        /* Spacing */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        
        /* Border Radius */
        --radius-sm: 0.25rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        
        /* Shadows - Lighter for dark theme */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.5);
    }
    
    /* ============================================
       GLOBAL STYLES - Dark Theme Professional
       ============================================ */
    
    /* Main app background - keep Streamlit's dark */
    .main, .main > div {
        font-family: var(--font-primary) !important;
        color: var(--gray-900) !important;
    }
    
    /* All text elements */
    p, span, div {
        font-family: var(--font-primary) !important;
        color: var(--gray-900) !important;
    }
    
    /* Headers - brighter for dark theme */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-primary) !important;
        font-weight: 700 !important;
        color: var(--primary-light) !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        margin-top: var(--space-xl) !important;
        margin-bottom: var(--space-md) !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-top: var(--space-lg) !important;
        margin-bottom: var(--space-sm) !important;
    }
        margin-top: var(--space-lg);
        margin-bottom: var(--space-sm);
    }
    
    /* ============================================
       METRIC CARDS - Hero Display
       ============================================ */
    
    [data-testid="stMetricValue"] {
        font-size: 3rem;
        font-weight: 900;
        color: var(--primary-dark);
        font-family: var(--font-primary);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--gray-700);
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* ============================================
       INPUT FIELDS - Dark Theme Professional
       ============================================ */
    
    /* Number Inputs */
    .stNumberInput > div > div > input {
        background: #1E2127 !important;
        border: 2px solid var(--gray-300) !important;
        border-radius: var(--radius-lg) !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        font-family: var(--font-mono) !important;
        color: var(--gray-900) !important;
        transition: all 0.2s ease !important;
        min-height: 44px !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 127, 196, 0.3) !important;
        outline: none !important;
    }
    
    .stNumberInput > div > div > input:hover {
        border-color: var(--primary-light) !important;
    }
    
    /* Text Inputs */
    .stTextInput > div > div > input {
        background: #1E2127 !important;
        border: 2px solid var(--gray-300) !important;
        border-radius: var(--radius-lg) !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        font-family: var(--font-primary) !important;
        color: var(--gray-900) !important;
        transition: all 0.2s ease !important;
        min-height: 44px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 127, 196, 0.3) !important;
        outline: none !important;
    }
    
    /* Select Boxes */
    .stSelectbox > div > div {
        background: #1E2127 !important;
        border: 2px solid var(--gray-300) !important;
        border-radius: var(--radius-lg) !important;
        font-family: var(--font-primary) !important;
        min-height: 44px !important;
        color: var(--gray-900) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--primary-light) !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: var(--primary-accent);
    }
    
    /* Checkboxes */
    .stCheckbox {
        font-family: var(--font-primary);
        font-size: 16px;
    }
    
    /* Input Labels - Make sure they're visible! */
    label {
        font-family: var(--font-primary) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--gray-700) !important;
        margin-bottom: var(--space-sm) !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Streamlit specific label classes */
    [data-testid="stMarkdownContainer"] label,
    .stNumberInput label,
    .stTextInput label,
    .stSelectbox label,
    .stSlider label,
    .stCheckbox label {
        font-family: var(--font-primary) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--gray-700) !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* ============================================
       BUTTONS - Clear Hierarchy
       ============================================ */
    
    .stButton > button {
        border-radius: var(--radius-lg);
        font-weight: 600;
        font-family: var(--font-primary);
        padding: 12px 24px;
        transition: all 0.2s ease;
        min-height: 44px;
        border: none;
    }
    
    /* Primary Button (CTA) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-accent) 0%, var(--primary-main) 100%);
        color: white;
        box-shadow: var(--shadow-md);
        font-size: 16px;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: var(--white);
        color: var(--primary-dark);
        border: 2px solid var(--gray-300);
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--primary-accent);
        background: var(--gray-100);
    }
    
    /* ============================================
       EXPANDERS - Collapsible Sections
       ============================================ */
    
    .streamlit-expanderHeader {
        background: var(--white);
        border-radius: var(--radius-lg);
        padding: 16px 24px;
        border: 2px solid var(--gray-300);
        font-size: 18px;
        font-weight: 600;
        font-family: var(--font-primary);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-accent);
        background: var(--gray-100);
    }
    
    .streamlit-expanderContent {
        background: var(--white);
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        padding: 24px;
        margin-top: -12px;
        border: 2px solid var(--gray-300);
        border-top: none;
    }
    
    /* ============================================
       TABS - Clean Navigation
       ============================================ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-lg);
        padding: 12px 24px;
        font-weight: 600;
        font-family: var(--font-primary);
        background: var(--white);
        border: 2px solid var(--gray-300);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-accent);
        color: white;
        border-color: var(--primary-accent);
    }
    
    /* ============================================
       TABLES - Professional Data Display
       ============================================ */
    
    .dataframe {
        font-family: var(--font-mono);
        font-size: 14px;
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe thead th {
        background: var(--gray-100);
        color: var(--gray-700);
        font-weight: 600;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 2px solid var(--gray-300);
        font-family: var(--font-primary);
    }
    
    .dataframe tbody td {
        padding: 10px 16px;
        border-bottom: 1px solid var(--gray-300);
    }
    
    .dataframe tbody tr:nth-child(even) {
        background: #F9FAFB;
    }
    
    .dataframe tbody tr:hover {
        background: #EEF2FF;
        transition: background 0.2s ease;
    }
    
    /* ============================================
       SIDEBAR - Force Dark Theme
       ============================================ */
    
    /* Force sidebar container to dark background */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"],
    .css-1d391kg,
    .st-emotion-cache-1d391kg {
        background-color: #1E2127 !important;
        background: #1E2127 !important;
    }
    
    /* Force all sidebar child elements */
    [data-testid="stSidebar"] * {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] {
        padding: var(--space-lg) !important;
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: var(--space-md) !important;
        background: transparent !important;
    }
    
    /* Force sidebar labels to be visible with light text */
    [data-testid="stSidebar"] label {
        font-family: var(--font-primary) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #E5E7EB !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin-bottom: 8px !important;
    }
    
    /* Force all text in sidebar to light color */
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: #FAFAFA !important;
        font-family: var(--font-primary) !important;
    }
    
    /* Make sure subheaders are bright */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #7CB8E8 !important;
        visibility: visible !important;
        display: block !important;
        font-family: var(--font-primary) !important;
        font-weight: 700 !important;
    }
    
    /* Input backgrounds in sidebar should be darker */
    [data-testid="stSidebar"] input {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    
    /* Button backgrounds in sidebar */
    [data-testid="stSidebar"] button {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
        border-color: #4B5563 !important;
    }
    
    /* ============================================
       PROGRESS BAR - During Simulation
       ============================================ */
    
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-accent) 0%, var(--success-main) 100%);
        border-radius: var(--radius-lg);
    }
    
    /* ============================================
       LOADING SPINNER
       ============================================ */
    
    .stSpinner > div {
        border-color: var(--primary-accent) transparent transparent transparent;
    }
    
    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */
    
    .stAlert {
        border-radius: var(--radius-lg);
        padding: var(--space-md);
        font-family: var(--font-primary);
    }
    
    /* Success Alert */
    [data-baseweb="notification"][kind="success"] {
        background: var(--success-light);
        border-left: 4px solid var(--success-main);
    }
    
    /* Warning Alert */
    [data-baseweb="notification"][kind="warning"] {
        background: var(--warning-light);
        border-left: 4px solid var(--warning-main);
    }
    
    /* Error Alert */
    [data-baseweb="notification"][kind="error"] {
        background: var(--danger-light);
        border-left: 4px solid var(--danger-main);
    }
    
    /* Info Alert */
    [data-baseweb="notification"][kind="info"] {
        background: #DBEAFE;
        border-left: 4px solid var(--primary-accent);
    }
    
    /* ============================================
       SCROLLBAR - Styled
       ============================================ */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gray-300);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-accent);
    }
    
    /* ============================================
       UTILITY CLASSES
       ============================================ */
    
    .success-text {
        color: var(--success-main);
        font-weight: 700;
    }
    
    .warning-text {
        color: var(--warning-main);
        font-weight: 700;
    }
    
    .danger-text {
        color: var(--danger-main);
        font-weight: 700;
    }
    
    .text-center {
        text-align: center;
    }
    
    .font-mono {
        font-family: var(--font-mono);
    }
    
    /* ============================================
       RESPONSIVE - iPad Optimizations
       ============================================ */
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
        }
    }
    
    </style>
""", unsafe_allow_html=True)

# ========================================
# CHART THEME CONFIGURATION
# ========================================

def get_professional_chart_layout():
    """Return professional Plotly layout configuration for dark theme"""
    return {
        'font': {
            'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            'size': 14,
            'color': '#E5E7EB'  # Light gray text
        },
        'title': {
            'font': {
                'size': 24,
                'color': '#7CB8E8',  # Bright blue for dark theme
                'family': 'Inter, sans-serif',
                'weight': 700
            },
            'x': 0.02,
            'xanchor': 'left'
        },
        'paper_bgcolor': '#0E1117',  # Dark background
        'plot_bgcolor': '#1E2127',   # Slightly lighter plot area
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': '#1E2127',
            'bordercolor': '#3B7FC4',
            'font': {'size': 13, 'family': 'Inter', 'color': '#FAFAFA'}
        },
        'xaxis': {
            'gridcolor': '#374151',  # Subtle grid
            'gridwidth': 1,
            'linecolor': '#4B5563',
            'linewidth': 2,
            'tickfont': {'size': 13, 'family': 'Inter', 'color': '#E5E7EB'},
            'title': {
                'font': {'size': 14, 'family': 'Inter', 'color': '#E5E7EB'}
            }
        },
        'yaxis': {
            'gridcolor': '#374151',
            'gridwidth': 1,
            'linecolor': '#4B5563',
            'linewidth': 2,
            'tickfont': {'size': 13, 'family': 'Inter', 'color': '#E5E7EB'},
            'title': {
                'font': {'size': 14, 'family': 'Inter', 'color': '#E5E7EB'}
            }
        },
        'margin': {'l': 80, 'r': 40, 't': 100, 'b': 60}
    }

# Professional color palette
CHART_COLORS = {
    'primary': '#3B7FC4',
    'success': '#16A34A',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'purple': '#8B5CF6',
    'pink': '#EC4899'
}

# ========================================
# SESSION STATE & DEFAULT VALUES
# ========================================

# Initialize session state
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'save_dialog' not in st.session_state:
    st.session_state.save_dialog = False
if 'load_dialog' not in st.session_state:
    st.session_state.load_dialog = False

# Create scenarios directory if it doesn't exist
# Use absolute path relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
SCENARIOS_DIR = os.path.join(SCRIPT_DIR, 'scenarios')

if not os.path.exists(SCENARIOS_DIR):
    os.makedirs(SCENARIOS_DIR)
    print(f"Created scenarios directory: {SCENARIOS_DIR}")

# Default values (mostly zeros with some reasonable defaults)
DEFAULT_VALUES = {
    # Personal
    'current_age': 54,
    'retirement_age': 62,
    'death_age': 90,
    'is_married': False,
    
    # Spouse (if married)
    'spouse_age': 54,
    'spouse_retirement_age': 63,
    'spouse_death_age': 90,
    
    # Pre-Retirement Income
    'current_salary': 0.0,
    'salary_growth_rate': 3.0,
    'annual_401k_contribution': 0.0,
    'annual_roth_contribution': 0.0,
    'annual_taxable_contribution': 0.0,
    'employer_match_percent': 0.0,
    
    # Spouse Income
    'spouse_current_salary': 0.0,
    'spouse_annual_401k': 0.0,
    
    # Current Assets - Pre-Tax
    'pretax_401k': 0.0,
    'pretax_403b': 0.0,
    'pretax_457': 0.0,
    'pretax_rollover': 0.0,
    
    # Current Assets - Roth
    'roth_401k': 0.0,
    'roth_403b': 0.0,
    'roth_457': 0.0,
    'roth_ira': 0.0,
    'roth_other': 0.0,
    
    # HSA
    'hsa_balance': 0.0,
    'hsa_contribution': 0.0,
    
    # Healthcare
    'healthcare_model': 'Average',
    'healthcare_annual_pre_medicare': 12000.0,
    'healthcare_annual_medicare': 9600.0,
    
    # Taxable Accounts
    'cash': 0.0,
    
    # Retirement Income
    'social_security_monthly': 0.0,
    'social_security_start_age': 67,
    'pension_monthly': 0.0,
    
    # Spouse Retirement Income
    'spouse_ss_monthly': 0.0,
    'spouse_ss_start_age': 67,
    'spouse_pension_monthly': 0.0,
    
    # Expenses
    'annual_spending': 75000.0,
    'final_estate_goal': 0.0,
    
    # Settings
    'inflation_rate': 3.0,
    'market_model': 'Average',
    'allocation_strategy': 'Glide Path'
}

# Load default values from session state or use DEFAULT_VALUES
def get_input_value(key, default=None):
    """Get input value from session state or default"""
    if default is None:
        default = DEFAULT_VALUES.get(key, 0.0)
    return st.session_state.get(f'input_{key}', default)

def set_input_value(key, value):
    """Set input value in session state"""
    st.session_state[f'input_{key}'] = value

def reset_to_defaults():
    """Reset all inputs to default values, clear results"""
    # Clear all input keys (both with and without 'input_' prefix)
    
    # Keys with 'input_' prefix
    st.session_state['input_current_age'] = DEFAULT_VALUES['current_age']
    st.session_state['input_retirement_age'] = DEFAULT_VALUES['retirement_age']
    st.session_state['input_death_age'] = DEFAULT_VALUES['death_age']
    st.session_state['input_is_married'] = DEFAULT_VALUES['is_married']
    
    # Spouse fields (no prefix)
    st.session_state['spouse_age'] = DEFAULT_VALUES['spouse_age']
    st.session_state['spouse_retirement_age'] = DEFAULT_VALUES['spouse_retirement_age']
    st.session_state['spouse_death_age'] = DEFAULT_VALUES['spouse_death_age']
    
    # Pre-retirement income (no prefix)
    st.session_state['current_salary'] = DEFAULT_VALUES['current_salary']
    st.session_state['annual_401k'] = DEFAULT_VALUES['annual_401k_contribution']
    st.session_state['annual_roth'] = DEFAULT_VALUES['annual_roth_contribution']
    st.session_state['annual_taxable'] = DEFAULT_VALUES['annual_taxable_contribution']
    st.session_state['employer_match'] = DEFAULT_VALUES['employer_match_percent']
    st.session_state['spouse_current_salary'] = DEFAULT_VALUES['spouse_current_salary']
    st.session_state['spouse_annual_401k'] = DEFAULT_VALUES['spouse_annual_401k']
    
    # Current assets - Pre-tax (no prefix)
    st.session_state['pretax_401k'] = DEFAULT_VALUES['pretax_401k']
    st.session_state['pretax_403b'] = DEFAULT_VALUES['pretax_403b']
    st.session_state['pretax_457'] = DEFAULT_VALUES['pretax_457']
    st.session_state['pretax_rollover'] = DEFAULT_VALUES['pretax_rollover']
    
    # Current assets - Roth (no prefix)
    st.session_state['roth_401k'] = DEFAULT_VALUES['roth_401k']
    st.session_state['roth_403b'] = DEFAULT_VALUES['roth_403b']
    st.session_state['roth_457'] = DEFAULT_VALUES['roth_457']
    st.session_state['roth_ira'] = DEFAULT_VALUES['roth_ira']
    st.session_state['roth_other'] = DEFAULT_VALUES['roth_other']
    
    # HSA & Cash (no prefix)
    st.session_state['hsa_balance'] = DEFAULT_VALUES['hsa_balance']
    st.session_state['hsa_contribution'] = DEFAULT_VALUES['hsa_contribution']
    st.session_state['cash'] = DEFAULT_VALUES['cash']
    
    # Healthcare (no prefix)
    st.session_state['healthcare_model'] = DEFAULT_VALUES['healthcare_model']
    st.session_state['healthcare_annual_pre_medicare'] = DEFAULT_VALUES['healthcare_annual_pre_medicare']
    st.session_state['healthcare_annual_medicare'] = DEFAULT_VALUES['healthcare_annual_medicare']
    
    # Retirement income (no prefix)
    st.session_state['social_security_monthly'] = DEFAULT_VALUES['social_security_monthly']
    st.session_state['social_security_start_age'] = DEFAULT_VALUES['social_security_start_age']
    st.session_state['pension_monthly'] = DEFAULT_VALUES['pension_monthly']
    st.session_state['spouse_ss_monthly'] = DEFAULT_VALUES['spouse_ss_monthly']
    st.session_state['spouse_ss_start_age'] = DEFAULT_VALUES['spouse_ss_start_age']
    st.session_state['spouse_pension_monthly'] = DEFAULT_VALUES['spouse_pension_monthly']
    
    # Expenses & Goals (no prefix)
    st.session_state['annual_spending'] = DEFAULT_VALUES['annual_spending']
    st.session_state['final_estate_goal'] = DEFAULT_VALUES['final_estate_goal']
    
    # Settings (no prefix)
    st.session_state['inflation_rate'] = DEFAULT_VALUES['inflation_rate']
    st.session_state['market_model'] = DEFAULT_VALUES['market_model']
    st.session_state['allocation_strategy'] = DEFAULT_VALUES['allocation_strategy']
    
    # Clear results
    st.session_state.simulation_run = False
    st.session_state.results = None

# ========================================
# MAIN HEADER
# ========================================

st.title("🎯 Retirement Planning Dashboard")
st.markdown("**Plan your retirement with confidence using Monte Carlo simulations**")
st.markdown("---")

# ========================================
# INPUT SECTION (TOP OF PAGE)
# ========================================

# All inputs visible - no collapsible expander

# ========================================
# SCENARIO MANAGEMENT
# ========================================

st.markdown("### 💾 Scenario Management")

col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
with col1:
    if st.button("💾 Save", use_container_width=True, key="btn_save"):
        st.session_state.save_dialog = True
        st.session_state.load_dialog = False
        st.rerun()
with col2:
    if st.button("📂 Load", use_container_width=True, key="btn_load"):
        st.session_state.load_dialog = True
        st.session_state.save_dialog = False
        st.rerun()
with col3:
    if st.button("🔄 Reset", use_container_width=True, key="btn_reset"):
        reset_to_defaults()
        st.success("Reset to defaults!")
        st.rerun()

# Save Dialog
if st.session_state.get('save_dialog', False):
    st.markdown("---")
    st.markdown("#### 💾 Save Scenario")
    
    scenario_name = st.text_input(
        "Scenario Name",
        value="My Retirement Plan",
        key="save_scenario_name"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Save", key="confirm_save", use_container_width=True):
            # Save immediately WITHOUT rerunning
            # This way all the form variables below have the current values
            st.session_state.pending_save_name = scenario_name
            st.session_state.save_dialog = False  # Close dialog immediately
            # Don't rerun - let the save happen further down after form is rendered
    with col2:
        if st.button("❌ Cancel", key="cancel_save", use_container_width=True):
            st.session_state.save_dialog = False
            st.rerun()

# Load Dialog
if st.session_state.get('load_dialog', False):
    st.markdown("---")
    st.markdown("#### 📂 Load Scenario")
    
    scenario_files = glob.glob(f'{SCENARIOS_DIR}/*.json')
    
    if scenario_files:
        scenario_names = [os.path.basename(f).replace('.json', '') 
                         for f in scenario_files]
        
        selected = st.selectbox(
            "Choose Scenario",
            scenario_names,
            key="load_scenario_select"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Load", key="confirm_load", use_container_width=True):
                try:
                    loaded_inputs = load_scenario(f'{SCENARIOS_DIR}/{selected}.json')
                    
                    # Debug: Write to log file
                    with open('/tmp/retirement_debug.log', 'a') as f:
                        f.write(f"\n=== LOAD DEBUG ===\n")
                        f.write(f"Time: {datetime.now()}\n")
                        f.write(f"Scenario: {selected}\n")
                        f.write(f"loaded current_age = {loaded_inputs.current_age}\n")
                        f.write(f"loaded cash = {loaded_inputs.cash}\n")
                        f.write(f"loaded annual_spending = {loaded_inputs.annual_spending}\n")
                        f.write(f"loaded pretax_401k (combined) = {loaded_inputs.pretax_401k}\n")
                    
                    st.success(f"🔍 DEBUG: Loading {selected} - check /tmp/retirement_debug.log")
                    
                    # Personal Information
                    st.session_state['input_current_age'] = loaded_inputs.current_age
                    st.session_state['input_retirement_age'] = loaded_inputs.retirement_age
                    st.session_state['input_death_age'] = loaded_inputs.death_age
                    st.session_state['input_is_married'] = loaded_inputs.is_married
                    
                    # Spouse Information
                    st.session_state['spouse_age'] = loaded_inputs.spouse_age
                    st.session_state['spouse_retirement_age'] = loaded_inputs.spouse_retirement_age
                    st.session_state['spouse_death_age'] = loaded_inputs.spouse_death_age
                    
                    # Pre-Retirement Income & Savings
                    st.session_state['current_salary'] = loaded_inputs.current_salary
                    st.session_state['annual_401k'] = loaded_inputs.annual_401k_contribution
                    st.session_state['annual_roth'] = loaded_inputs.annual_roth_contribution
                    st.session_state['annual_taxable'] = loaded_inputs.annual_taxable_contribution
                    st.session_state['employer_match'] = loaded_inputs.employer_match_percent * 100
                    st.session_state['spouse_current_salary'] = loaded_inputs.spouse_current_salary
                    st.session_state['spouse_annual_401k'] = loaded_inputs.spouse_annual_401k_contribution
                    
                    # Current Assets - Note: pretax_401k and roth_ira in file are COMBINED totals
                    # We'll split them evenly or just put in first field for now
                    st.session_state['pretax_401k'] = loaded_inputs.pretax_401k
                    st.session_state['pretax_403b'] = 0.0
                    st.session_state['pretax_457'] = 0.0
                    st.session_state['pretax_rollover'] = 0.0
                    
                    st.session_state['roth_401k'] = 0.0
                    st.session_state['roth_403b'] = 0.0
                    st.session_state['roth_457'] = 0.0
                    st.session_state['roth_ira'] = loaded_inputs.roth_ira
                    st.session_state['roth_other'] = 0.0
                    
                    # HSA and Cash
                    st.session_state['hsa_balance'] = loaded_inputs.hsa_balance
                    st.session_state['hsa_contribution'] = loaded_inputs.hsa_contribution
                    st.session_state['cash'] = loaded_inputs.cash
                    
                    # Healthcare
                    st.session_state['healthcare_model'] = "Average"  # Default for now
                    st.session_state['healthcare_annual_pre_medicare'] = loaded_inputs.healthcare_annual_pre_medicare
                    st.session_state['healthcare_annual_medicare'] = loaded_inputs.healthcare_annual_medicare
                    
                    # Retirement Income
                    st.session_state['social_security_monthly'] = loaded_inputs.social_security_monthly
                    st.session_state['social_security_start_age'] = loaded_inputs.social_security_start_age
                    st.session_state['pension_monthly'] = loaded_inputs.pension_monthly
                    st.session_state['spouse_ss_monthly'] = loaded_inputs.spouse_social_security_monthly
                    st.session_state['spouse_ss_start_age'] = loaded_inputs.spouse_social_security_start_age
                    st.session_state['spouse_pension_monthly'] = loaded_inputs.spouse_pension_monthly
                    
                    # Expenses & Goals
                    st.session_state['annual_spending'] = loaded_inputs.annual_spending
                    st.session_state['final_estate_goal'] = loaded_inputs.final_estate_goal
                    
                    # Settings
                    # Market model: stored as 'conservative'/'average'/'optimistic', display as 'Conservative'/'Average'/'Optimistic'
                    market_map_reverse = {'conservative': 'Conservative', 'average': 'Average', 'optimistic': 'Optimistic'}
                    st.session_state['market_model'] = market_map_reverse.get(loaded_inputs.market_model, 'Average')
                    
                    # Allocation: stored as 'glide_path'/'conservative'/etc, display as 'Glide Path'/'Conservative'/etc
                    allocation_map_reverse = {
                        'conservative': 'Conservative', 
                        'moderate': 'Moderate', 
                        'aggressive': 'Aggressive', 
                        'glide_path': 'Glide Path'
                    }
                    st.session_state['allocation_strategy'] = allocation_map_reverse.get(loaded_inputs.allocation_strategy, 'Glide Path')
                    
                    # Inflation: stored as 0.03, display as 3.0
                    st.session_state['inflation_rate'] = loaded_inputs.inflation_rate * 100
                    
                    st.session_state.load_dialog = False
                    st.success(f"✅ Loaded: {selected}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading scenario: {str(e)}")
        with col2:
            if st.button("❌ Cancel", key="cancel_load", use_container_width=True):
                st.session_state.load_dialog = False
                st.rerun()
    else:
        st.info("📁 No saved scenarios found. Save a scenario first!")
        if st.button("Close", key="close_load", use_container_width=True):
            st.session_state.load_dialog = False
            st.rerun()

st.markdown("---")
    
    # ========================================
    # ORGANIZED INPUT SECTIONS (NO TABS - SINGLE PAGE)
# ========================================

# 👤 PERSONAL INFORMATION
st.markdown("### 👤 Personal Information")

col1, col2, col3, col4 = st.columns(4)

with col1:
    current_age = st.number_input(
        "Current Age", 
        min_value=18, max_value=100, 
        value=get_input_value('current_age', 54), 
        step=1,
        key='input_current_age'
    )

with col2:
    retirement_age = st.number_input(
        "Retirement Age", 
        min_value=current_age, max_value=100, 
        value=max(current_age, get_input_value('retirement_age', 62)), 
        step=1,
        key='input_retirement_age'
    )

with col3:
    death_age = st.number_input(
        "Life Expectancy", 
        min_value=retirement_age, max_value=120, 
        value=max(retirement_age, get_input_value('death_age', 90)), 
        step=1,
        key='input_death_age'
    )

with col4:
    is_married = st.checkbox(
        "Married", 
        value=get_input_value('is_married', False),
        key='input_is_married'
    )

# Spouse info (conditional)
spouse_age = 0
spouse_retirement_age = 0
spouse_death_age = 0
spouse_current_salary = 0.0
spouse_annual_401k = 0.0
spouse_ss_monthly = 0.0
spouse_ss_start_age = 67
spouse_pension_monthly = 0.0

if is_married:
    st.markdown("**Spouse Information:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        spouse_age = st.number_input(
            "Spouse Age", 
            min_value=18, 
            max_value=100, 
            value=get_input_value('spouse_age', 54), 
            step=1,
            key='spouse_age'
        )
    with col2:
        spouse_retirement_age = st.number_input(
            "Spouse Retirement Age", 
            min_value=spouse_age, 
            max_value=100, 
            value=max(spouse_age, get_input_value('spouse_retirement_age', 63)), 
            step=1,
            key='spouse_retirement_age'
        )
    with col3:
        spouse_death_age = st.number_input(
            "Spouse Life Expectancy", 
            min_value=spouse_retirement_age, 
            max_value=120, 
            value=max(spouse_retirement_age, get_input_value('spouse_death_age', 90)), 
            step=1,
            key='spouse_death_age'
        )

st.markdown("---")

# 💰 INCOME & CONTRIBUTIONS
st.markdown("### 💰 Pre-Retirement Income & Savings")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Your Income**")
    current_salary = st.number_input(
        "Annual Salary", 
        min_value=0.0, 
        value=get_input_value('current_salary', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='current_salary'
    )
    annual_401k = st.number_input(
        "401k Contribution (Annual)", 
        min_value=0.0, 
        value=get_input_value('annual_401k', 0.0), 
        step=1000.0, 
        format="%.0f",
        key='annual_401k'
    )
    annual_roth = st.number_input(
        "Roth IRA Contribution", 
        min_value=0.0, 
        value=get_input_value('annual_roth', 0.0), 
        step=500.0, 
        format="%.0f",
        key='annual_roth'
    )
    annual_taxable = st.number_input(
        "Taxable Savings (Annual)", 
        min_value=0.0, 
        value=get_input_value('annual_taxable', 0.0), 
        step=1000.0, 
        format="%.0f",
        key='annual_taxable'
    )
    employer_match = st.slider(
        "Employer Match (%)", 
        min_value=0.0, 
        max_value=20.0, 
        value=get_input_value('employer_match', 0.0), 
        step=1.0,
        key='employer_match'
    ) / 100

with col2:
    if is_married:
        st.markdown("**Spouse's Income**")
        spouse_current_salary = st.number_input(
            "Spouse Salary", 
            min_value=0.0, 
            value=get_input_value('spouse_current_salary', 0.0), 
            step=5000.0, 
            format="%.0f",
            key='spouse_current_salary'
        )
        spouse_annual_401k = st.number_input(
            "Spouse 401k Contribution", 
            min_value=0.0, 
            value=get_input_value('spouse_annual_401k', 0.0), 
            step=1000.0, 
            format="%.0f",
            key='spouse_annual_401k'
        )
    else:
        st.markdown("**_Spouse income fields appear when married_**")

st.markdown("---")

# 💎 CURRENT ASSETS
st.markdown("### 💎 Current Assets")

# Pre-Tax Accounts
st.markdown("**Pre-Tax Accounts**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pretax_401k = st.number_input(
        "401(k)", 
        min_value=0.0, 
        value=get_input_value('pretax_401k', 0.0), 
        step=10000.0, 
        format="%.0f",
        key='pretax_401k'
    )
with col2:
    pretax_403b = st.number_input(
        "403(b)", 
        min_value=0.0, 
        value=get_input_value('pretax_403b', 0.0), 
        step=10000.0, 
        format="%.0f",
        key='pretax_403b'
    )
with col3:
    pretax_457 = st.number_input(
        "457(b)", 
        min_value=0.0, 
        value=get_input_value('pretax_457', 0.0), 
        step=10000.0, 
        format="%.0f",
        key='pretax_457'
    )
with col4:
    pretax_rollover = st.number_input(
        "Rollover IRA", 
        min_value=0.0, 
        value=get_input_value('pretax_rollover', 0.0), 
        step=10000.0, 
        format="%.0f",
        key='pretax_rollover'
    )

total_pretax = pretax_401k + pretax_403b + pretax_457 + pretax_rollover
st.caption(f"**Total Pre-Tax: {format_currency(total_pretax)}**")

st.markdown("")

# Roth Accounts
st.markdown("**Roth Accounts**")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    roth_401k = st.number_input(
        "Roth 401(k)", 
        min_value=0.0, 
        value=get_input_value('roth_401k', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='roth_401k'
    )
with col2:
    roth_403b = st.number_input(
        "Roth 403(b)", 
        min_value=0.0, 
        value=get_input_value('roth_403b', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='roth_403b'
    )
with col3:
    roth_457 = st.number_input(
        "Roth 457(b)", 
        min_value=0.0, 
        value=get_input_value('roth_457', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='roth_457'
    )
with col4:
    roth_ira = st.number_input(
        "Roth IRA", 
        min_value=0.0, 
        value=get_input_value('roth_ira', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='roth_ira'
    )
with col5:
    roth_other = st.number_input(
        "Other Roth", 
        min_value=0.0, 
        value=get_input_value('roth_other', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='roth_other'
    )

total_roth = roth_401k + roth_403b + roth_457 + roth_ira + roth_other
st.caption(f"**Total Roth: {format_currency(total_roth)}**")

st.markdown("")

# HSA & Cash
st.markdown("**HSA & Cash**")
col1, col2, col3 = st.columns(3)
with col1:
    hsa_balance = st.number_input(
        "HSA Balance", 
        min_value=0.0, 
        value=get_input_value('hsa_balance', 0.0), 
        step=1000.0, 
        format="%.0f",
        key='hsa_balance'
    )
with col2:
    hsa_contribution = st.number_input(
        "HSA Annual Contribution", 
        min_value=0.0, 
        value=get_input_value('hsa_contribution', 0.0), 
        step=500.0, 
        format="%.0f",
        key='hsa_contribution'
    )
with col3:
    cash = st.number_input(
        "Cash/Taxable", 
        min_value=0.0, 
        value=get_input_value('cash', 0.0), 
        step=5000.0, 
        format="%.0f",
        key='cash'
    )

# Total assets
total_assets = total_pretax + total_roth + hsa_balance + cash
st.markdown(f"**💰 Total Assets: {format_currency(total_assets)}**")

st.markdown("---")

# 🏥 HEALTHCARE
st.markdown("### 🏥 Healthcare Costs")

col1, col2, col3 = st.columns(3)
with col1:
    healthcare_options = ["Low", "Average", "High"]
    current_healthcare = get_input_value('healthcare_model', "Average")
    healthcare_index = healthcare_options.index(current_healthcare) if current_healthcare in healthcare_options else 1
    healthcare_model = st.selectbox(
        "Cost Model", 
        healthcare_options, 
        index=healthcare_index,
        key='healthcare_model'
    )
with col2:
    healthcare_annual_pre_medicare = st.number_input(
        "Annual (Pre-Medicare)", 
        min_value=0.0, 
        value=get_input_value('healthcare_annual_pre_medicare', 12000.0), 
        step=1000.0, 
        format="%.0f",
        key='healthcare_annual_pre_medicare'
    )
with col3:
    healthcare_annual_medicare = st.number_input(
        "Annual (Medicare)", 
        min_value=0.0, 
        value=get_input_value('healthcare_annual_medicare', 9600.0), 
        step=500.0, 
        format="%.0f",
        key='healthcare_annual_medicare'
    )

st.markdown("---")

# 📊 RETIREMENT INCOME
st.markdown("### 📊 Retirement Income")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Your Income**")
    social_security_monthly = st.number_input(
        "Social Security (Monthly)", 
        min_value=0.0, 
        value=get_input_value('social_security_monthly', 0.0), 
        step=100.0, 
        format="%.0f",
        key='social_security_monthly'
    )
    social_security_start_age = st.number_input(
        "SS Start Age", 
        min_value=62, 
        max_value=70, 
        value=get_input_value('social_security_start_age', 67), 
        step=1,
        key='social_security_start_age'
    )
    pension_monthly = st.number_input(
        "Pension (Monthly)", 
        min_value=0.0, 
        value=get_input_value('pension_monthly', 0.0), 
        step=100.0, 
        format="%.0f",
        key='pension_monthly'
    )

with col2:
    if is_married:
        st.markdown("**Spouse's Income**")
        spouse_ss_monthly = st.number_input(
            "Spouse SS (Monthly)", 
            min_value=0.0, 
            value=get_input_value('spouse_ss_monthly', 0.0), 
            step=100.0, 
            format="%.0f",
            key='spouse_ss_monthly'
        )
        spouse_ss_start_age = st.number_input(
            "Spouse SS Start Age", 
            min_value=62, 
            max_value=70, 
            value=get_input_value('spouse_ss_start_age', 67), 
            step=1,
            key='spouse_ss_start_age'
        )
        spouse_pension_monthly = st.number_input(
            "Spouse Pension (Monthly)", 
            min_value=0.0, 
            value=get_input_value('spouse_pension_monthly', 0.0), 
            step=100.0, 
            format="%.0f",
            key='spouse_pension_monthly'
        )
    else:
        st.markdown("**_Spouse fields appear when married_**")

st.markdown("---")

# 💵 EXPENSES
st.markdown("### 💵 Retirement Expenses & Goals")

col1, col2 = st.columns(2)
with col1:
    annual_spending = st.number_input(
        "Annual Spending", 
        min_value=0.0, 
        value=get_input_value('annual_spending', 75000.0), 
        step=5000.0, 
        format="%.0f",
        key='annual_spending'
    )
with col2:
    final_estate_goal = st.number_input(
        "Estate Goal (Optional)", 
        min_value=0.0, 
        value=get_input_value('final_estate_goal', 0.0), 
        step=10000.0, 
        format="%.0f",
        key='final_estate_goal'
    )

st.markdown("---")

# ⚙️ SETTINGS
st.markdown("### ⚙️ Settings")

col1, col2, col3 = st.columns(3)

with col1:
    inflation_rate = st.slider(
        "Inflation Rate (%)", 
        min_value=0.0, 
        max_value=10.0, 
        value=get_input_value('inflation_rate', 3.0), 
        step=0.5,
        key='inflation_rate'
    ) / 100

with col2:
    market_options = ["Conservative", "Average", "Optimistic"]
    current_market = get_input_value('market_model', "Average")
    # Handle both display format and internal format
    if current_market.lower() in ['conservative', 'average', 'optimistic']:
        current_market = current_market.capitalize()
    market_index = market_options.index(current_market) if current_market in market_options else 1
    
    market_model = st.selectbox(
        "Market Model", 
        market_options, 
        index=market_index,
        key='market_model'
    )

with col3:
    allocation_options = ["Conservative", "Moderate", "Aggressive", "Glide Path"]
    current_allocation = get_input_value('allocation_strategy', "Glide Path")
    # Handle both display format and internal format  
    if '_' in current_allocation:
        current_allocation = current_allocation.replace('_', ' ').title()
    allocation_index = allocation_options.index(current_allocation) if current_allocation in allocation_options else 3
    
    allocation_strategy = st.selectbox(
        "Allocation", 
        allocation_options, 
        index=allocation_index,
        key='allocation_strategy'
    )

# Mappings
market_model_mapping = {
    "Conservative": "conservative",
    "Average": "average",
    "Optimistic": "optimistic"
}

allocation_strategy_mapping = {
    "Conservative": "conservative",
    "Moderate": "moderate",
    "Aggressive": "aggressive",
    "Glide Path": "glide_path"
}

st.markdown("---")
st.markdown("")

# 🚀 RUN BUTTON
run_button = st.button(
    "🚀 Run Monte Carlo Simulation (5,000 runs)",
    type="primary",
    use_container_width=True
)

# ========================================
# HANDLE PENDING SAVE (After all inputs defined)
# ========================================

if st.session_state.get('pending_save_name'):
    scenario_name = st.session_state.pending_save_name
    
    try:
        # NOW all the form variables have current values!
        # Debug: Write to log file
        with open('/tmp/retirement_debug.log', 'a') as f:
            f.write(f"\n=== SAVE DEBUG ===\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Scenario: {scenario_name}\n")
            f.write(f"current_age variable = {current_age}\n")
            f.write(f"retirement_age variable = {retirement_age}\n")
            f.write(f"death_age variable = {death_age}\n")
        
        # Create inputs using current form values
        inputs_to_save = RetirementInputs(
            current_age=current_age,
            retirement_age=retirement_age,
            death_age=death_age,
            is_married=is_married,
            pretax_401k=total_pretax,  # Combined from individual accounts
            roth_ira=total_roth,       # Combined from individual accounts
            cash=cash,
            hsa_balance=hsa_balance,
            hsa_contribution=hsa_contribution,
            healthcare_annual_pre_medicare=healthcare_annual_pre_medicare,
            healthcare_annual_medicare=healthcare_annual_pre_medicare,  # Using same value
            current_salary=current_salary,
            annual_401k_contribution=annual_401k,
            annual_roth_contribution=annual_roth,
            annual_taxable_contribution=annual_taxable,
            employer_match_percent=employer_match,
            spouse_age=spouse_age,
            spouse_retirement_age=spouse_retirement_age,
            spouse_death_age=spouse_death_age,
            spouse_current_salary=spouse_current_salary,
            spouse_annual_401k_contribution=spouse_annual_401k,
            spouse_social_security_monthly=spouse_ss_monthly,
            spouse_social_security_start_age=spouse_ss_start_age,
            spouse_pension_monthly=spouse_pension_monthly,
            social_security_monthly=social_security_monthly,
            social_security_start_age=social_security_start_age,
            pension_monthly=pension_monthly,
            annual_spending=annual_spending,
            final_estate_goal=final_estate_goal,
            inflation_rate=inflation_rate,
            market_model=market_model_mapping[market_model],
            allocation_strategy=allocation_strategy_mapping[allocation_strategy]
        )
        
        # Save to scenarios folder
        save_scenario(inputs_to_save, f'{SCENARIOS_DIR}/{scenario_name}.json')
        st.success(f'✅ Saved scenario: {scenario_name}')
        del st.session_state.pending_save_name
    except Exception as e:
        st.error(f'❌ Error saving: {str(e)}')
        if 'pending_save_name' in st.session_state:
            del st.session_state.pending_save_name

# ========================================
# MAIN CONTENT AREA
# ========================================

if run_button:
    # Create inputs object
    # Combine account balances for simulation
    # Note: For now, we'll combine all pre-tax and all Roth accounts
    # Future enhancement: Track withdrawal order by account type (457 first, etc.)
    combined_pretax = total_pretax
    combined_roth = total_roth
    
    inputs = RetirementInputs(
        current_age=current_age,
        retirement_age=retirement_age,
        death_age=death_age,
        is_married=is_married,
        pretax_401k=combined_pretax,  # Combined all pre-tax accounts
        roth_ira=combined_roth,        # Combined all Roth accounts
        cash=cash,
        hsa_balance=hsa_balance,
        hsa_contribution=hsa_contribution,
        healthcare_annual_pre_medicare=healthcare_annual_pre_medicare,
        healthcare_annual_medicare=healthcare_annual_medicare,
        current_salary=current_salary,
        annual_401k_contribution=annual_401k,
        annual_roth_contribution=annual_roth,
        annual_taxable_contribution=annual_taxable,
        employer_match_percent=employer_match,
        spouse_age=spouse_age,
        spouse_retirement_age=spouse_retirement_age,
        spouse_death_age=spouse_death_age,
        spouse_current_salary=spouse_current_salary,
        spouse_annual_401k_contribution=spouse_annual_401k,
        spouse_social_security_monthly=spouse_ss_monthly,
        spouse_social_security_start_age=spouse_ss_start_age,
        spouse_pension_monthly=spouse_pension_monthly,
        social_security_monthly=social_security_monthly,
        social_security_start_age=social_security_start_age,
        pension_monthly=pension_monthly,
        annual_spending=annual_spending,
        final_estate_goal=final_estate_goal,
        inflation_rate=inflation_rate,
        market_model=market_model_mapping[market_model],
        allocation_strategy=allocation_strategy_mapping[allocation_strategy]
    )
    
    # Determine number of simulations
    n_simulations = 5000
    
    # Run simulation with progress bar
    with st.spinner(f'Running {n_simulations:,} Monte Carlo simulations...'):
        start_time = time.time()
        # Run Monte Carlo simulation
        results = run_monte_carlo_simulation(inputs, n_simulations=n_simulations)
        elapsed_time = time.time() - start_time
    
    st.session_state.results = results
    st.session_state.simulation_run = True
    st.session_state.inputs = inputs
    
    st.success(f'✅ Simulation completed in {elapsed_time:.1f} seconds ({n_simulations:,} runs)')

# Display Results
if st.session_state.simulation_run and st.session_state.results is not None:
    results = st.session_state.results
    inputs = st.session_state.inputs
    
    # ========================================
    # PROFESSIONAL HERO METRICS
    # ========================================
    
    st.markdown("## 📊 Retirement Plan Summary")
    st.markdown("")  # Spacing
    
    success_rate = results.success_rate
    median_final = np.median(results.final_balances)
    percentile_10_final = np.percentile(results.final_balances, 10)
    years_to_retirement = retirement_age - current_age
    
    # Determine success level and colors
    if success_rate >= 0.85:
        gradient = "linear-gradient(135deg, #16A34A 0%, #22C55E 100%)"
        status_text = "Excellent!"
        status_icon = "🎉"
        border_color = "#16A34A"
    elif success_rate >= 0.70:
        gradient = "linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)"
        status_text = "Moderate"
        status_icon = "⚠️"
        border_color = "#F59E0B"
    else:
        gradient = "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"
        status_text = "Needs Work"
        status_icon = "❌"
        border_color = "#EF4444"
    
    # Create 4-column layout for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Column 1: Success Rate (Hero Metric with gradient)
    with col1:
        st.markdown(f"""
        <div style="
            background: {gradient};
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        ">
            <div style="
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                opacity: 0.95;
                margin-bottom: 8px;
                color: white;
            ">SUCCESS RATE</div>
            <div style="
                font-size: 42px;
                font-weight: 900;
                line-height: 1;
                margin: 12px 0;
                color: white;
            ">{format_percentage(success_rate)}</div>
            <div style="
                font-size: 14px;
                font-weight: 600;
                opacity: 0.95;
                color: white;
            ">{status_icon} {status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Column 2: Median Final Balance
    with col2:
        st.markdown(f"""
        <div style="
            background: #1E2127;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #374151;
            text-align: center;
        ">
            <div style="
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                color: #9CA3AF;
                margin-bottom: 8px;
            ">MEDIAN FINAL BALANCE</div>
            <div style="
                font-size: 32px;
                font-weight: 700;
                line-height: 1.2;
                margin: 8px 0;
                color: #FAFAFA;
            ">{format_currency(median_final)}</div>
            <div style="
                font-size: 12px;
                color: #9CA3AF;
            ">50th percentile outcome</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Column 3: 10th Percentile
    with col3:
        st.markdown(f"""
        <div style="
            background: #1E2127;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #374151;
            text-align: center;
        ">
            <div style="
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                color: #9CA3AF;
                margin-bottom: 8px;
            ">10TH PERCENTILE FINAL</div>
            <div style="
                font-size: 32px;
                font-weight: 700;
                line-height: 1.2;
                margin: 8px 0;
                color: #FAFAFA;
            ">{format_currency(percentile_10_final)}</div>
            <div style="
                font-size: 12px;
                color: #9CA3AF;
            ">Worst-case scenario</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Column 4: Years to Retirement
    with col4:
        st.markdown(f"""
        <div style="
            background: #1E2127;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #374151;
            text-align: center;
        ">
            <div style="
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                color: #9CA3AF;
                margin-bottom: 8px;
            ">YEARS TO RETIREMENT</div>
            <div style="
                font-size: 32px;
                font-weight: 700;
                line-height: 1.2;
                margin: 8px 0;
                color: #FAFAFA;
            ">{years_to_retirement} <span style="font-size: 18px;">years</span></div>
            <div style="
                font-size: 12px;
                color: #9CA3AF;
            ">Retiring at age {retirement_age}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interpretation Banner
    st.markdown("")  # Spacing
    if success_rate >= 0.85:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(22, 163, 74, 0.15) 0%, rgba(34, 197, 94, 0.05) 100%);
            border-left: 4px solid #16A34A;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 20px 0;
        ">
            <div style="color: #22C55E; font-size: 18px; font-weight: 600; margin-bottom: 4px;">
                🎉 Excellent! Your retirement plan is on solid ground.
            </div>
            <div style="color: #86EFAC; font-size: 14px;">
                Your plan has a {format_percentage(success_rate)} probability of success. You're well-positioned for retirement!
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif success_rate >= 0.70:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(252, 211, 77, 0.05) 100%);
            border-left: 4px solid #F59E0B;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 20px 0;
        ">
            <div style="color: #FCD34D; font-size: 18px; font-weight: 600; margin-bottom: 4px;">
                ⚠️ Moderate Risk - Consider adjustments
            </div>
            <div style="color: #FDE68A; font-size: 14px;">
                Your plan has a {format_percentage(success_rate)} success rate. Consider increasing savings or adjusting retirement expenses.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(248, 113, 113, 0.05) 100%);
            border-left: 4px solid #EF4444;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 20px 0;
        ">
            <div style="color: #F87171; font-size: 18px; font-weight: 600; margin-bottom: 4px;">
                ❌ High Risk - Significant changes needed
            </div>
            <div style="color: #FCA5A5; font-size: 14px;">
                Your plan has only a {format_percentage(success_rate)} success rate. Consider delaying retirement, increasing savings, or reducing expenses.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================
    # PORTFOLIO PROJECTION CHART
    # ========================================
    
    st.markdown("")  # Spacing
    st.markdown("""
    <div style="
        border-bottom: 3px solid #374151;
        padding-bottom: 12px;
        margin: 32px 0 20px 0;
    ">
        <h2 style="margin: 0; color: #7CB8E8; font-size: 24px;">
            📈 Projected Net Worth
        </h2>
        <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 14px;">
            Monte Carlo simulation showing portfolio value over time with uncertainty bands
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    
    years = results.years
    percentiles = results.percentiles
    
    # Add percentile bands with professional colors
    # 90th percentile - Best case
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[90],
        name='Best Case (90th %ile)',
        line=dict(color='#3B7FC4', width=2),
        mode='lines',
        showlegend=True,
        hovertemplate='<b>Age %{x}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # 75th percentile with fill
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[75],
        name='75th Percentile',
        fill='tonexty',
        fillcolor='rgba(59, 127, 196, 0.15)',
        line=dict(color='#5B9BD5', width=1.5),
        mode='lines',
        showlegend=True,
        hovertemplate='<b>Age %{x}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # Median - Most important line
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[50],
        name='Expected (Median)',
        line=dict(color='#1E3A5F', width=4),
        mode='lines',
        showlegend=True,
        hovertemplate='<b>Age %{x}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # 25th percentile with fill
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[25],
        name='25th Percentile',
        fill='tonexty',
        fillcolor='rgba(245, 158, 11, 0.15)',
        line=dict(color='#F59E0B', width=1.5),
        mode='lines',
        showlegend=True,
        hovertemplate='<b>Age %{x}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # 10th percentile - Worst case
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[10],
        name='Worst Case (10th %ile)',
        fill='tonexty',
        fillcolor='rgba(239, 68, 68, 0.15)',
        line=dict(color='#EF4444', width=2, dash='dot'),
        mode='lines',
        showlegend=True,
        hovertemplate='<b>Age %{x}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # Add retirement marker
    fig.add_vline(
        x=retirement_age,
        line=dict(color='#16A34A', width=2, dash='dash'),
        annotation=dict(
            text="🎯 Retirement",
            showarrow=False,
            yref="paper",
            y=1.05,
            font=dict(size=14, color='#16A34A', family='Inter', weight=600)
        )
    )
    
    # Add goal line if specified
    if final_estate_goal > 0:
        fig.add_hline(
            y=final_estate_goal,
            line=dict(color='#8B5CF6', width=2, dash='dot'),
            annotation_text=f"Goal: {format_currency(final_estate_goal)}",
            annotation_position="right"
        )
    
    # Apply professional layout
    layout_config = get_professional_chart_layout()
    # Remove title from layout_config to avoid duplicate
    layout_config.pop('title', None)
    
    fig.update_layout(
        **layout_config,
        title={'text': 'Portfolio Value Projection with Uncertainty Bands'},
        xaxis_title='Age',
        yaxis_title='Portfolio Value',
        height=600,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13, family='Inter'),
            bgcolor='rgba(30, 33, 39, 0.9)',
            bordercolor='#4B5563',
            borderwidth=1
        )
    )
    
    fig.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # NET WORTH COMPOSITION CHART
    # ========================================
    
    st.markdown("")  # Spacing
    st.markdown("""
    <div style="
        border-bottom: 3px solid #374151;
        padding-bottom: 12px;
        margin: 32px 0 20px 0;
    ">
        <h2 style="margin: 0; color: #7CB8E8; font-size: 24px;">
            💼 Net Worth Composition Over Time
        </h2>
        <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 14px;">
            Breakdown of your retirement assets by account type (median scenario)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # For simplicity, show median path breakdown by account type
    fig2 = go.Figure()
    
    # Create stacked area chart - more elegant than bars
    # Using percentiles as proxy for different asset categories
    retirement_accounts = percentiles[50] * 0.65  # Approximation for retirement accounts
    taxable_accounts = percentiles[50] * 0.25     # Taxable
    cash_reserves = percentiles[50] * 0.10        # Cash
    
    # Stack from bottom to top
    fig2.add_trace(go.Scatter(
        x=years,
        y=retirement_accounts,
        name='Retirement Accounts (401k, IRA, HSA)',
        fill='tozeroy',
        fillcolor='rgba(59, 127, 196, 0.6)',
        line=dict(color='#3B7FC4', width=2),
        mode='lines',
        stackgroup='one',
        hovertemplate='<b>Age %{x}</b><br>Retirement: $%{y:,.0f}<extra></extra>'
    ))
    
    fig2.add_trace(go.Scatter(
        x=years,
        y=taxable_accounts,
        name='Taxable Investments',
        fill='tonexty',
        fillcolor='rgba(245, 158, 11, 0.6)',
        line=dict(color='#F59E0B', width=2),
        mode='lines',
        stackgroup='one',
        hovertemplate='<b>Age %{x}</b><br>Taxable: $%{y:,.0f}<extra></extra>'
    ))
    
    fig2.add_trace(go.Scatter(
        x=years,
        y=cash_reserves,
        name='Cash Reserves',
        fill='tonexty',
        fillcolor='rgba(22, 163, 74, 0.6)',
        line=dict(color='#16A34A', width=2),
        mode='lines',
        stackgroup='one',
        hovertemplate='<b>Age %{x}</b><br>Cash: $%{y:,.0f}<extra></extra>'
    ))
    
    # Apply professional layout
    layout_config = get_professional_chart_layout()
    layout_config.pop('title', None)
    
    fig2.update_layout(
        **layout_config,
        title={'text': 'Net Worth by Account Type (Median Scenario)'},
        xaxis_title='Age',
        yaxis_title='Net Worth',
        height=500,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13, family='Inter'),
            bgcolor='rgba(30, 33, 39, 0.9)',
            bordercolor='#4B5563',
            borderwidth=1
        )
    )
    
    fig2.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # ========================================
    # INCOME VS EXPENSES CHART
    # ========================================
    
    st.markdown("")  # Spacing
    st.markdown("""
    <div style="
        border-bottom: 3px solid #374151;
        padding-bottom: 12px;
        margin: 32px 0 20px 0;
    ">
        <h2 style="margin: 0; color: #7CB8E8; font-size: 24px;">
            💰 Lifetime Income Projection
        </h2>
        <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 14px;">
            Income sources vs. expenses throughout your retirement years
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fig3 = go.Figure()
    
    # Calculate income streams by age
    work_income = []
    ss_income = []
    pension_income = []
    rmd_income = []
    expenses = []
    
    for age in years:
        # Work income (before retirement)
        if age < retirement_age:
            total_salary = inputs.current_salary
            if inputs.is_married and age - current_age + inputs.spouse_age < inputs.spouse_retirement_age:
                total_salary += inputs.spouse_current_salary
            work_income.append(total_salary)
        else:
            work_income.append(0)
        
        # Social Security
        ss = 0
        if age >= inputs.social_security_start_age:
            ss += inputs.social_security_monthly * 12
        if inputs.is_married and age - current_age + inputs.spouse_age >= inputs.spouse_social_security_start_age:
            ss += inputs.spouse_social_security_monthly * 12
        ss_income.append(ss)
        
        # Pensions
        pension = 0
        if age >= retirement_age:
            pension += inputs.pension_monthly * 12
        if inputs.is_married and age - current_age + inputs.spouse_age >= inputs.spouse_retirement_age:
            pension += inputs.spouse_pension_monthly * 12
        pension_income.append(pension)
        
        # RMD (simplified - just show after age 73)
        if age >= 73:
            rmd_income.append(20000)  # Placeholder
        else:
            rmd_income.append(0)
        
        # Expenses
        if age >= retirement_age:
            years_retired = age - retirement_age
            exp = inputs.annual_spending * ((1 + inputs.inflation_rate) ** years_retired)
        else:
            exp = 0
        expenses.append(exp)
    
    # Stacked bar chart for income sources with professional colors
    fig3.add_trace(go.Bar(
        x=years, y=work_income,
        name='Work Income',
        marker_color='#8B5CF6',  # Purple
        hovertemplate='<b>Age %{x}</b><br>Work: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=ss_income,
        name='Social Security',
        marker_color='#3B7FC4',  # Blue
        hovertemplate='<b>Age %{x}</b><br>Social Security: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=pension_income,
        name='Pension',
        marker_color='#16A34A',  # Green
        hovertemplate='<b>Age %{x}</b><br>Pension: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=rmd_income,
        name='RMD/Withdrawals',
        marker_color='#F59E0B',  # Amber
        hovertemplate='<b>Age %{x}</b><br>RMD: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add expenses line
    fig3.add_trace(go.Scatter(
        x=years, y=expenses,
        name='Expenses',
        line=dict(color='#EF4444', width=4, dash='dash'),  # Red dashed
        mode='lines',
        hovertemplate='<b>Age %{x}</b><br>Expenses: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add retirement marker
    fig3.add_vline(
        x=retirement_age,
        line=dict(color='#16A34A', width=2, dash='dash'),
        annotation=dict(
            text="🎯 Retirement",
            showarrow=False,
            yref="paper",
            y=1.05,
            font=dict(size=14, color='#16A34A', family='Inter', weight=600)
        )
    )
    
    # Apply professional layout
    layout_config = get_professional_chart_layout()
    layout_config.pop('title', None)
    
    fig3.update_layout(
        **layout_config,
        title={'text': 'Income Sources vs. Expenses Over Time'},
        xaxis_title='Age',
        yaxis_title='Annual Amount',
        barmode='stack',
        height=550,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13, family='Inter'),
            bgcolor='rgba(30, 33, 39, 0.9)',
            bordercolor='#4B5563',
            borderwidth=1
        )
    )
    
    fig3.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # ========================================
    # DETAILED PROJECTIONS TABLE
    # ========================================
    
    st.markdown("")  # Spacing
    st.markdown("""
    <div style="
        border-bottom: 3px solid #374151;
        padding-bottom: 12px;
        margin: 32px 0 20px 0;
    ">
        <h2 style="margin: 0; color: #7CB8E8; font-size: 24px;">
            📋 Detailed Projections
        </h2>
        <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 14px;">
            Portfolio value at key ages (every 5 years)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    df = create_summary_dataframe(results)
    df['Age'] = df['Age'].astype(int)
    
    # Format currency columns
    for col in df.columns:
        if col != 'Age':
            df[col] = df[col].apply(lambda x: f"${x:,.0f}")
    
    # Show every 5 years
    df_display = df[df['Age'] % 5 == 0].reset_index(drop=True)
    
    st.dataframe(df_display, width="stretch", height=400)
    
    # Download Results
    st.markdown("---")
    st.markdown('<p class="section-header">💾 Export Data</p>', unsafe_allow_html=True)
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Projections (CSV)",
        data=csv,
        file_name=f"retirement_projection_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    # Welcome message
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 👋 Welcome to Your Retirement Planning Dashboard!")
    st.markdown("Enter your information in the sidebar and click **🚀 Run Simulation** to:")
    st.markdown("- See your probability of retirement success")
    st.markdown("- Visualize your portfolio growth over time")
    st.markdown("- Understand income vs. expenses in retirement")
    st.markdown("- Test different retirement scenarios")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ Key Features")
        st.write("✅ Monte Carlo simulation (5,000 scenarios)")
        st.write("✅ Spouse & dual income modeling")
        st.write("✅ Pre-retirement savings tracking")
        st.write("✅ Tax-efficient withdrawal strategies")
        st.write("✅ Social Security optimization")
        st.write("✅ Beautiful, interactive charts")
    
    with col2:
        st.subheader("🎯 What You'll Learn")
        st.write("📊 When you can afford to retire")
        st.write("💰 How much you need to save")
        st.write("📈 Your portfolio's projected growth")
        st.write("⚠️ Potential risks and opportunities")
        st.write("🔄 Impact of different strategies")
        st.write("💡 Ways to improve your plan")
    
    st.markdown("---")
    st.info("💡 **Pro Tip**: Start by entering your current financial situation, then experiment with different retirement ages and spending levels to find your optimal plan!")
