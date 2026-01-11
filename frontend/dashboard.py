import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def show_dashboard(db):
    st.title("📊 Dashboard Overview")
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cars = len(db.cars)
        st.metric("Total Cars", total_cars)
    
    with col2:
        active_leases = len(db.contracts[db.contracts['status'] == 'Active'])
        st.metric("Active Leases", active_leases)
    
    with col3:
        monthly_revenue = db.contracts['monthly_payment'].sum() if not db.contracts.empty else 0
        st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}")
    
    with col4:
        avg_monthly = db.contracts['monthly_payment'].mean() if not db.contracts.empty else 0
        st.metric("Avg. Monthly", f"${avg_monthly:,.0f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Car types distribution
        type_counts = db.cars['type'].value_counts()
        fig1 = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Car Types Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Monthly payments by brand
        if not db.contracts.empty:
            fig2 = px.bar(
                db.contracts,
                x='monthly_payment',
                y='customer_name',
                orientation='h',
                title="Monthly Payments by Customer",
                color='monthly_payment',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No lease contracts yet")
    
    # Recent Contracts
    st.subheader("📝 Recent Contracts")
    if not db.contracts.empty:
        recent_contracts = db.contracts.sort_values('created_at', ascending=False).head(5)
        st.dataframe(
            recent_contracts[['id', 'customer_name', 'monthly_payment', 'status', 'start_date']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No contracts created yet")