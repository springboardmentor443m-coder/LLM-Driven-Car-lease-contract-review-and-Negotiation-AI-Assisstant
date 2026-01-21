import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def price_comparison_section():
    st.title("📊 Compare Multiple Offers")
    
    # Check if we have contracts to compare
    contracts = st.session_state.get('contracts', [])
    
    if len(contracts) < 2:
        st.warning("You need at least 2 contracts to compare.")
        st.info("Upload more contracts using the Upload page.")
        return
    
    st.subheader(f"Comparing {len(contracts)} Contract(s)")
    
    # Contract selection
    st.markdown("### Select Contracts to Compare")
    
    selected_contracts = []
    
    for i, contract in enumerate(contracts):
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            select = st.checkbox("", key=f"select_{i}", value=i < 3)  # Select first 3 by default
        
        with col2:
            filename = contract.get('filename', f'Contract {i+1}')
            score = contract.get('fairness_score', 0)
            color = get_score_color(score)
            
            st.markdown(f"**{filename}**")
            st.markdown(f"Score: <span style='color:{color}'>{score}/100</span>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("View", key=f"view_{i}"):
                st.session_state.current_contract = contract
                st.rerun()  # Changed from st.switch_page
        
        if select:
            selected_contracts.append(contract)
    
    if len(selected_contracts) < 2:
        st.warning("Please select at least 2 contracts to compare")
        return
    
    st.divider()
    
    # Comparison tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Side-by-Side", "💰 Financial Comparison", "📊 Visual Analysis", "🏆 Best Deal"])
    
    with tab1:
        side_by_side_comparison(selected_contracts)
    
    with tab2:
        financial_comparison(selected_contracts)
    
    with tab3:
        visual_analysis(selected_contracts)
    
    with tab4:
        best_deal_recommendation(selected_contracts)

def side_by_side_comparison(contracts):
    """Display side-by-side comparison table"""
    st.subheader("📈 Contract Terms Comparison")
    
    # Extract key terms from each contract
    comparison_data = []
    
    for contract in contracts:
        sla_data = contract.get('sla_data', {})
        comparison_data.append({
            'Contract': contract.get('filename', 'Unknown'),
            'Fairness Score': contract.get('fairness_score', 0),
            'APR (%)': sla_data.get('interest_rate', 'N/A'),
            'Monthly Payment ($)': format_currency(sla_data.get('monthly_payment_amount')),
            'Term (months)': sla_data.get('lease_term_months', 'N/A'),
            'Down Payment ($)': format_currency(sla_data.get('down_payment_amount')),
            'Mileage/Year': format_mileage(sla_data.get('mileage_allowance_per_year')),
            'Overage Charge ($/mile)': format_currency(sla_data.get('mileage_overage_charge_per_mile')),
            'Residual Value ($)': format_currency(sla_data.get('residual_value')),
            'Buyout Price ($)': format_currency(sla_data.get('purchase_option_price'))
        })
    
    # Create DataFrame
    df = pd.DataFrame(comparison_data)
    
    # Display as table with formatting
    st.dataframe(
        df,
        use_container_width=True
    )
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Comparison CSV",
        data=csv,
        file_name=f"contract_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def financial_comparison(contracts):
    """Financial comparison analysis"""
    st.subheader("💰 Financial Analysis")
    
    # Calculate total costs
    financial_data = []
    
    for contract in contracts:
        sla_data = contract.get('sla_data', {})
        
        try:
            monthly = float(sla_data.get('monthly_payment_amount', 0))
            term = int(sla_data.get('lease_term_months', 36))
            down = float(sla_data.get('down_payment_amount', 0))
            
            total_cost = (monthly * term) + down
            
            financial_data.append({
                'Contract': contract.get('filename', 'Unknown'),
                'Monthly Payment': monthly,
                'Down Payment': down,
                'Term': term,
                'Total Cost': total_cost,
                'Cost per Month': total_cost / term if term > 0 else 0
            })
        except:
            continue
    
    if not financial_data:
        st.warning("Insufficient financial data for comparison")
        return
    
    df = pd.DataFrame(financial_data)
    
    # Create comparison chart
    fig = go.Figure()
    
    # Add bars for total cost
    fig.add_trace(go.Bar(
        x=df['Contract'],
        y=df['Total Cost'],
        name='Total Cost',
        text=[f"${x:,.0f}" for x in df['Total Cost']],
        textposition='auto',
        marker_color='lightblue'
    ))
    
    # Add bars for down payment
    fig.add_trace(go.Bar(
        x=df['Contract'],
        y=df['Down Payment'],
        name='Down Payment',
        text=[f"${x:,.0f}" for x in df['Down Payment']],
        textposition='auto',
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title='Total Cost Comparison',
        barmode='stack',
        yaxis_title='Amount ($)',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed financial breakdown
    st.subheader("📋 Financial Breakdown")
    
    for data in financial_data:
        with st.expander(f"💰 {data['Contract']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Monthly", f"${data['Monthly Payment']:,.2f}")
            
            with col2:
                st.metric("Down", f"${data['Down Payment']:,.2f}")
            
            with col3:
                st.metric("Term", f"{data['Term']} months")
            
            with col4:
                st.metric("Total", f"${data['Total Cost']:,.2f}")
            
            st.progress(min(data['Total Cost'] / max(df['Total Cost']), 1.0))

def visual_analysis(contracts):
    """Visual analysis with charts"""
    st.subheader("📊 Visual Comparison")
    
    # Prepare data for radar chart
    categories = ['APR', 'Monthly Cost', 'Mileage', 'Overage', 'Term Flexibility']
    
    fig = go.Figure()
    
    for contract in contracts:
        sla_data = contract.get('sla_data', {})
        filename = contract.get('filename', 'Unknown')
        
        # Normalize values (0-1 scale, where 1 is best)
        try:
            # APR (lower is better)
            apr = float(sla_data.get('interest_rate', 10))
            apr_score = max(0, 1 - (apr / 15))  # 0% APR = 1, 15% APR = 0
            
            # Monthly payment (lower is better, relative)
            monthly = float(sla_data.get('monthly_payment_amount', 1000))
            monthly_score = max(0, 1 - (monthly / 2000))
            
            # Mileage (higher is better)
            mileage = int(sla_data.get('mileage_allowance_per_year', 10000))
            mileage_score = min(1, mileage / 20000)
            
            # Overage charge (lower is better)
            overage = float(sla_data.get('mileage_overage_charge_per_mile', 0.25))
            overage_score = max(0, 1 - (overage / 0.5))
            
            # Term (mid-range is best)
            term = int(sla_data.get('lease_term_months', 36))
            term_score = 1 - abs(term - 36) / 48  # 36 months is ideal
            
            values = [apr_score, monthly_score, mileage_score, overage_score, term_score]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=filename
            ))
        except:
            continue
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title="Contract Comparison Radar Chart",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar chart comparison
    st.subheader("📊 Key Metrics Comparison")
    
    metrics_data = []
    for contract in contracts:
        sla_data = contract.get('sla_data', {})
        metrics_data.append({
            'Contract': contract.get('filename', 'Unknown'),
            'APR': float(sla_data.get('interest_rate', 0)),
            'Monthly': float(sla_data.get('monthly_payment_amount', 0)),
            'Mileage': int(sla_data.get('mileage_allowance_per_year', 0)),
            'Score': contract.get('fairness_score', 0)
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Create grouped bar chart
    fig = px.bar(df_metrics, 
                x='Contract', 
                y=['APR', 'Monthly', 'Score'],
                barmode='group',
                title="Key Metrics Comparison")
    
    fig.update_layout(yaxis_title="Value")
    st.plotly_chart(fig, use_container_width=True)

def best_deal_recommendation(contracts):
    """Recommend the best deal"""
    st.subheader("🏆 Best Deal Recommendation")
    
    if not contracts:
        st.warning("No contracts to analyze")
        return
    
    # Find best contract based on multiple factors
    best_contract = None
    best_score = -1
    
    for contract in contracts:
        score = calculate_comprehensive_score(contract)
        if score > best_score:
            best_score = score
            best_contract = contract
    
    if best_contract:
        st.success(f"🎉 **Best Deal:** {best_contract.get('filename', 'Unknown')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fairness Score", f"{best_contract.get('fairness_score', 0):.1f}/100")
        
        with col2:
            sla_data = best_contract.get('sla_data', {})
            apr = sla_data.get('interest_rate', 'N/A')
            st.metric("APR", f"{apr}%" if apr != 'N/A' else "N/A")
        
        with col3:
            monthly = sla_data.get('monthly_payment_amount', 'N/A')
            st.metric("Monthly", f"${monthly}" if monthly != 'N/A' else "N/A")
        
        # Why it's the best
        st.subheader("✅ Why this is the best deal:")
        
        reasons = []
        
        # Compare with others
        for contract in contracts:
            if contract != best_contract:
                sla_best = best_contract.get('sla_data', {})
                sla_other = contract.get('sla_data', {})
                
                # APR comparison
                if sla_best.get('interest_rate') and sla_other.get('interest_rate'):
                    apr_best = float(sla_best['interest_rate'])
                    apr_other = float(sla_other['interest_rate'])
                    if apr_best < apr_other:
                        reasons.append(f"Lower APR ({apr_best}% vs {apr_other}%)")
                
                # Monthly payment comparison
                if sla_best.get('monthly_payment_amount') and sla_other.get('monthly_payment_amount'):
                    monthly_best = float(sla_best['monthly_payment_amount'])
                    monthly_other = float(sla_other['monthly_payment_amount'])
                    if monthly_best < monthly_other:
                        reasons.append(f"Lower monthly payment (${monthly_best} vs ${monthly_other})")
        
        # Add unique reasons
        if best_contract.get('fairness_score', 0) > 80:
            reasons.append("Highest overall fairness score")
        
        if sla_best.get('mileage_allowance_per_year'):
            mileage = int(sla_best['mileage_allowance_per_year'])
            if mileage >= 12000:
                reasons.append(f"Good mileage allowance ({mileage} miles/year)")
        
        # Display reasons
        for reason in set(reasons[:5]):  # Show up to 5 unique reasons
            st.write(f"• {reason}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Select This Contract", use_container_width=True):
                st.session_state.current_contract = best_contract
                st.success("Contract selected! Go to Analysis page for details.")
        
        with col2:
            if st.button("💬 Get Negotiation Tips", use_container_width=True):
                st.rerun()
    
    else:
        st.warning("Unable to determine best deal")

def calculate_comprehensive_score(contract):
    """Calculate comprehensive score for contract comparison"""
    score = contract.get('fairness_score', 0)
    sla_data = contract.get('sla_data', {})
    
    # Adjust based on key factors
    try:
        # Lower APR is better
        if 'interest_rate' in sla_data:
            apr = float(sla_data['interest_rate'])
            if apr < 4:
                score += 20
            elif apr < 6:
                score += 10
            elif apr > 10:
                score -= 20
        
        # Reasonable monthly payment
        if 'monthly_payment_amount' in sla_data:
            monthly = float(sla_data['monthly_payment_amount'])
            if monthly < 300:
                score += 10
            elif monthly > 800:
                score -= 10
        
        # Good mileage allowance
        if 'mileage_allowance_per_year' in sla_data:
            mileage = int(sla_data['mileage_allowance_per_year'])
            if mileage >= 12000:
                score += 5
        
    except:
        pass
    
    return score

def format_currency(value):
    """Format currency values"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"${float(value):,.2f}"
    except:
        return str(value)

def format_mileage(value):
    """Format mileage values"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{int(value):,}"
    except:
        return str(value)

def get_score_color(score):
    """Get color based on score"""
    if score >= 80:
        return "#00cc00"
    elif score >= 60:
        return "#ff9900"
    else:
        return "#ff0000"