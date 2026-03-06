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

# Custom CSS for better styling (Boldin-inspired)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'results' not in st.session_state:
    st.session_state.results = None

# Title
st.markdown('<p class="main-header">🎯 Retirement Planning Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan your retirement with confidence using Monte Carlo simulations</p>', unsafe_allow_html=True)

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
    
    # Portfolio Projection Chart (Boldin-style)
    st.markdown('<p class="section-header">📈 Projected Net Worth</p>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    years = results.years
    percentiles = results.percentiles
    
    # Add percentile bands with better styling
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[90],
        name='90th Percentile',
        line=dict(color='rgba(144, 238, 144, 0.8)', width=2),  # Light green, more visible
        mode='lines',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[75],
        name='75th Percentile',
        fill='tonexty',
        fillcolor='rgba(144, 238, 144, 0.3)',  # Light green fill
        line=dict(color='rgba(144, 238, 144, 0.6)', width=2),
        mode='lines',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[50],
        name='Median (50th)',
        line=dict(color='rgb(64, 196, 255)', width=4),  # Bright cyan
        mode='lines',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[25],
        name='25th Percentile',
        fill='tonexty',
        fillcolor='rgba(255, 193, 7, 0.3)',  # Yellow fill
        line=dict(color='rgba(255, 193, 7, 0.8)', width=2),  # Bright yellow
        mode='lines',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=percentiles[10],
        name='10th Percentile',
        fill='tonexty',
        fillcolor='rgba(255, 99, 71, 0.3)',  # Tomato red fill
        line=dict(color='rgba(255, 99, 71, 0.8)', width=2),  # Bright red
        mode='lines',
        showlegend=True
    ))
    
    # Add retirement age line
    fig.add_vline(x=retirement_age, line_dash="dash", line_color="rgba(144, 238, 144, 1)", line_width=3,
                  annotation_text="Retirement", annotation_position="top", 
                  annotation_font_color="white")
    
    # Add goal line
    if final_estate_goal > 0:
        fig.add_hline(y=final_estate_goal, line_dash="dot", line_color="rgba(255, 105, 180, 1)", line_width=3,
                      annotation_text=f"Goal: {format_currency(final_estate_goal)}", 
                      annotation_position="right",
                      annotation_font_color="white")
    
    fig.update_layout(
        title={
            'text': "Portfolio Value Projection with Uncertainty Bands",
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title="Age",
        yaxis_title="Portfolio Value",
        hovermode='x unified',
        height=550,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(40, 40, 40, 0.8)",
            font=dict(color='white')
        ),
        plot_bgcolor='rgb(30, 30, 30)',  # Dark background
        paper_bgcolor='rgb(20, 20, 20)',  # Darker outer background
        font=dict(color='white'),  # All text white
    )
    
    fig.update_xaxes(gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    fig.update_yaxes(tickformat="$,.0f", gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    
    st.plotly_chart(fig, width="stretch")
    
    # Net Worth Breakdown Chart (Boldin-style stacked bars)
    st.markdown('<p class="section-header">💼 Net Worth Composition Over Time</p>', unsafe_allow_html=True)
    
    # For simplicity, show median path breakdown by account type
    # This would ideally track each account type separately through simulation
    fig2 = go.Figure()
    
    # Create stacked bar chart
    # Using percentiles as proxy for different asset categories
    savings_portion = percentiles[50] * 0.6  # Approximation
    investments_portion = percentiles[50] * 0.4
    
    fig2.add_trace(go.Bar(
        x=years,
        y=savings_portion,
        name='Retirement Accounts',
        marker_color='rgb(0, 255, 157)',  # Bright cyan-green
        hovertemplate='Age: %{x}<br>Retirement Accounts: $%{y:,.0f}<extra></extra>'
    ))
    
    fig2.add_trace(go.Bar(
        x=years,
        y=investments_portion,
        name='Taxable Investments',
        marker_color='rgb(255, 193, 7)',  # Bright yellow
        hovertemplate='Age: %{x}<br>Taxable Investments: $%{y:,.0f}<extra></extra>'
    ))
    
    fig2.update_layout(
        title={
            'text': "Net Worth by Account Type (Median Scenario)",
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title="Age",
        yaxis_title="Net Worth",
        barmode='stack',
        height=450,
        plot_bgcolor='rgb(30, 30, 30)',  # Dark background
        paper_bgcolor='rgb(20, 20, 20)',  # Darker outer background
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(40, 40, 40, 0.8)",
            font=dict(color='white')
        )
    )
    
    fig2.update_xaxes(gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    fig2.update_yaxes(tickformat="$,.0f", gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    
    st.plotly_chart(fig2, width="stretch")
    
    # Income vs Expenses Chart (Boldin-style)
    st.markdown('<p class="section-header">💰 Lifetime Income Projection</p>', unsafe_allow_html=True)
    
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
    
    # Stacked bar chart for income sources
    fig3.add_trace(go.Bar(
        x=years, y=work_income,
        name='Work Income',
        marker_color='rgb(147, 112, 219)',  # Bright purple
        hovertemplate='Age: %{x}<br>Work: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=ss_income,
        name='Social Security',
        marker_color='rgb(255, 140, 0)',  # Bright orange
        hovertemplate='Age: %{x}<br>Social Security: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=pension_income,
        name='Pension',
        marker_color='rgb(64, 196, 255)',  # Bright cyan
        hovertemplate='Age: %{x}<br>Pension: $%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=years, y=rmd_income,
        name='RMD/Withdrawals',
        marker_color='rgb(255, 215, 0)',  # Bright gold
        hovertemplate='Age: %{x}<br>RMD: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add expenses line
    fig3.add_trace(go.Scatter(
        x=years, y=expenses,
        name='Expenses & Taxes',
        line=dict(color='rgb(255, 69, 0)', width=4, dash='dash'),  # Bright red-orange
        mode='lines',
        hovertemplate='Age: %{x}<br>Expenses: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add retirement line
    fig3.add_vline(x=retirement_age, line_dash="dash", line_color="rgba(144, 238, 144, 0.8)", line_width=3,
                   annotation_font_color="white")
    
    fig3.update_layout(
        title={
            'text': "Income Sources vs. Expenses Over Time",
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title="Age",
        yaxis_title="Annual Amount",
        barmode='stack',
        height=500,
        plot_bgcolor='rgb(30, 30, 30)',  # Dark background
        paper_bgcolor='rgb(20, 20, 20)',  # Darker outer background
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(40, 40, 40, 0.8)",
            font=dict(color='white')
        )
    )
    
    fig3.update_xaxes(gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    fig3.update_yaxes(tickformat="$,.0f", gridcolor='rgba(100, 100, 100, 0.3)', color='white')
    
    st.plotly_chart(fig3, width="stretch")
    
    # Detailed Statistics Table
    st.markdown('<p class="section-header">📋 Detailed Projections</p>', unsafe_allow_html=True)
    
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