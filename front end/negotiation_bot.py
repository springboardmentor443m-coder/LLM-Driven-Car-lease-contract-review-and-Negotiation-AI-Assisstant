import streamlit as st
import json
from datetime import datetime

def negotiation_assistant_section():
    st.title("💬 Negotiation Assistant")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm your car negotiation assistant. I can help you understand your contract terms and suggest negotiation strategies. How can I help you today?"}
        ]
    
    # Check if we have contract data
    has_contract = st.session_state.get('current_contract') is not None
    has_vehicle = st.session_state.get('vehicle_data') is not None
    
    # Show status
    col1, col2 = st.columns(2)
    with col1:
        status = "✅" if has_contract else "❌"
        st.write(f"{status} Contract Loaded")
    with col2:
        status = "✅" if has_vehicle else "❌"
        st.write(f"{status} Vehicle Data")
    
    st.divider()
    
    # Quick suggestions
    st.subheader("💡 Quick Suggestions")
    
    suggestion_cols = st.columns(3)
    
    with suggestion_cols[0]:
        if st.button("Analyze APR", use_container_width=True):
            analyze_apr()
    
    with suggestion_cols[1]:
        if st.button("Check Mileage Terms", use_container_width=True):
            analyze_mileage()
    
    with suggestion_cols[2]:
        if st.button("Review Fees", use_container_width=True):
            analyze_fees()
    
    st.divider()
    
    # Chat interface
    st.subheader("Chat with Assistant")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about negotiation strategies..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_negotiation_response(prompt)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    st.divider()
    
    # Negotiation tools
    st.subheader("🛠️ Negotiation Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate Email Template", use_container_width=True):
            generate_email_template()
    
    with col2:
        if st.button("Counter-Offer Calculator", use_container_width=True):
            show_counter_offer_calculator()
    
    with col3:
        if st.button("Dealer Questions", use_container_width=True):
            show_dealer_questions()

def get_negotiation_response(prompt):
    """Generate negotiation response based on context"""
    # Get context from session
    contract = st.session_state.get('current_contract', {})
    vehicle = st.session_state.get('vehicle_data', {})
    sla_data = contract.get('sla_data', {})
    
    # Simple rule-based responses (in production, use LLM)
    prompt_lower = prompt.lower()
    
    if "apr" in prompt_lower or "interest" in prompt_lower:
        return generate_apr_advice(sla_data)
    
    elif "mileage" in prompt_lower:
        return generate_mileage_advice(sla_data)
    
    elif "fee" in prompt_lower or "charge" in prompt_lower:
        return generate_fee_advice(sla_data)
    
    elif "monthly" in prompt_lower or "payment" in prompt_lower:
        return generate_payment_advice(sla_data, vehicle)
    
    elif "terminat" in prompt_lower or "end" in prompt_lower:
        return generate_termination_advice(sla_data)
    
    elif "warranty" in prompt_lower:
        return generate_warranty_advice(sla_data)
    
    else:
        return get_general_advice(prompt, sla_data, vehicle)

def generate_apr_advice(sla_data):
    """Generate advice about APR"""
    if 'interest_rate' in sla_data:
        apr = float(sla_data['interest_rate'])
        
        if apr > 8:
            return f"""Your APR of {apr}% is higher than the current market average (4-6%). Here's what you can do:

**Negotiation Strategy:**
1. **Ask for justification:** "Can you explain how this APR was calculated?"
2. **Shop around:** Get quotes from credit unions (typically 3-5%)
3. **Manufacturer deals:** Ask about any special financing offers
4. **Credit check:** Ensure your credit score is accurately reflected

**What to say:**
"I've seen credit union rates around 4%. Can you match or beat that rate?"

**Target:** Aim for 5-6% or lower if you have good credit."""
        
        elif apr > 5:
            return f"""Your APR of {apr}% is within the fair range. You might still negotiate:

**Suggestions:**
1. **Ask for 0.5-1% reduction:** "Is there any flexibility on the rate?"
2. **Bundle with other services:** Sometimes better rates come with extended warranties
3. **Check for promotions:** Manufacturers often have seasonal rates

**Target:** Try to get down to 4.5-5%"""
        
        else:
            return f"""Your APR of {apr}% is excellent! This is a competitive rate.

**What to do:**
1. **Lock it in:** This is a good deal
2. **Focus on other terms:** Negotiate fees, mileage, or warranty instead
3. **Get it in writing:** Ensure the rate is guaranteed"""
    
    return "I don't see APR information in your contract. Please upload your contract for specific advice."

def generate_mileage_advice(sla_data):
    """Generate advice about mileage terms"""
    advice = "**Mileage Terms Analysis:**\n\n"
    
    if 'mileage_allowance_per_year' in sla_data:
        mileage = int(sla_data['mileage_allowance_per_year'])
        
        if mileage < 10000:
            advice += f"⚠️ **Low allowance:** {mileage:,} miles/year is below standard (12,000).\n"
            advice += "**Negotiate:** Ask for 12,000 miles/year standard allowance\n"
        elif mileage < 12000:
            advice += f"✅ **Standard allowance:** {mileage:,} miles/year\n"
            advice += "**Tip:** This is acceptable for average drivers\n"
        else:
            advice += f"✅ **Good allowance:** {mileage:,} miles/year\n"
            advice += "**Tip:** This should cover most driving needs\n"
    
    if 'mileage_overage_charge_per_mile' in sla_data:
        charge = float(sla_data['mileage_overage_charge_per_mile'])
        
        if charge > 0.25:
            advice += f"\n⚠️ **High overage:** ${charge:.2f}/mile is above average ($0.15-0.20)\n"
            advice += "**Negotiate:** Ask to reduce to $0.20/mile\n"
        else:
            advice += f"\n✅ **Fair overage charge:** ${charge:.2f}/mile\n"
    
    if not ('mileage_allowance_per_year' in sla_data or 'mileage_overage_charge_per_mile' in sla_data):
        advice = "I don't see mileage terms in your contract. Standard is 12,000 miles/year at $0.20/mile overage."
    
    return advice

def generate_fee_advice(sla_data):
    """Generate advice about fees"""
    advice = "**Fee Analysis:**\n\n"
    
    common_fees = {
        'acquisition_fee': ('Acquisition Fee', 500, 'Often negotiable'),
        'disposition_fee': ('Disposition Fee', 400, 'Can sometimes be waived'),
        'documentation_fee': ('Doc Fee', 300, 'State maximums apply'),
        'registration_fee': ('Registration', 200, 'Set by state'),
        'title_fee': ('Title Fee', 100, 'Set by state')
    }
    
    found_fees = False
    
    for fee_key, (fee_name, typical_max, tip) in common_fees.items():
        if fee_key in sla_data:
            found_fees = True
            fee_value = float(sla_data[fee_key])
            
            if fee_value > typical_max:
                advice += f"⚠️ **{fee_name}:** ${fee_value:.0f} (High - typical max: ${typical_max})\n"
                advice += f"   *Negotiation:* {tip}\n\n"
            else:
                advice += f"✅ **{fee_name}:** ${fee_value:.0f} (Reasonable)\n\n"
    
    if not found_fees:
        advice += "No specific fees found in contract.\n\n"
        advice += "**Common negotiable fees to ask about:**\n"
        advice += "1. Acquisition fee ($0-895)\n"
        advice += "2. Documentation fee ($75-500)\n"
        advice += "3. Dealer preparation fee (often can be waived)\n"
        advice += "4. Advertising fee (questionable)\n"
    
    return advice

def generate_payment_advice(sla_data, vehicle_data):
    """Generate advice about payments"""
    if 'monthly_payment_amount' in sla_data:
        payment = float(sla_data['monthly_payment_amount'])
        
        # Get vehicle value for comparison
        vehicle_value = None
        if vehicle_data and 'pricing' in vehicle_data:
            prices = vehicle_data['pricing']
            if isinstance(prices, dict):
                avg_price = prices.get('average_price')
                if avg_price:
                    vehicle_value = avg_price
        
        advice = f"**Monthly Payment:** ${payment:,.2f}\n\n"
        
        if vehicle_value:
            # Calculate if payment is reasonable (approx 1% of vehicle value per month for lease)
            expected_payment = vehicle_value * 0.01
            
            if payment > expected_payment * 1.2:
                advice += f"⚠️ **High payment:** Your payment is {((payment/expected_payment)-1)*100:.0f}% above typical\n"
                advice += f"   *Based on vehicle value of ${vehicle_value:,.0f}, expected: ${expected_payment:,.0f}\n"
                advice += "   **Ask:** 'What components make up this payment amount?'\n"
            elif payment < expected_payment * 0.8:
                advice += f"✅ **Good payment:** Below typical range\n"
            else:
                advice += f"✅ **Fair payment:** Within typical range\n"
        
        advice += "\n**Negotiation tips:**\n"
        advice += "1. Ask for the 'money factor' (lease equivalent of APR)\n"
        advice += "2. Request to see the payment breakdown\n"
        advice += "3. Compare with 0.00125 money factor (approx 3% APR)\n"
        
        return advice
    
    return "Monthly payment information not found. Please upload your contract for specific advice."

def generate_termination_advice(sla_data):
    """Generate advice about termination terms"""
    if 'early_termination_conditions' in sla_data:
        terms = sla_data['early_termination_conditions']
        
        advice = "**Early Termination Analysis:**\n\n"
        advice += f"Terms: {terms}\n\n"
        
        if 'non-refundable' in terms.lower():
            advice += "⚠️ **Red flag:** Non-refundable termination fee\n"
            advice += "   *Negotiate:* Ask for prorated or reduced fee\n"
        
        if 'balloon' in terms.lower():
            advice += "⚠️ **Red flag:** Balloon payment required\n"
            advice += "   *Warning:* This could be expensive at lease end\n"
        
        advice += "\n**What to ask:**\n"
        advice += "1. 'What is the exact early termination formula?'\n"
        advice += "2. 'Is there a way to transfer the lease instead?'\n"
        advice += "3. 'Can termination fees be capped?'\n"
        
        return advice
    
    return "Early termination terms not specified. Standard is typically remaining payments plus fees."

def generate_warranty_advice(sla_data):
    """Generate advice about warranty"""
    if 'warranty_coverage' in sla_data:
        warranty = sla_data['warranty_coverage']
        
        advice = "**Warranty Coverage:**\n\n"
        advice += f"{warranty}\n\n"
        
        if 'manufacturer' in warranty.lower():
            advice += "✅ Standard manufacturer warranty\n"
            advice += "   *Check:* Typically 3 years/36,000 miles\n"
        
        if 'extended' in warranty.lower():
            advice += "⚠️ **Extended warranty included**\n"
            advice += "   *Consider:* This adds cost but may be negotiable\n"
        
        if 'none' in warranty.lower() or 'as is' in warranty.lower():
            advice += "⚠️ **No warranty - high risk**\n"
            advice += "   *Negotiate:* Request at least basic coverage\n"
        
        return advice
    
    return "Warranty terms not specified. Standard is manufacturer's warranty for 3 years/36,000 miles."

def get_general_advice(prompt, sla_data, vehicle_data):
    """Generate general negotiation advice"""
    return f"""I understand you're asking about: "{prompt}"

Based on your contract terms, here are general negotiation principles:

**1. Do Your Research:**
- Know the fair market value of the vehicle
- Understand current interest rates (4-6% is typical)
- Research dealer invoice prices

**2. Negotiation Strategy:**
- Negotiate price first, then financing
- Be prepared to walk away
- Get all quotes in writing

**3. Key Questions to Ask:**
- "What is the money factor?"
- "What fees are negotiable?"
- "Are there any manufacturer incentives?"

**4. Red Flags to Watch For:**
- APR over 8%
- Mileage allowance under 10,000/year
- Non-refundable fees
- Balloon payments

Would you like specific advice on any particular aspect of your contract?"""

def analyze_apr():
    """Quick APR analysis"""
    if 'current_contract' in st.session_state:
        sla_data = st.session_state.current_contract.get('sla_data', {})
        response = generate_apr_advice(sla_data)
        
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response
        })
        st.rerun()
    else:
        st.warning("Please upload a contract first")

def analyze_mileage():
    """Quick mileage analysis"""
    if 'current_contract' in st.session_state:
        sla_data = st.session_state.current_contract.get('sla_data', {})
        response = generate_mileage_advice(sla_data)
        
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response
        })
        st.rerun()
    else:
        st.warning("Please upload a contract first")

def analyze_fees():
    """Quick fee analysis"""
    if 'current_contract' in st.session_state:
        sla_data = st.session_state.current_contract.get('sla_data', {})
        response = generate_fee_advice(sla_data)
        
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response
        })
        st.rerun()
    else:
        st.warning("Please upload a contract first")

def generate_email_template():
    """Generate negotiation email template"""
    template = """
**Negotiation Email Template:**

Subject: Follow-up on [Vehicle Make/Model] - Lease/Loan Terms

Dear [Dealer/Salesperson Name],

Thank you for your time today discussing the [Vehicle Make/Model]. I'm very interested but have a few questions about the terms:

1. **APR/Interest Rate:** The quoted rate of [X]% seems higher than current market rates. Can you explain how this was calculated?

2. **Monthly Payment:** At $[Y]/month, this appears above average for this vehicle. Can you provide a breakdown of this amount?

3. **Fees:** I noticed several fees including [list specific fees]. Are any of these negotiable or can they be reduced?

4. **Mileage:** The [Z] miles/year allowance is below my needs. Can we adjust this to 12,000 miles/year?

I've attached the contract for your reference. I'm ready to move forward if we can address these points.

Please let me know what flexibility you have on these terms.

Best regards,
[Your Name]
[Your Phone Number]
"""
    
    st.subheader("📧 Email Template")
    st.text_area("Copy and customize this template:", template, height=300)
    
    if st.button("Copy to Clipboard"):
        st.info("Template copied! (Manual copy required in Streamlit Cloud)")

def show_counter_offer_calculator():
    """Show counter-offer calculator"""
    st.subheader("🧮 Counter-Offer Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_apr = st.number_input("Current APR (%)", min_value=0.0, max_value=30.0, value=6.5, step=0.1)
        current_payment = st.number_input("Current Monthly Payment ($)", min_value=0, value=450, step=10)
        current_term = st.number_input("Term (months)", min_value=12, max_value=84, value=36, step=12)
    
    with col2:
        target_apr = st.number_input("Target APR (%)", min_value=0.0, max_value=30.0, value=4.5, step=0.1)
        target_payment = st.number_input("Target Payment ($)", min_value=0, value=400, step=10)
        down_payment = st.number_input("Additional Down Payment ($)", min_value=0, value=1000, step=100)
    
    # Calculate savings
    total_current = current_payment * current_term
    total_target = target_payment * current_term + down_payment
    savings = total_current - total_target
    
    st.metric("Total Savings", f"${savings:,.2f}")
    
    if savings > 0:
        st.success(f"You could save ${savings:,.2f} over the term!")
    else:
        st.warning("Your target terms would cost more")

def show_dealer_questions():
    """Show list of questions to ask dealers"""
    st.subheader("❓ Questions to Ask the Dealer")
    
    questions = [
        "What is the money factor? (lease equivalent of APR)",
        "Can you show me the dealer invoice price?",
        "What manufacturer incentives are currently available?",
        "Are all fees itemized and which are negotiable?",
        "What is the residual value and how was it calculated?",
        "Is there a prepayment penalty?",
        "What happens if I exceed the mileage allowance?",
        "Can I transfer the lease to someone else?",
        "What warranty is included and what does it cover?",
        "What maintenance is included?",
        "What is the disposition fee at lease end?",
        "Can I purchase the vehicle at lease end and at what price?",
        "What happens in case of early termination?",
        "Is gap insurance included or required?",
        "What is the acquisition fee and can it be waived?"
    ]
    
    for i, question in enumerate(questions, 1):
        st.write(f"{i}. {question}")
    
    st.info("💡 Tip: Ask for all answers in writing before signing anything")