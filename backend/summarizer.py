# summarizer.py
"""
Generate AI-powered contract summaries using Groq LLM
"""

import os
import json
import traceback
from groq import Groq
from config import settings
from logger import logger

GROQ_API_KEY = settings.GROQ_API_KEY
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client in summarizer: {e}", exc_info=True)
        groq_client = None
else:
    groq_client = None


def call_summary_llm(raw_text: str, structured_data: dict) -> dict:
    """
    Generate a comprehensive summary of the contract using LLM.
    """
    
    if not groq_client:
        return {
            "plain_summary": "LLM not configured. Unable to generate AI summary.",
            "red_flags": ["AI summary unavailable - check GROQ_API_KEY"],
            "key_terms": [],
            "confidence": "low"
        }
    
    # Get structured fields
    core = structured_data.get("core", {})
    financial = structured_data.get("financial_analysis", {})
    
    # Build context - more detailed
    vehicle_info = f"{core.get('year', 'N/A')} {core.get('make', 'N/A')} {core.get('model', 'N/A')}"
    monthly = core.get("monthly_payment", "N/A")
    term = core.get("term_months", "N/A")
    apr = core.get("apr", "") or core.get("interest_rate", "N/A")
    price = financial.get("vehicle_price", "") or core.get("vehicle_price", "N/A")
    
    # Truncate raw text
    truncated_text = raw_text[:6000] if len(raw_text) > 6000 else raw_text
    
    prompt = f"""You are a car contract analysis expert. Analyze this contract and provide a detailed summary.

CONTRACT TEXT EXCERPT:
{truncated_text}

EXTRACTED KEY DATA:
- Vehicle: {vehicle_info}
- VIN: {core.get('vin', 'N/A')}
- Price: {price}
- Monthly Payment: {monthly}
- Term: {term} months
- APR/Interest Rate: {apr}
- Buyer: {core.get('buyer_name', 'N/A')}
- Seller: {core.get('seller_name', 'N/A')}

Provide a JSON response with these EXACT fields:
{{
  "plain_summary": "3-4 sentence summary explaining: (1) what type of deal this is, (2) key financial terms, (3) overall assessment",
  "red_flags": ["specific concerning clause 1", "specific concerning clause 2", "etc"],
  "key_terms": ["important term 1", "important term 2", "important term 3"],
  "confidence": "high|medium|low"
}}

IMPORTANT:
- plain_summary: Write a clear, informative summary a buyer can understand
- red_flags: List SPECIFIC concerning terms from the contract (fees, penalties, restrictions). If none found, return empty array []
- key_terms: List the 3-5 most important financial obligations
- confidence: "high" if contract has clear terms, "medium" if some ambiguity, "low" if poor quality data

Return ONLY valid JSON, no markdown formatting."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=800,
            messages=[
                {"role": "system", "content": "You are a car contract expert. Analyze contracts objectively and return only JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result_text = response.choices[0].message.content
        
        # Clean markdown if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        result_text = result_text.strip()
        
        # Parse JSON
        try:
            summary = json.loads(result_text)
            
            # Validate and provide defaults
            if not isinstance(summary.get("plain_summary"), str) or not summary["plain_summary"]:
                summary["plain_summary"] = f"Contract for {vehicle_info} at {monthly}/month for {term} months with {apr} interest rate."
            
            if not isinstance(summary.get("red_flags"), list):
                summary["red_flags"] = []
            
            if not isinstance(summary.get("key_terms"), list):
                summary["key_terms"] = [
                    f"Monthly Payment: {monthly}",
                    f"Term: {term} months",
                    f"Interest Rate: {apr}"
                ]
            
            if summary.get("confidence") not in ["high", "medium", "low"]:
                summary["confidence"] = "medium"
            
            return summary
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error in summary: {e}. Response preview: {result_text[:200]}")
            # Return fallback with actual data
            return {
                "plain_summary": f"This is a contract for a {vehicle_info} with monthly payments of {monthly} over {term} months at {apr} interest. Review all terms carefully before signing.",
                "red_flags": ["Unable to analyze contract automatically - manual review recommended"],
                "key_terms": [
                    f"Monthly Payment: {monthly}",
                    f"Term: {term} months", 
                    f"APR: {apr}",
                    f"Vehicle Price: {price}"
                ],
                "confidence": "low"
            }
    
    except Exception as e:
        logger.error(f"Summary LLM error: {str(e)}", exc_info=True)
        
        # Fallback using structured data
        return {
            "plain_summary": f"Contract for {vehicle_info} with {monthly} monthly payment over {term} months at {apr} APR. Total vehicle price: {price}. Buyer: {core.get('buyer_name', 'N/A')}. Seller: {core.get('seller_name', 'N/A')}.",
            "red_flags": ["AI analysis unavailable - review contract manually for concerning terms"],
            "key_terms": [
                f"Monthly Payment: {monthly}",
                f"Loan/Lease Term: {term} months",
                f"Interest Rate: {apr}",
                f"Vehicle Cost: {price}"
            ],
            "confidence": "low"
        }
        # ============================================================
# PUBLIC ENTRY POINT (USED BY STREAMLIT APP)
# ============================================================

def summarize_contract(extracted: dict) -> dict:
    """
    Public summarization entry point for Streamlit.
    """

    raw_text = extracted.get("raw_text", "")
    structured = extracted.get("llm_structured_data_full", {})

    if not raw_text.strip():
        return {
            "plain_summary": "No readable text found to summarize.",
            "red_flags": [],
            "key_terms": [],
            "confidence": "low"
        }

    try:
        return call_summary_llm(raw_text, structured)
    except Exception as e:
        return {
            "plain_summary": f"Summary generation failed: {str(e)}",
            "red_flags": [],
            "key_terms": [],
            "confidence": "low"
        }

