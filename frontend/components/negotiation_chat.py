import streamlit as st
import random
from datetime import datetime

class NegotiationChat:
    def __init__(self):
        self.ai_responses = [
            "Based on market data, you should target a 4.5% APR instead of 5.9%.",
            "The down payment seems high. Try negotiating for $2,000 instead of $2,500.",
            "Mention that you've seen better offers from competitors.",
            "Ask about promotional rates or first-time buyer discounts.",
            "Suggest extending the lease term to lower monthly payments.",
            "Request maintenance package to be included.",
            "Propose a higher mileage allowance with lower excess charges.",
            "Ask about loyalty discounts if you're a returning customer."
        ]
        
        self.dealer_responses = [
            "Our rates are competitive with the market.",
            "Let me check with my manager about the down payment.",
            "We can offer you an extended warranty instead.",
            "The mileage allowance is standard for all leases.",
            "We have a promotion ending this week.",
            "Your credit qualifies you for our best rate.",
            "I can offer you $500 off the down payment.",
            "Let me run the numbers with different terms."
        ]
    
    def display_chat_interface(self):
        """Display the negotiation chat interface"""
        st.subheader("🤖 Negotiation Assistant")
        st.info("Chat with our AI assistant to prepare for dealer negotiations")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['sender'] == 'user':
                    st.chat_message("user").write(message['text'])
                else:
                    st.chat_message("assistant").write(message['text'])
        
        # User input
        user_input = st.chat_input("Ask negotiation advice...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'sender': 'user',
                'text': user_input,
                'time': datetime.now().strftime("%H:%M")
            })
            
            # Generate AI response
            ai_response = self.generate_ai_response(user_input)
            st.session_state.chat_history.append({
                'sender': 'assistant',
                'text': ai_response,
                'time': datetime.now().strftime("%H:%M")
            })
            
            st.rerun()
        
        # Quick action buttons
        st.markdown("### 💡 Quick Questions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("How to lower interest?", use_container_width=True):
                st.session_state.chat_history.append({
                    'sender': 'user',
                    'text': "How can I negotiate a lower interest rate?",
                    'time': datetime.now().strftime("%H:%M")
                })
                st.rerun()
        
        with col2:
            if st.button("Reduce down payment?", use_container_width=True):
                st.session_state.chat_history.append({
                    'sender': 'user',
                    'text': "How to reduce the down payment?",
                    'time': datetime.now().strftime("%H:%M")
                })
                st.rerun()
        
        # Generate negotiation script
        st.markdown("---")
        st.subheader("📝 Negotiation Script")
        
        with st.expander("Generate Email to Dealer"):
            dealer_name = st.text_input("Dealer Name", "Sales Manager")
            issues = st.multiselect(
                "Issues to Address",
                ["High Interest Rate", "Large Down Payment", "Low Mileage", "Early Termination Fee", "Warranty Coverage"]
            )
            
            if st.button("Generate Email"):
                email_template = f"""Dear {dealer_name},

I've reviewed the lease proposal and would like to discuss the following:

"""
                if "High Interest Rate" in issues:
                    email_template += "- The APR of 5.9% seems higher than current market rates. Can we discuss a rate around 4.5%?\n"
                if "Large Down Payment" in issues:
                    email_template += "- The down payment of $2,500 is more than I anticipated. Can we reduce this to $2,000?\n"
                if "Low Mileage" in issues:
                    email_template += "- 10,000 miles/year may not be sufficient. Can we increase to 12,000 miles?\n"
                
                email_template += """
I'm prepared to proceed if we can reach agreement on these points.

Best regards,
[Your Name]
"""
                
                st.text_area("Email Template", email_template, height=200)
                
                st.download_button(
                    "📥 Download Email",
                    email_template,
                    "negotiation_email.txt",
                    "text/plain"
                )
    
    def generate_ai_response(self, user_input: str) -> str:
        """Generate AI response based on user input"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['interest', 'apr', 'rate']):
            return random.choice([
                "Research shows current market rates are 4-5%. Use this as leverage.",
                "Ask if they have promotional rates for first-time buyers.",
                "Mention you have pre-approval from another lender at 4.5%."
            ])
        
        elif any(word in input_lower for word in ['down payment', 'deposit']):
            return random.choice([
                "Many dealers offer $0 down promotions. Ask about current offers.",
                "Propose increasing monthly payment slightly to reduce down payment.",
                "Ask if you can split the down payment over first 3 months."
            ])
        
        elif any(word in input_lower for word in ['mileage', 'limit']):
            return random.choice([
                "Average American drives 13,500 miles/year. Request at least 12,000.",
                "Ask about the cost to increase mileage allowance.",
                "Propose paying slightly more monthly for higher mileage."
            ])
        
        return random.choice(self.ai_responses)