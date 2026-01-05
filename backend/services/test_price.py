import asyncio
from services.market_service import get_market_price, calculate_buying_score

async def test_buying_score():
    print("Testing Buying Score Logic...")

    # 1. Fetch Real Market Price (e.g., Honda Civic)
    market_price = await get_market_price("Honda", "Civic", 2022)
    
    if market_price:
        print(f"✅ Market Price found: ${market_price:,.2f}")

        # 2. Simulate a Dealer Offer (Let's say they want $30,000)
        fake_dealer_offer = 30000 
        print(f"📄 Dealer Contract Price: ${fake_dealer_offer:,.2f}")

        # 3. Calculate Score
        score, verdict = calculate_buying_score(market_price, fake_dealer_offer)
        
        print("-" * 30)
        print(f"🏆 BUYING SCORE: {score}/10")
        print(f"📢 VERDICT: {verdict}")
        print("-" * 30)
    else:
        print("❌ Could not fetch market price.")

if __name__ == "__main__":
    asyncio.run(test_buying_score())