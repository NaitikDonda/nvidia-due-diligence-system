from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

app = FastAPI(
    title="NVIDIA Financial Research API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:62763"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "outputs"
)

sys.path.insert(
    0,
    OUTPUT_PATH
)


class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    conversation: Optional[List[Message]] = None


def generate_natural_answer(result):
    """Generate natural language response from structured analysis result."""
    if not result or result.get("status") == "error":
        return "I apologize, but I encountered an error processing your request."
    
    synthesis = result.get("synthesis", {})
    verification = result.get("verification", {})
    category = result.get("category", "")
    model = result.get("model", "")
    evidence = result.get("evidence", [])
    output = result.get("output", {})
    
    answer = ""
    
    # Build response based on category - category-specific pipelines
    if category == "investment":
        rec = synthesis.get("recommendation", "HOLD")
        conf = synthesis.get("confidence")
        conf_pct = f"{int(conf * 100)}%" if conf else "moderate"
        signals = synthesis.get("signals", {})
        scenario = synthesis.get("scenario", {}) or signals.get("scenario", {})
        
        if scenario.get("p_today") is not None and scenario.get("p_avg") is not None:
            p_today = scenario["p_today"]
            p_yesterday = scenario.get("p_yesterday")
            p_avg = scenario["p_avg"]
            chg = scenario.get("daily_change_pct", 0)
            val_diff = scenario.get("valuation_diff_pct", 0)

            answer += f"Based on your stock price scenario (Yesterday: ${p_yesterday:.2f}, Today: ${p_today:.2f}, Average: ${p_avg:.2f}), "
            answer += f"NVIDIA receives a **{rec}** assessment with **{conf_pct}** confidence.\n\n"

            if val_diff < -30:
                answer += f"**Key Financial Insight**: Trading at **${p_today:.2f}** represents a massive **{abs(val_diff):.1f}% discount** relative to the **${p_avg:.2f}** average price benchmark. "
                if chg >= 0:
                    answer += f"Combined with positive 1-day momentum (+{chg:.1f}%), this offers a strong margin of safety and upside potential for purchasing. "
                else:
                    answer += f"Even with minor short-term price pressure, the severe valuation discount makes this an attractive long-term entry point. "
            elif val_diff > 100:
                answer += f"**Key Financial Insight**: Trading at **${p_today:.2f}** places the stock at a substantial **+{val_diff:.1f}% premium** over the **${p_avg:.2f}** historical/baseline average. "
                if chg < 0:
                    answer += f"Although the stock experienced a **{chg:.1f}% pullback** from ${p_yesterday:.2f}, buying at high valuation multiples carries elevated mean-reversion risk. Caution is advised. "
                else:
                    answer += f"Despite positive momentum (+{chg:.1f}%), the current price remains heavily elevated above average historical valuation benchmarks. "
            else:
                answer += f"The current price (${p_today:.2f}) is close to average valuation levels (${p_avg:.2f}, {val_diff:+.1f}% variance) with {chg:+.1f}% 1-day price movement. "
        else:
            answer += f"Based on the available NVIDIA financial, market, stock, risk, valuation and research analysis, NVIDIA receives a **{rec}** assessment with **{conf_pct}** confidence. "
            
            # Add supporting factors
            factors = []
            if signals.get("stock_signal") == 1:
                factors.append("positive stock momentum")
            if signals.get("financial_signal") == 1:
                factors.append("strong financial health")
            if signals.get("market_signal") == 1:
                factors.append("outperforming market position")
            if signals.get("risk_signal") == 0:
                factors.append("manageable risk exposure")
            
            if factors:
                answer += f"Key supporting factors include {', '.join(factors)}. "
        
        # Add counter-factors
        counter_factors = []
        if signals.get("stock_signal") == 0:
            counter_factors.append("stock momentum concerns")
        if signals.get("financial_signal") == 0:
            counter_factors.append("financial health challenges")
        if signals.get("market_signal") == 0:
            counter_factors.append("competitive pressure")
        if signals.get("risk_signal") == 1:
            counter_factors.append("elevated risk exposure")
        
        if counter_factors:
            answer += f"However, {', '.join(counter_factors)} should be considered. "
    
    elif category == "news" or category == "sentiment":
        sentiment = output.get("sentiment", "neutral")
        conf = output.get("confidence", 0)
        conf_pct = f"{int(conf * 100)}%" if conf else "moderate"
        
        answer += f"Based on the available news and sentiment analysis, NVIDIA's current sentiment is {sentiment.upper()} with {conf_pct} confidence. "
        
        if evidence and len(evidence) > 0:
            answer += f"I found {len(evidence)} relevant news sources from the research corpus. "
            answer += "Note: These sources are from the available research dataset and may not reflect the most recent real-time news. "
        
        if sentiment == "positive":
            answer += "The news coverage suggests positive developments and favorable sentiment. "
        elif sentiment == "negative":
            answer += "The news coverage suggests concerns or negative developments. "
        else:
            answer += "The news coverage appears neutral or mixed. "
    
    elif category == "financial":
        financial_health = output.get("financial_health", "UNKNOWN")
        
        answer += f"Regarding NVIDIA's financial position, the analysis indicates {financial_health} financial health. "
        
        if evidence and len(evidence) > 0:
            answer += f"I retrieved {len(evidence)} relevant financial sources from the research corpus. "
        
        if financial_health == "STRONG":
            answer += "Key indicators suggest solid revenue growth, profitability, and balance sheet strength. "
        elif financial_health == "WEAK":
            answer += "Key indicators suggest areas of concern in revenue, profitability, or balance sheet metrics. "
        else:
            answer += "The analysis considers revenue, profitability, growth rates, and overall financial health indicators. "
    
    elif category == "risk":
        high_risk = output.get("high_risk", 0)
        conf = output.get("confidence", 0)
        conf_pct = f"{int(conf * 100)}%" if conf else "moderate"
        
        answer += f"Based on the risk analysis, NVIDIA's risk profile is {'HIGH' if high_risk else 'LOW'} with {conf_pct} confidence. "
        
        if evidence and len(evidence) > 0:
            answer += f"I retrieved {len(evidence)} relevant risk sources from the research corpus. "
        
        if high_risk:
            answer += "Key risk factors include market volatility, competitive pressures, operational challenges, and regulatory considerations. "
        else:
            answer += "NVIDIA maintains a relatively manageable risk profile with well-diversified revenue streams and strong market position. "
    
    elif category == "stock":
        prediction = output.get("prediction", "UNKNOWN")
        conf = output.get("confidence", 0)
        conf_pct = f"{int(conf * 100)}%" if conf else "moderate"
        
        answer += f"Regarding NVIDIA's stock outlook, the technical analysis indicates a {prediction} direction with {conf_pct} confidence. "
        
        if evidence and len(evidence) > 0:
            answer += f"I retrieved {len(evidence)} relevant sources from the research corpus. "
        
        if prediction == "UP":
            answer += "The technical indicators suggest upward momentum based on recent price trends, moving averages, and volatility patterns. "
        elif prediction == "DOWN":
            answer += "The technical indicators suggest caution based on recent price action and market conditions. "
        else:
            answer += "The analysis considers price trends, moving averages, volatility, and technical indicators. "
    
    elif category == "market":
        market_position = output.get("market_position", "UNKNOWN")
        
        answer += f"In terms of competitive positioning, NVIDIA's market position is {market_position}. "
        
        if evidence and len(evidence) > 0:
            answer += f"I retrieved {len(evidence)} relevant sources from the research corpus. "
        
        if market_position == "OUTPERFORMING":
            answer += "NVIDIA is outperforming in the market with strong competitive advantages in GPU technology, AI acceleration, and data center solutions. "
        elif market_position == "UNDERPERFORMING":
            answer += "NVIDIA faces competitive challenges from other semiconductor companies and market dynamics. "
        else:
            answer += "The analysis considers NVIDIA's position relative to competitors in the GPU, AI, and semiconductor markets, including market share, technological advantages, and competitive pressures. "
    
    elif category == "valuation":
        answer += "Regarding valuation, "
        
        if evidence and len(evidence) > 0:
            answer += f"I retrieved {len(evidence)} relevant sources from the research corpus. "
        
        # Use valuation data from synthesis if available
        if synthesis and synthesis.get("model_outputs", {}).get("valuation"):
            val_data = synthesis["model_outputs"]["valuation"]
            revenue_growth = val_data.get("Revenue_Growth", 0)
            net_income_growth = val_data.get("Net_Income_Growth", 0)
            
            answer += f"NVIDIA shows strong revenue growth of {revenue_growth:.1f}% and net income growth of {net_income_growth:.1f}%. "
            answer += "The valuation considers revenue growth rates, profitability metrics, market position, and industry comparables. "
        else:
            answer += "the analysis considers revenue growth rates, profitability metrics, market position, and industry comparables. "
    
    elif category == "research":
        if evidence and len(evidence) > 0:
            answer += f"Based on the research corpus analysis ({len(evidence)} sources retrieved):\n\n"
            summarized_facts = []
            for item in evidence:
                text_snippet = item.get("text", "").strip()
                if text_snippet:
                    # Clean snippet
                    clean_text = " ".join(text_snippet.split())
                    if len(clean_text) > 200:
                        clean_text = clean_text[:200] + "..."
                    summarized_facts.append(f"• {clean_text}")
            if summarized_facts:
                answer += "\n".join(summarized_facts[:3])
            else:
                answer += "Key research data includes NVIDIA's technology ecosystem, hardware offerings, and operational disclosures."
        else:
            answer += "NVIDIA designs and manufactures key accelerated computing products across several divisions:\n"
            answer += "• **Graphics & Gaming**: GeForce RTX GPUs, NVIDIA DLSS, and G-SYNC technology.\n"
            answer += "• **Data Center & AI Acceleration**: Hopper (H100/H200), Blackwell (B200/GB200), and Grace CPU architectures for enterprise AI training and inference.\n"
            answer += "• **Professional Visualization**: RTX Workstation GPUs and NVIDIA Omniverse platform.\n"
            answer += "• **Automotive & Robotics**: NVIDIA DRIVE platform and Jetson embedded systems.\n"
            answer += "• **Networking & Infrastructure**: Quantum InfiniBand, Spectrum Ethernet switches, and BlueField DPUs."
    
    else:
        # Fallback for unknown categories
        answer += f"Based on the {model} analysis, "
    
    # Add verification note only for investment category
    if category == "investment":
        if verification.get("verification_status") == "PASS":
            answer += "The red-team verification confirms the consistency of this assessment across different model outputs. "
        elif verification.get("verification_status") == "REVIEW":
            answer += "The red-team verification identified some aspects that warrant further review due to conflicting signals. "
    
    return answer.strip()


def is_greeting(query):
    """Check if the query is a casual greeting."""
    greetings = ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening"]
    query_lower = query.lower().strip()
    return any(query_lower == greeting or query_lower.startswith(greeting + " ") for greeting in greetings)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "NVIDIA Financial Research API"
    }


@app.post("/analyze")
def analyze(request: QueryRequest):
    try:
        # Check for casual greetings
        if is_greeting(request.query):
            return {
                "query": request.query,
                "answer": "Hello! I'm NVIDIA Intelligence, your AI-powered financial research assistant. I can help you analyze NVIDIA's financials, risks, valuation, market position, and investment outlook. What would you like to know?",
                "category": "greeting",
                "model": "NVIDIA Intelligence",
                "details": None
            }
        
        from nvidia_engine import analyze_nvidia
        
        # For multi-turn context, we could use conversation history here
        # For now, process the current query
        result = analyze_nvidia(request.query)
        
        # Generate natural language answer
        answer = generate_natural_answer(result)
        
        # Return both natural answer and structured details
        # Only include synthesis/verification for investment category
        details = {
            "model": result.get("model"),
            "category": result.get("category"),
            "reasoning": result.get("reasoning"),
            "synthesis": result.get("synthesis"),
            "verification": result.get("verification"),
            "output": result.get("output"),
            "evidence": result.get("evidence")
        }
        
        return {
            "query": request.query,
            "answer": answer,
            "category": result.get("category"),
            "model": result.get("model"),
            "details": details
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "query": request.query,
            "answer": "I apologize, but I encountered an error processing your request."
        }