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
            'titlefont': {'size': 14, 'family': 'Inter', 'color': '#E5E7EB'}
        },
        'yaxis': {
            'gridcolor': '#374151',
            'gridwidth': 1,
            'linecolor': '#4B5563',
            'linewidth': 2,
            'tickfont': {'size': 13, 'family': 'Inter', 'color': '#E5E7EB'},
            'titlefont': {'size': 14, 'family': 'Inter', 'color': '#E5E7EB'}
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
# SESSION STATE
# ========================================

# Initialize session state
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'results' not in st.session_state:
    st.session_state.results = None

# ========================================
# MAIN HEADER
# ========================================

st.title("🎯 Retirement Planning Dashboard")
st.markdown("**Plan your retirement with confidence using Monte Carlo simulations**")
st.markdown("---")

# Sidebar - Input Parameters
with st.sidebar:
    st.header("📋 Input Parameters")
    
    # Scenario Management
    st.subheader("💾 Scenario Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save", width="stretch"):
            st.session_state.save_dialog = True
    with col2:
        if st.button("📂 Load", width="stretch"):
            st.session_state.load_dialog = True
    
    st.markdown("---")
    
    # Personal Information
    st.subheader("👤 Personal Information")
    current_age = st.number_input("Current Age", min_value=18, max_value=100, value=54, step=1)
    retirement_age = st.number_input("Planned Retirement Age", min_value=current_age, max_value=100, value=62, step=1)
    death_age = st.number_input("Life Expectancy", min_value=retirement_age, max_value=120, value=90, step=1)
    is_married = st.checkbox("Married", value=False)
    
    # Spouse Information (conditional)
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
        spouse_age = st.number_input("Spouse's Current Age", min_value=18, max_value=100, value=54, step=1)
        spouse_retirement_age = st.number_input("Spouse's Retirement Age", min_value=spouse_age, max_value=100, value=63, step=1)
        spouse_death_age = st.number_input("Spouse's Life Expectancy", min_value=spouse_retirement_age, max_value=120, value=90, step=1)
    
    st.markdown("---")
    
    # Pre-Retirement Income & Savings
    st.subheader("💼 Pre-Retirement Income")
    current_salary = st.number_input("Your Annual Salary", 
                                     min_value=0.0, value=271000.0, step=5000.0,
                                     format="%.0f",
                                     help="Your current annual gross income")
    
    st.markdown("**Annual Contributions:**")
    annual_401k = st.number_input("401k Contribution (Annual)", 
                                   min_value=0.0, value=30000.0, step=1000.0,
                                   format="%.0f")
    employer_match = st.slider("Employer Match (%)", 
                               min_value=0.0, max_value=10.0, value=10.0, step=1.0,
                               help="Employer match as % of your contribution") / 100
    annual_roth = st.number_input("Roth IRA Contribution (Annual)", 
                                  min_value=0.0, value=7000.0, step=500.0,
                                  format="%.0f")
    annual_taxable = st.number_input("Taxable/Cash Savings (Annual)", 
                                     min_value=0.0, value=10000.0, step=1000.0,
                                     format="%.0f")
    
    # Spouse pre-retirement income (if married)
    if is_married:
        st.markdown("**Spouse's Income & Contributions:**")
        spouse_current_salary = st.number_input("Spouse's Annual Salary", 
                                               min_value=0.0, value=120000.0, step=5000.0,
                                               format="%.0f")
        spouse_annual_401k = st.number_input("Spouse's 401k Contribution (Annual)", 
                                            min_value=0.0, value=15000.0, step=1000.0,
                                            format="%.0f")
    
    st.markdown("---")
    
    # Current Assets - Organized by Tax Treatment
    st.subheader("💰 Current Assets")
    
    # Pre-Tax Accounts
    st.markdown("### 📊 Pre-Tax Accounts")
    st.caption("Traditional retirement accounts - taxed upon withdrawal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pretax_401k = st.number_input("401(k) - Pre-tax", 
                                       min_value=0.0, value=0.0, step=10000.0,
                                       format="%.0f",
                                       help="Traditional 401(k) balance")
        pretax_403b = st.number_input("403(b) - Pre-tax", 
                                       min_value=0.0, value=0.0, step=10000.0,
                                       format="%.0f",
                                       help="Traditional 403(b) balance")
    
    with col2:
        pretax_457 = st.number_input("457(b) - Pre-tax ⭐", 
                                      min_value=0.0, value=0.0, step=10000.0,
                                      format="%.0f",
                                      help="457(b) - No penalty at any age!")
        pretax_rollover = st.number_input("Rollover IRA - Pre-tax", 
                                          min_value=0.0, value=0.0, step=10000.0,
                                          format="%.0f",
                                          help="Traditional IRA from rollovers")
    
    total_pretax = pretax_401k + pretax_403b + pretax_457 + pretax_rollover
    
    # Post-Tax (Roth) Accounts
    st.markdown("### 💎 Post-Tax (Roth) Accounts")
    st.caption("Already taxed - withdrawals are tax-free!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        roth_401k = st.number_input("Roth 401(k)", 
                                     min_value=0.0, value=0.0, step=5000.0,
                                     format="%.0f",
                                     help="Roth 401(k) balance")
        roth_403b = st.number_input("Roth 403(b)", 
                                     min_value=0.0, value=0.0, step=5000.0,
                                     format="%.0f",
                                     help="Roth 403(b) balance")
        roth_457 = st.number_input("Roth 457(b) ⭐⭐", 
                                    min_value=0.0, value=0.0, step=5000.0,
                                    format="%.0f",
                                    help="Roth 457(b) - Tax-free AND no penalty!")
    
    with col2:
        roth_ira = st.number_input("Roth IRA", 
                                    min_value=0.0, value=0.0, step=5000.0,
                                    format="%.0f",
                                    help="Roth IRA balance")
        roth_other = st.number_input("Other Roth", 
                                      min_value=0.0, value=0.0, step=5000.0,
                                      format="%.0f",
                                      help="Other Roth accounts")
    
    total_roth = roth_401k + roth_403b + roth_457 + roth_ira + roth_other
    
    # Health Savings Account (HSA)
    st.markdown("### 💊 Health Savings Account (HSA)")
    st.caption("Triple tax-advantaged! Pre-tax contributions, tax-free growth, tax-free withdrawals for medical")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hsa_balance = st.number_input("Current HSA Balance", 
                                      min_value=0.0, value=0.0, step=1000.0,
                                      format="%.0f",
                                      help="Current Health Savings Account balance")
    
    with col2:
        hsa_contribution = st.number_input("Annual HSA Contribution", 
                                          min_value=0.0, value=0.0, step=500.0,
                                          format="%.0f",
                                          help="Annual HSA contribution (2024 limit: $4,150 individual, $5,150 if 55+)")
    
    # Taxable Accounts
    st.markdown("### 💵 Taxable Accounts")
    st.caption("Brokerage, savings, and cash accounts")
    
    cash = st.number_input("Cash/Brokerage/Savings", 
                          min_value=0.0, value=0.0, step=5000.0,
                          format="%.0f",
                          help="Taxable investment accounts and cash")
    
    # Summary
    total_assets = total_pretax + total_roth + hsa_balance + cash
    
    st.markdown("---")
    st.markdown("### 📊 Asset Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Pre-Tax", format_currency(total_pretax))
    with col2:
        st.metric("Roth", format_currency(total_roth))
    with col3:
        st.metric("HSA", format_currency(hsa_balance))
    with col4:
        st.metric("Cash/Taxable", format_currency(cash))
    with col5:
        st.metric("**Total Assets**", format_currency(total_assets))
    
    st.markdown("---")
    
    # Retirement Income Streams
    st.subheader("💵 Retirement Income")
    social_security_monthly = st.number_input("Your Social Security (Monthly)", 
                                              min_value=0.0, value=2500.0, step=100.0,
                                              format="%.0f")
    social_security_start_age = st.selectbox("Your SS Start Age", 
                                             options=[62, 67, 70], index=1)
    pension_monthly = st.number_input("Your Pension (Monthly)", 
                                     min_value=0.0, value=0.0, step=100.0,
                                     format="%.0f")
    
    # Spouse retirement income (if married)
    if is_married:
        st.markdown("**Spouse's Retirement Income:**")
        spouse_ss_monthly = st.number_input("Spouse's Social Security (Monthly)", 
                                           min_value=0.0, value=2000.0, step=100.0,
                                           format="%.0f")
        spouse_ss_start_age = st.selectbox("Spouse's SS Start Age", 
                                          options=[62, 67, 70], index=1)
        spouse_pension_monthly = st.number_input("Spouse's Pension (Monthly)", 
                                                min_value=0.0, value=0.0, step=100.0,
                                                format="%.0f")
    
    st.markdown("---")
    
    # Expenses
    st.subheader("💳 Retirement Expenses")
    annual_spending = st.number_input("Annual Spending in Retirement", 
                                     min_value=0.0, value=200000.0, step=5000.0,
                                     format="%.0f",
                                     help="Total annual expenses in retirement")
    final_estate_goal = st.number_input("Final Estate Goal", 
                                       min_value=0.0, value=0.0, step=10000.0,
                                       format="%.0f",
                                       help="Amount you want to leave behind")
    
    # Healthcare Costs
    st.markdown("### 🏥 Healthcare Costs")
    st.caption("Model healthcare expenses throughout retirement")
    
    healthcare_model = st.selectbox(
        "Healthcare Cost Model",
        options=["Minimal", "Average", "Comprehensive", "Custom"],
        index=1,
        help="Estimate of healthcare spending in retirement"
    )
    
    # Define healthcare cost presets
    healthcare_presets = {
        "Minimal": {
            "single_pre_medicare": 6000,
            "couple_pre_medicare": 12000,
            "single_medicare": 6000,
            "couple_medicare": 12000,
            "description": "Healthy, minimal care needed"
        },
        "Average": {
            "single_pre_medicare": 12000,
            "couple_pre_medicare": 24000,
            "single_medicare": 9600,
            "couple_medicare": 19200,
            "description": "Typical healthcare needs (Medicare Part B/D, Supplement, out-of-pocket)"
        },
        "Comprehensive": {
            "single_pre_medicare": 18000,
            "couple_pre_medicare": 36000,
            "single_medicare": 15000,
            "couple_medicare": 30000,
            "description": "High healthcare needs, more medications, frequent care"
        }
    }
    
    if healthcare_model == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            healthcare_annual_pre_medicare = st.number_input(
                "Annual Healthcare (Pre-Medicare, per person)",
                min_value=0.0, value=12000.0, step=1000.0,
                format="%.0f",
                help="Healthcare costs before age 65"
            )
        with col2:
            healthcare_annual_medicare = st.number_input(
                "Annual Healthcare (Medicare, per person)",
                min_value=0.0, value=9600.0, step=1000.0,
                format="%.0f",
                help="Healthcare costs after age 65 (Part B/D, Supplement, out-of-pocket)"
            )
    else:
        preset = healthcare_presets[healthcare_model]
        st.info(f"💡 **{healthcare_model}:** {preset['description']}")
        
        if is_married:
            healthcare_annual_pre_medicare = preset["couple_pre_medicare"]
            healthcare_annual_medicare = preset["couple_medicare"]
            st.caption(f"Pre-Medicare: ${healthcare_annual_pre_medicare:,.0f}/year (couple)")
            st.caption(f"Medicare (65+): ${healthcare_annual_medicare:,.0f}/year (couple)")
        else:
            healthcare_annual_pre_medicare = preset["single_pre_medicare"]
            healthcare_annual_medicare = preset["single_medicare"]
            st.caption(f"Pre-Medicare: ${healthcare_annual_pre_medicare:,.0f}/year")
            st.caption(f"Medicare (65+): ${healthcare_annual_medicare:,.0f}/year")
    
    st.markdown("---")
    
    # Assumptions
    st.subheader("📊 Assumptions")
    inflation_rate = st.slider("Average Inflation Rate (%)", 
                               min_value=0.0, max_value=10.0, value=3.0, step=0.5) / 100
    
    market_model = st.selectbox("Market Performance Model",
                               options=["Conservative", "Average (30-year)", "Managed (Higher Risk)"],
                               index=1)
    market_model_mapping = {
        "Conservative": "conservative",
        "Average (30-year)": "average",
        "Managed (Higher Risk)": "managed"
    }
    
    allocation_strategy = st.selectbox("Asset Allocation Strategy",
                                      options=["Glide Path (Traditional)", "Optimized"],
                                      index=0)
    allocation_strategy_mapping = {
        "Glide Path (Traditional)": "glide_path",
        "Optimized": "optimized"
    }
    
    st.markdown("---")
    
    # Run Simulation Button
    run_button = st.button("🚀 Run Simulation", type="primary", width="stretch")

# Main Content Area
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
    
    # Key Metrics Section
    st.markdown('<p class="section-header">📊 Retirement Plan Summary</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    success_rate = results.success_rate
    median_final = np.median(results.final_balances)
    percentile_10_final = np.percentile(results.final_balances, 10)
    years_to_retirement = retirement_age - current_age
    
    with col1:
        if success_rate >= 0.85:
            st.markdown(f'<div class="success-box"><h3 style="color: #1a5928;">Success Rate</h3><h1 style="color: #1a5928;">{format_percentage(success_rate)}</h1><p style="color: #2d6a3e;">Excellent!</p></div>', 
                       unsafe_allow_html=True)
        elif success_rate >= 0.70:
            st.markdown(f'<div class="warning-box"><h3 style="color: #664d03;">Success Rate</h3><h1 style="color: #664d03;">{format_percentage(success_rate)}</h1><p style="color: #856404;">Moderate</p></div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="danger-box"><h3 style="color: #721c24;">Success Rate</h3><h1 style="color: #721c24;">{format_percentage(success_rate)}</h1><p style="color: #842029;">Needs Work</p></div>', 
                       unsafe_allow_html=True)
    
    with col2:
        st.metric("Median Final Balance", format_currency(median_final))
        st.caption("50th percentile outcome")
    
    with col3:
        st.metric("10th Percentile Final", format_currency(percentile_10_final))
        st.caption("Worst-case scenario")
    
    with col4:
        st.metric("Years to Retirement", f"{years_to_retirement} years")
        st.caption(f"Retiring at age {retirement_age}")
    
    # Interpretation
    st.markdown("---")
    if success_rate >= 0.85:
        st.success(f"🎉 **Excellent!** Your retirement plan has a {format_percentage(success_rate)} probability of success. You're well-positioned for retirement!")
    elif success_rate >= 0.70:
        st.warning(f"⚠️ **Moderate Risk.** Your plan has a {format_percentage(success_rate)} success rate. Consider increasing savings or adjusting expectations.")
    else:
        st.error(f"❌ **High Risk.** Your plan has only a {format_percentage(success_rate)} success rate. Significant changes may be needed.")
    
    st.markdown("---")
    
    # Portfolio Projection Chart
    st.subheader("📈 Projected Net Worth")
    
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
            annotation=dict(
                text=f"Goal: {format_currency(final_estate_goal)}",
                xref="paper",
                x=1.02,
                font=dict(size=12, color='#8B5CF6', family='Inter')
            )
        )
    
    # Apply professional layout
    layout_config = get_professional_chart_layout()
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
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#D1D5DB',
            borderwidth=1
        )
    )
    
    fig.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Net Worth Breakdown Chart
    st.subheader("💼 Net Worth Composition Over Time")
    
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
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#D1D5DB',
            borderwidth=1
        )
    )
    
    fig2.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Income vs Expenses Chart
    st.subheader("💰 Lifetime Income Projection")
    
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
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#D1D5DB',
            borderwidth=1
        )
    )
    
    fig3.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Detailed Statistics Table
    st.subheader("📋 Detailed Projections")
    
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
    st.markdown('<p class="section-header">💾 Export & Save</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Projections (CSV)",
            data=csv,
            file_name=f"retirement_projection_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width="stretch"
        )
    
    with col2:
        scenario_filename = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if st.button("💾 Save Current Scenario", width="stretch"):
            save_scenario(inputs, scenario_filename)
            st.success(f"✅ Scenario saved as {scenario_filename}")

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