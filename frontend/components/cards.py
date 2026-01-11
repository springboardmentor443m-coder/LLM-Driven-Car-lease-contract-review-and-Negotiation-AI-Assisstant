import streamlit as st

def car_card(car):
    """Display a car card with details"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {car['brand']} {car['model']}")
        st.markdown(f"**Year:** {car['year']} | **Type:** {car['type']} | **Fuel:** {car['fuel']}")
        st.markdown(f"**Price:** ${car['price']:,} | **Monthly:** ${car['monthly']}")
    
    with col2:
        if st.button("🔄 Lease", key=f"lease_{car['id']}", use_container_width=True):
            st.session_state.selected_car = car
            st.rerun()
    
    st.markdown("---")

def contract_card(contract):
    """Display a contract card"""
    with st.container():
        st.markdown(f"### 📄 Contract #{contract['id']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Customer:** {contract['customer_name']}")
            st.markdown(f"**Status:** {contract['status']}")
        with col2:
            st.markdown(f"**Monthly:** ${contract['monthly_payment']}")
            st.markdown(f"**Start:** {contract['start_date']}")
        with col3:
            st.markdown(f"**End:** {contract['end_date']}")
            
            status_color = {
                'Active': 'green',
                'Pending': 'orange',
                'Completed': 'blue',
                'Cancelled': 'red'
            }.get(contract['status'], 'gray')
            
            st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{contract['status']}</span>", 
                       unsafe_allow_html=True)
        
        st.markdown("---")