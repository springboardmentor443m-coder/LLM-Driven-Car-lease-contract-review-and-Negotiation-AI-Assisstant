import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def sla_analysis_section():
    st.title("🔍 Contract Terms Analysis")
    
    if not st.session_state.get('current_contract'):
        st.warning("No contract loaded. Please upload a contract first.")
        if st.button("Go to Upload Page"):
            st.rerun()
        return
    
    contract = st.session_state.current_contract
    sla_data = contract.get('sla_data', {})
    
    # Show contract info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Contract", contract.get('filename', 'Unknown'))
    with col2:
        st.metric("Upload Date", contract.get('upload_date').strftime('%Y-%m-%d'))
    with col3:
        score = contract.get('fairness_score', 0)
        color = get_score_color(score)
        st.markdown(f"**Fairness Score:** <span style='color:{color}; font-size:24px'>{score}/100</span>", 
                   unsafe_allow_html=True)
    
    st.divider()
    
    # Main analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Key Terms", "🚩 Red Flags", "💰 Payment Analysis", "📈 Market Comparison"])
    
    with tab1:
        display_key_terms(sla_data)
    
    with tab2:
        display_red_flags(sla_data)
    
    with tab3:
        display_payment_analysis(sla_data)
    
    with tab4:
        display_market_comparison(sla_data)

def display_key_terms(sla_data):
    """Display key contract terms"""
    st.subheader("📊 Key Contract Terms")
    
    if not sla_data:
        st.info("No SLA data extracted yet. Would you like to extract terms?")
        if st.button("Extract Terms"):
            extract_terms()
        return
    
    # Create columns for terms display
    col1, col2 = st.columns(2)
    
    # Financial terms
    with col1:
        st.markdown("### 💰 Financial Terms")
        
        terms_grid = st.columns(2)
        
        with terms_grid[0]:
            if 'interest_rate' in sla_data:
                apr = float(sla_data['interest_rate'])
                color = "green" if apr < 5 else "orange" if apr < 8 else "red"
                st.metric("APR", f"{apr}%")
        
        with terms_grid[1]:
            if 'monthly_payment_amount' in sla_data:
                payment = float(sla_data['monthly_payment_amount'])
                st.metric("Monthly Payment", f"${payment:,.2f}")
        
        if 'lease_term_months' in sla_data:
            st.metric("Lease Term", f"{sla_data['lease_term_months']} months")
        
        if 'down_payment_amount' in sla_data:
            st.metric("Down Payment", f"${float(sla_data['down_payment_amount']):,.2f}")
    
    with col2:
        st.markdown("### 📝 Contract Details")
        
        if 'mileage_allowance_per_year' in sla_data:
            mileage = int(sla_data['mileage_allowance_per_year'])
            st.metric("Annual Mileage", f"{mileage:,} miles")
        
        if 'mileage_overage_charge_per_mile' in sla_data:
            charge = float(sla_data['mileage_overage_charge_per_mile'])
            st.metric("Overage Charge", f"${charge:.2f}/mile")
        
        if 'residual_value' in sla_data:
            residual = float(sla_data['residual_value'])
            st.metric("Residual Value", f"${residual:,.2f}")
        
        if 'purchase_option_price' in sla_data:
            buyout = float(sla_data['purchase_option_price'])
            st.metric("Buyout Price", f"${buyout:,.2f}")
    
    # Additional terms expander
    with st.expander("📋 Additional Terms"):
        additional_terms = [
            ('Early Termination', 'early_termination_conditions'),
            ('Maintenance', 'maintenance_responsibilities'),
            ('Warranty', 'warranty_coverage'),
            ('Insurance', 'insurance_requirements'),
            ('Late Fees', 'late_fee_amount'),
            ('Penalties', 'penalty_clauses')
        ]
        
        for label, key in additional_terms:
            if key in sla_data and sla_data[key]:
                st.markdown(f"**{label}:**")
                st.write(sla_data[key])
                st.divider()

def display_red_flags(sla_data):
    """Display red flags in contract"""
    st.subheader("🚩 Potential Red Flags")
    
    red_flags = identify_red_flags(sla_data)
    
    if not red_flags:
        st.success("✅ No major red flags detected!")
    else:
        st.warning(f"⚠️ Found {len(red_flags)} potential issue(s)")
        
        for i, flag in enumerate(red_flags, 1):
            st.markdown(f"{i}. **{flag}**")
        
        st.info("💡 Consider negotiating these points with the dealer")

def display_payment_analysis(sla_data):
    """Display payment analysis"""
    st.subheader("💰 Payment Analysis")
    
    if 'monthly_payment_amount' not in sla_data or 'lease_term_months' not in sla_data:
        st.info("Payment data not available for analysis")
        return
    
    monthly_payment = float(sla_data['monthly_payment_amount'])
    term_months = int(sla_data['lease_term_months'])
    
    # Create payment schedule
    months = list(range(1, term_months + 1))
    payments = [monthly_payment] * term_months
    
    # Create dataframe
    df = pd.DataFrame({
        'Month': months,
        'Payment': payments,
        'Cumulative': [monthly_payment * i for i in range(1, term_months + 1)]
    })
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Payments", f"${monthly_payment * term_months:,.2f}")
    with col2:
        down_payment = float(sla_data.get('down_payment_amount', 0))
        st.metric("Down Payment", f"${down_payment:,.2f}")
    with col3:
        total_cost = (monthly_payment * term_months) + down_payment
        st.metric("Total Cost", f"${total_cost:,.2f}")
    
    # Payment chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative'],
                           mode='lines+markers',
                           name='Cumulative Payments',
                           line=dict(color='blue', width=3)))
    fig.add_trace(go.Bar(x=df['Month'], y=df['Payment'],
                        name='Monthly Payment',
                        marker_color='lightblue'))
    
    fig.update_layout(
        title='Payment Schedule',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_market_comparison(sla_data):
    """Display market comparison"""
    st.subheader("📈 Market Comparison")
    
    if 'interest_rate' not in sla_data:
        st.info("Market comparison requires interest rate data")
        return
    
    current_apr = float(sla_data['interest_rate'])
    
    # Market benchmarks (example data)
    market_data = {
        'Credit Union': 3.5,
        'Manufacturer Financing': 4.2,
        'Bank Average': 5.8,
        'Your Rate': current_apr
    }
    
    # Create comparison chart
    fig = go.Figure()
    
    for source, rate in market_data.items():
        color = 'green' if rate < 5 else 'orange' if rate < 7 else 'red'
        fig.add_trace(go.Bar(
            x=[source],
            y=[rate],
            name=source,
            marker_color=color,
            text=f"{rate}%",
            textposition='auto'
        ))
    
    fig.update_layout(
        title='APR Comparison with Market Rates',
        yaxis_title='APR (%)',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if current_apr > 6:
        st.warning("Your APR is above market average. Consider:")
        st.markdown("- Shop around with credit unions")
        st.markdown("- Ask about manufacturer incentives")
        st.markdown("- Improve credit score for better rates")
    else:
        st.success("Your APR is competitive with market rates!")

def get_score_color(score):
    """Get color based on fairness score"""
    if score >= 80:
        return "#00cc00"  # Green
    elif score >= 60:
        return "#ff9900"  # Orange
    else:
        return "#ff0000"  # Red

def extract_terms():
    """Extract terms from current contract"""
    contract = st.session_state.current_contract
    if contract and 'text' in contract:
        # Call extraction function
        sla_data = extract_sla_from_text(contract['text'])
        if sla_data:
            st.session_state.current_contract['sla_data'] = sla_data
            st.rerun()

def extract_sla_from_text(text):
    """Placeholder for SLA extraction"""
    # In production, this would call the API
    return {
        'interest_rate': '5.5',
        'monthly_payment_amount': '450',
        'lease_term_months': '36',
        'down_payment_amount': '2500',
        'mileage_allowance_per_year': '12000',
        'mileage_overage_charge_per_mile': '0.25'
    }

def identify_red_flags(sla_data):
    """Identify red flags in contract terms"""
    red_flags = []
    
    try:
        if sla_data.get('interest_rate'):
            apr = float(sla_data['interest_rate'])
            if apr > 10:
                red_flags.append(f"High interest rate ({apr}% > 10%)")
        
        if sla_data.get('mileage_overage_charge_per_mile'):
            charge = float(sla_data['mileage_overage_charge_per_mile'])
            if charge > 0.30:
                red_flags.append(f"High mileage overage charge (${charge}/mile > $0.30/mile)")
        
        if sla_data.get('mileage_allowance_per_year'):
            mileage = int(sla_data['mileage_allowance_per_year'])
            if mileage < 10000:
                red_flags.append(f"Low annual mileage allowance ({mileage} < 10,000 miles)")
        
        termination_clause = str(sla_data.get('early_termination_conditions', '')).lower()
        if 'non-refundable' in termination_clause:
            red_flags.append("Non-refundable early termination fee")
        
        if 'balloon' in termination_clause:
            red_flags.append("Balloon payment required")
            
    except Exception as e:
        st.error(f"Error analyzing red flags: {e}")
    
    return red_flags