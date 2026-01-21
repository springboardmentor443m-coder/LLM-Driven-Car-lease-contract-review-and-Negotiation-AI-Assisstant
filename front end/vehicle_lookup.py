import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Fix imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from utils import APIClient
except ImportError:
    # Create a mock APIClient for development
    class APIClient:
        def __init__(self):
            pass
        
        def get_nhtsa_data(self, vin):
            return {
                'vin': vin,
                'make': 'Toyota',
                'model': 'Camry',
                'year': '2023',
                'body_style': 'Sedan'
            }
        
        def get_pricing_data(self, make, model, year):
            return {
                'edmunds': 28000,
                'kbb': 27500,
                'truecar': 28500,
                'average_price': 28000
            }

# [Rest of the vehicle_lookup.py code...]

def vehicle_lookup_section():
    st.title("🚗 Vehicle Information Lookup")
    
    # Initialize API client
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    
    api_client = st.session_state.api_client
    
    # Lookup methods
    tab1, tab2 = st.tabs(["VIN Lookup", "Manual Entry"])
    
    with tab1:
        vin_lookup_tab(api_client)
    
    with tab2:
        manual_entry_tab(api_client)

def vin_lookup_tab(api_client):
    """VIN lookup interface"""
    st.subheader("VIN (Vehicle Identification Number) Lookup")
    
    vin = st.text_input(
        "Enter 17-character VIN",
        placeholder="1HGCM82633A123456",
        max_chars=17,
        help="The VIN is usually found on the dashboard or driver's side door"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 Lookup Vehicle", use_container_width=True) and vin:
            lookup_vehicle_by_vin(vin, api_client)
    
    with col2:
        if st.button("Scan Barcode", use_container_width=True):
            st.info("Barcode scanning not available in web version")

def manual_entry_tab(api_client):
    """Manual vehicle entry interface"""
    st.subheader("Manual Vehicle Entry")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        make = st.text_input("Make", placeholder="Toyota")
    
    with col2:
        model = st.text_input("Model", placeholder="Camry")
    
    with col3:
        year = st.number_input("Year", min_value=1990, max_value=2024, value=2023)
    
    if st.button("Get Vehicle Data", use_container_width=True) and make and model:
        lookup_vehicle_by_details(make, model, year, api_client)

def lookup_vehicle_by_vin(vin, api_client):
    """Lookup vehicle by VIN"""
    with st.spinner("Fetching vehicle information..."):
        try:
            # Get NHTSA data
            nhtsa_data = api_client.get_nhtsa_data(vin)
            
            if nhtsa_data:
                display_vehicle_data(nhtsa_data, api_client)
            else:
                st.error("Vehicle not found. Please check the VIN.")
                
        except Exception as e:
            st.error(f"Error fetching vehicle data: {e}")

def lookup_vehicle_by_details(make, model, year, api_client):
    """Lookup vehicle by make/model/year"""
    with st.spinner("Fetching vehicle information..."):
        try:
            # Get pricing data
            pricing_data = api_client.get_pricing_data(make, model, year)
            
            # Get recall data
            recall_data = api_client.get_recall_data(make, model, year)
            
            # Get safety ratings
            safety_data = api_client.get_safety_ratings(make, model, year)
            
            # Display data
            display_manual_vehicle_data(make, model, year, pricing_data, recall_data, safety_data)
            
        except Exception as e:
            st.error(f"Error fetching vehicle data: {e}")

def display_vehicle_data(vehicle_data, api_client):
    """Display vehicle information"""
    st.success("✅ Vehicle found!")
    
    # Basic info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Make", vehicle_data.get('make', 'N/A'))
    
    with col2:
        st.metric("Model", vehicle_data.get('model', 'N/A'))
    
    with col3:
        st.metric("Year", vehicle_data.get('year', 'N/A'))
    
    with col4:
        st.metric("Body Style", vehicle_data.get('body_style', 'N/A'))
    
    st.divider()
    
    # Tabs for different data
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Details", "💰 Pricing", "⚠️ Recalls", "⭐ Safety"])
    
    with tab1:
        display_vehicle_details(vehicle_data)
    
    with tab2:
        display_pricing_data(vehicle_data, api_client)
    
    with tab3:
        display_recall_data(vehicle_data, api_client)
    
    with tab4:
        display_safety_data(vehicle_data, api_client)
    
    # Save to session
    st.session_state.vehicle_data = vehicle_data

def display_vehicle_details(vehicle_data):
    """Display vehicle details"""
    st.subheader("Vehicle Specifications")
    
    details = {
        "VIN": vehicle_data.get('vin'),
        "Engine": vehicle_data.get('engine'),
        "Fuel Type": vehicle_data.get('fuel_type'),
        "Transmission": vehicle_data.get('transmission'),
        "Drive Type": vehicle_data.get('drive_type'),
        "Doors": vehicle_data.get('doors'),
        "Seats": vehicle_data.get('seats'),
        "Country of Origin": vehicle_data.get('country'),
        "Plant City": vehicle_data.get('plant_city')
    }
    
    for key, value in details.items():
        if value:
            st.write(f"**{key}:** {value}")

def display_pricing_data(vehicle_data, api_client):
    """Display pricing information"""
    st.subheader("💰 Market Pricing")
    
    make = vehicle_data.get('make')
    model = vehicle_data.get('model')
    year = vehicle_data.get('year')
    
    if make and model and year:
        # For demo purposes, create sample data
        sample_prices = {
            'Edmunds': 28000,
            'KBB': 27500,
            'TrueCar': 28500
        }
        
        prices = list(sample_prices.values())
        sources = list(sample_prices.keys())
        
        # Create bar chart
        fig = px.bar(
            x=sources,
            y=prices,
            title=f"{year} {make} {model} - Price Comparison",
            labels={'x': 'Source', 'y': 'Price ($)'},
            text=[f"${p:,.0f}" for p in prices],
            color=prices,
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Show average
        avg_price = sum(prices) / len(prices)
        st.metric("Average Market Price", f"${avg_price:,.0f}")
    else:
        st.info("Incomplete vehicle information for pricing lookup")

def display_recall_data(vehicle_data, api_client):
    """Display recall information"""
    st.subheader("⚠️ Recall Information")
    
    make = vehicle_data.get('make')
    model = vehicle_data.get('model')
    year = vehicle_data.get('year')
    
    if make and model and year:
        # Sample recall data for demo
        sample_recalls = [
            {
                'component': 'Airbag',
                'summary': 'Airbag may not deploy properly',
                'date': '2023-05-15'
            },
            {
                'component': 'Brake System',
                'summary': 'Potential brake fluid leak',
                'date': '2022-11-30'
            }
        ]
        
        if sample_recalls:
            st.warning(f"Found {len(sample_recalls)} recall(s)")
            
            for i, recall in enumerate(sample_recalls, 1):
                with st.expander(f"Recall #{i}: {recall.get('component', 'Unknown')}"):
                    st.write(f"**Date:** {recall.get('date', 'N/A')}")
                    st.write(f"**Summary:** {recall.get('summary', 'N/A')}")
        else:
            st.success("✅ No recalls found for this vehicle")
    else:
        st.warning("Incomplete vehicle information for recall check")

def display_safety_data(vehicle_data, api_client):
    """Display safety ratings"""
    st.subheader("⭐ Safety Ratings")
    
    make = vehicle_data.get('make')
    model = vehicle_data.get('model')
    year = vehicle_data.get('year')
    
    if make and model and year:
        # Sample safety data for demo
        safety_ratings = [
            {'Category': 'Overall', 'Rating': '5 Stars'},
            {'Category': 'Frontal Crash', 'Rating': '5 Stars'},
            {'Category': 'Side Crash', 'Rating': '4 Stars'},
            {'Category': 'Rollover', 'Rating': '4 Stars'}
        ]
        
        if safety_ratings:
            # Display safety ratings
            for rating in safety_ratings:
                st.write(f"**{rating.get('Category', 'Rating')}:** {rating.get('Rating', 'N/A')}")
        else:
            st.info("Safety ratings not available for this vehicle")
    else:
        st.warning("Incomplete vehicle information for safety ratings")

def display_manual_vehicle_data(make, model, year, pricing_data, recall_data, safety_data):
    """Display manually entered vehicle data"""
    st.success(f"✅ Data retrieved for {year} {make} {model}")
    
    # Pricing data
    if pricing_data:
        st.subheader("💰 Pricing Information")
        
        # Convert pricing data to DataFrame
        price_items = []
        for source, price in pricing_data.items():
            if isinstance(price, (int, float)) and price > 0:
                price_items.append({'Source': source, 'Price': price})
        
        if price_items:
            price_df = pd.DataFrame(price_items)
            fig = px.bar(price_df, x='Source', y='Price', 
                        title=f"{year} {make} {model} - Market Prices")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recall data
    if recall_data:
        st.subheader("⚠️ Recall Information")
        st.write(f"Found {len(recall_data)} recall(s)")
        
        for recall in recall_data[:3]:  # Show first 3 recalls
            if isinstance(recall, dict):
                st.write(f"- {recall.get('Component', 'Unknown component')}")
    
    # Safety data
    if safety_data:
        st.subheader("⭐ Safety Ratings")
        
        # Display as metrics
        col1, col2, col3 = st.columns(3)
        
        # Example metrics
        with col1:
            st.metric("Overall Rating", "5 Stars" if len(safety_data) > 0 else "N/A")
        
        with col2:
            st.metric("Front Crash", "Good" if len(safety_data) > 1 else "N/A")
        
        with col3:
            st.metric("Side Crash", "Good" if len(safety_data) > 2 else "N/A")
    
    # Store in session
    st.session_state.vehicle_data = {
        'make': make,
        'model': model,
        'year': year,
        'pricing': pricing_data,
        'recalls': recall_data,
        'safety': safety_data
    }