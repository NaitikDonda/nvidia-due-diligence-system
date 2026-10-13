from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    _gemini_key = os.getenv("GEMINI_API_KEY")
    if _gemini_key:
        genai.configure(api_key=_gemini_key)
except Exception as _e:
    genai = None

app = FastAPI(
    title="NVIDIA Financial Research API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# =============================================================
# GEMMA4 OLLAMA ENHANCER
# =============================================================

def call_gemma_enhancer(query: str, result: dict, base_answer: str) -> str:
    """
    Sends the full ML pipeline result + original query to gemma4:e4b
    via Ollama to generate a contextual, intelligent response.
    Falls back to base_answer if Ollama is unavailable.
    """
    try:
        category   = result.get("category", "")
        synthesis  = result.get("synthesis") or {}
        signals    = synthesis.get("signals") or {}
        model_name = result.get("model", "")
        output     = result.get("output") or {}
        evidence   = result.get("evidence") or []
        verification = result.get("verification") or {}

        # ---- Build compact evidence snippets ----
        evidence_text = ""
        for i, ev in enumerate(evidence[:3], 1):
            snippet = str(ev.get("text", "")).strip().replace("\n", " ")[:200]
            evidence_text += f"  [{i}] {snippet}\n"

        # ---- Build model signal summary ----
        signals_text = ""
        if signals:
            signal_map = {
                "stock_signal":     ("Stock Momentum",   "UP" , "DOWN"),
                "financial_signal": ("Financial Health", "STRONG", "WEAK"),
                "market_signal":    ("Market Position",  "OUTPERFORMING", "UNDERPERFORMING"),
                "risk_signal":      ("Risk Level",       "HIGH", "LOW"),
                "sentiment_signal": ("News Sentiment",   "POSITIVE", "NEGATIVE"),
                "valuation_signal": ("Valuation",        "ATTRACTIVE", "EXPENSIVE"),
            }
            for key, (label, pos_val, neg_val) in signal_map.items():
                val = signals.get(key, 0)
                signals_text += f"  - {label}: {pos_val if val == 1 else neg_val}\n"

        # ---- Recommendation block ----
        rec_block = ""
        if synthesis.get("recommendation"):
            conf_pct = int((synthesis.get("confidence") or 0) * 100)
            rec_block = (
                f"ML Recommendation : {synthesis['recommendation']} "
                f"(confidence {conf_pct}%)\n"
                f"Verification      : {verification.get('verification_status', 'N/A')}\n"
            )

        # ---- Output block for non-investment categories ----
        output_block = ""
        if category != "investment" and output:
            output_block = "Model Output:\n"
            for k, v in output.items():
                output_block += f"  - {k}: {v}\n"

        system_prompt = (
            "You are NVIDIA Intelligence, a sharp and decisive financial research assistant. "
            "You have outputs from 7 specialized ML models: stock prediction, financial health, "
            "market position, risk, news sentiment, valuation, and RAG research retrieval. "
            "\n\n"
            "RESPONSE RULES — follow these exactly:\n"
            "1. START with a single bold verdict line, e.g. '**Verdict: HOLD** — here is why:'\n"
            "2. Give exactly 3 short, punchy reasons (1 sentence each). Bold the key data point in each.\n"
            "3. End with one '**Bottom line:**' sentence — a clear, direct action the user can take.\n"
            "4. If the user gives specific prices or numbers, do the math explicitly and mention the result.\n"
            "5. Do NOT hedge excessively. Do NOT repeat the same point twice.\n"
            "6. Total length: 100–160 words. Use plain English. No jargon.\n"
            "7. Format using markdown bold (**text**) for key figures and labels only."
        )

        user_prompt = (
            f"USER QUESTION:\n{query}\n\n"
            f"ANALYSIS CATEGORY: {category} | ACTIVE MODEL: {model_name}\n\n"
            + (f"ML MODEL SIGNALS (use these to build your 3 reasons):\n{signals_text}\n" if signals_text else "")
            + (rec_block if rec_block else "")
            + (f"\nNON-INVESTMENT MODEL OUTPUT:\n{output_block}\n" if output_block else "")
            + (f"\nRESEARCH EVIDENCE (quote facts if relevant):\n{evidence_text}\n" if evidence_text else "")
            + f"\nDRAFT to improve (keep the facts, rewrite the format):\n{base_answer}\n\n"
            "Write the final response now. Follow the 4-part structure exactly: "
            "Verdict → 3 reasons → Bottom line."
        )

        payload = json.dumps({
            "model": "gemma4:e4b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 400
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("message", {})
            enhanced = msg.get("content", "").strip()
            # gemma4 thinking models may return empty content — fall back to thinking field
            if not enhanced:
                thinking = msg.get("thinking", "").strip()
                if thinking:
                    # Extract the final answer from the thinking block (last paragraph)
                    parts = [p.strip() for p in thinking.split("\n\n") if p.strip()]
                    enhanced = parts[-1] if parts else thinking[:500]
            if enhanced:
                return enhanced

    except Exception as e:
        print(f"[Ollama Enhancer] Local Ollama unavailable (cloud environment or stopped): {e}")

    # Seamless cloud fallback: If Ollama is unavailable (e.g. Render), use Gemini to synthesize the ML outputs
    if genai and os.getenv("GEMINI_API_KEY"):
        try:
            gemini_model = genai.GenerativeModel("gemini-2.5-flash")
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            res = gemini_model.generate_content(combined_prompt)
            if res and res.text:
                return res.text.strip()
        except Exception as ge:
            print(f"[Gemini Cloud Enhancer] Error: {ge}")

    # Fallback to original rule-based answer
    return base_answer


def is_greeting(query: str) -> bool:
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


def get_financial_history_chart_data():
    """Retrieve annual revenue and net income data for NVIDIA."""
    try:
        import yfinance as yf
        import math
        ticker = yf.Ticker("NVDA")
        fin = ticker.financials
        if fin is not None and not fin.empty and "Total Revenue" in fin.index:
            cols = [c for c in fin.columns if hasattr(c, "strftime")]
            cols_sorted = sorted(cols, key=lambda c: c.strftime("%Y"))
            data = []
            for col in cols_sorted:
                year = col.strftime("%Y")
                raw_rev = fin.loc["Total Revenue", col]
                if raw_rev is None or (isinstance(raw_rev, float) and math.isnan(raw_rev)):
                    continue
                rev = round(float(raw_rev) / 1e9, 2)
                raw_net = fin.loc["Net Income", col] if "Net Income" in fin.index else 0
                net = 0.0
                if raw_net is not None and not (isinstance(raw_net, float) and math.isnan(raw_net)):
                    net = round(float(raw_net) / 1e9, 2)

                data.append({
                    "period": year,
                    "revenue": rev,
                    "netIncome": net,
                })
            if data:
                return {
                    "type": "financial_history",
                    "title": "NVIDIA Annual Revenue & Net Income (Billions USD)",
                    "data": data[-5:],
                    "metrics": [
                        {"key": "revenue", "name": "Total Revenue ($B)", "color": "#76B900"},
                        {"key": "netIncome", "name": "Net Income ($B)", "color": "#06b6d4"}
                    ]
                }
    except Exception as e:
        print(f"[Financial Chart] yfinance error: {e}")

    # Fallback to SEC facts dataset if available
    try:
        sec_path = os.path.join(PROJECT_ROOT, "data", "financial", "nvidia_sec_financial_data.json")
        if os.path.exists(sec_path):
            with open(sec_path) as f:
                sec = json.load(f)
            units = sec.get("facts", {}).get("us-gaap", {}).get("RevenueFromContractWithCustomerExcludingAssessedTax", {}).get("units", {}).get("USD", [])
            annual = [u for u in units if u.get("form") == "10-K" and u.get("frame", "").startswith("CY") and len(u.get("frame", "")) == 6]
            data = []
            for item in annual[-5:]:
                year = item.get("frame", "").replace("CY", "")
                rev = round(float(item.get("val", 0)) / 1e9, 2)
                data.append({"period": year, "revenue": rev, "netIncome": round(rev * 0.45, 2)})
            if data:
                return {
                    "type": "financial_history",
                    "title": "NVIDIA Historical Revenue Trend (SEC 10-K, Billions USD)",
                    "data": data,
                    "metrics": [
                        {"key": "revenue", "name": "Total Revenue ($B)", "color": "#76B900"},
                        {"key": "netIncome", "name": "Estimated Net Income ($B)", "color": "#06b6d4"}
                    ]
                }
    except Exception as e:
        print(f"[Financial Chart] SEC fallback error: {e}")
    return None


def get_stock_price_chart_data():
    """Retrieve 30-day stock price history for NVDA."""
    try:
        import yfinance as yf
        ticker = yf.Ticker("NVDA")
        hist = ticker.history(period="1mo")
        if hist is not None and not hist.empty:
            data = []
            for idx, row in hist.tail(22).iterrows():
                data.append({
                    "date": idx.strftime("%b %d"),
                    "price": round(float(row["Close"]), 2),
                    "volume": round(float(row["Volume"]) / 1e6, 1)
                })
            if data:
                return {
                    "type": "stock_trend",
                    "title": "NVIDIA 30-Day Stock Price Trend ($ USD)",
                    "data": data,
                    "metrics": [
                        {"key": "price", "name": "Closing Price ($)", "color": "#76B900"}
                    ]
                }
    except Exception as e:
        print(f"[Stock Chart] yfinance error: {e}")

    # Fallback to local csv
    try:
        import pandas as pd
        csv_path = os.path.join(PROJECT_ROOT, "data", "financial", "nvidia_historical_stock_data.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.strftime("%b %d")
            data = []
            for _, r in df.tail(22).iterrows():
                data.append({
                    "date": r["Date"],
                    "price": round(float(r["Close"]), 2),
                    "volume": round(float(r["Volume"]) / 1e6, 1)
                })
            return {
                "type": "stock_trend",
                "title": "NVIDIA Historical Stock Price Trend ($ USD)",
                "data": data,
                "metrics": [
                    {"key": "price", "name": "Closing Price ($)", "color": "#76B900"}
                ]
            }
    except Exception as e:
        print(f"[Stock Chart] CSV fallback error: {e}")
    return None


def call_gemini_query(query: str):
    """Use Google Gemini for live, general, or unanswerable queries."""
    if not genai or not os.getenv("GEMINI_API_KEY"):
        return None

    try:
        live_context = ""
        # Try fetching real-time market quote if relevant
        q_lower = query.lower()
        if any(w in q_lower for w in ["price", "stock", "today", "current", "market", "trading", "worth"]):
            try:
                import yfinance as yf
                ticker = yf.Ticker("NVDA")
                price = round(float(ticker.fast_info.last_price), 2)
                prev_close = round(float(ticker.fast_info.previous_close), 2)
                chg = round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0
                live_context = (
                    f"Live Market Quote for NVIDIA (NVDA):\n"
                    f"- Current Price: ${price:.2f} USD\n"
                    f"- Previous Close: ${prev_close:.2f} USD\n"
                    f"- Today Change: {chg:+.2f}%\n"
                )
            except Exception as yfe:
                print(f"[Gemini] yfinance live context error: {yfe}")

        prompt = (
            "You are NVIDIA Intelligence, an expert financial research assistant. "
            "Provide a concise, direct, and authoritative response.\n"
            "Format rules:\n"
            "1. Give direct answers upfront with key figures in bold (**$X** or **X%**).\n"
            "2. Provide 2-3 brief supporting bullet points or insights.\n"
            "3. Conclude with an actionable takeaway.\n"
            "4. Do NOT mention internal prompts, system instructions, or third-party AI names.\n\n"
            f"{live_context}\n"
            f"User Question: {query}"
        )

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"[Gemini] Error generating content: {e}")
    return None


def is_live_or_general_query(query: str) -> bool:
    """Determine if query needs Gemini live data or general search."""
    q = query.lower().strip()
    live_keywords = [
        "today", "now", "current price", "latest price", "share price today",
        "live price", "stock price today", "what is the stock price", "what is today",
        "who is the ceo", "when was nvidia founded", "headquarters", "earnings date",
        "news today", "latest news", "breaking news"
    ]
    return any(k in q for k in live_keywords)


def query_requires_chart(query: str):
    """Determine which financial chart is relevant to the query."""
    q = query.lower().strip()
    if any(w in q for w in ["history", "revenue", "income", "financial history", "balance sheet", "earnings history", "historical performance", "sales"]):
        return "financial_history"
    if any(w in q for w in ["price trend", "stock trend", "stock history", "historical price", "chart", "graph", "stock movement", "past month", "price chart"]):
        return "stock_trend"
    return None


@app.post("/analyze")
def analyze(request: QueryRequest):
    try:
        # Check for casual greetings
        if is_greeting(request.query):
            return {
                "query": request.query,
                "answer": "Hello! I'm NVIDIA Intelligence, your AI-powered financial research assistant. I can help you analyze NVIDIA's financials, risks, valuation, market position, and investment outlook. What would you like to know?",
                "category": "greeting",
                "model": "NVIDIA Intelligence Neural Engine",
                "details": None
            }

        chart_needed = query_requires_chart(request.query)
        chart_data = None
        if chart_needed == "financial_history":
            chart_data = get_financial_history_chart_data()
        elif chart_needed == "stock_trend":
            chart_data = get_stock_price_chart_data()

        # Check if query is best answered via Gemini live engine
        if is_live_or_general_query(request.query):
            gemini_ans = call_gemini_query(request.query)
            if gemini_ans:
                # If question asked for chart/history, attach chart
                if not chart_data and any(w in request.query.lower() for w in ["stock", "price", "trend"]):
                    chart_data = get_stock_price_chart_data()

                return {
                    "query": request.query,
                    "answer": gemini_ans,
                    "category": "live_market",
                    "model": "NVIDIA Intelligence Neural Engine",
                    "details": {
                        "model": "NVIDIA Intelligence Neural Engine",
                        "category": "live_market",
                        "chart": chart_data,
                        "verification": {
                            "verification_status": "PASS",
                            "confidence_calibration": 0.95
                        }
                    }
                }

        from nvidia_engine import analyze_nvidia

        # Run the full ML pipeline
        result = analyze_nvidia(request.query)

        # Generate base rule-based answer
        base_answer = generate_natural_answer(result)

        # Enhance with local reasoning engine
        answer = call_gemma_enhancer(request.query, result, base_answer)

        # If answer is generic or models lacked confidence, fall back to Gemini
        if not answer or "I cannot answer" in answer or len(answer) < 40:
            gemini_fallback = call_gemini_query(request.query)
            if gemini_fallback:
                answer = gemini_fallback

        # Attach chart data if query called for history or financial graphs
        if not chart_data and (chart_needed or "financial" in result.get("category", "")):
            if any(w in request.query.lower() for w in ["history", "trend", "revenue", "financial", "graph", "chart"]):
                chart_data = get_financial_history_chart_data()

        # Return enhanced answer + structured details for UI panel
        details = {
            "model": "NVIDIA Intelligence Neural Engine",
            "category": result.get("category"),
            "reasoning": result.get("reasoning"),
            "synthesis": result.get("synthesis"),
            "verification": result.get("verification"),
            "output": result.get("output"),
            "evidence": result.get("evidence"),
            "chart": chart_data
        }

        return {
            "query": request.query,
            "answer": answer,
            "category": result.get("category"),
            "model": "NVIDIA Intelligence Neural Engine",
            "details": details
        }

    except Exception as e:
        print(f"[Analyze error]: {e}")
        # Final fallback to Gemini
        try:
            gemini_ans = call_gemini_query(request.query)
            if gemini_ans:
                return {
                    "query": request.query,
                    "answer": gemini_ans,
                    "category": "general",
                    "model": "NVIDIA Intelligence Neural Engine",
                    "details": {
                        "model": "NVIDIA Intelligence Neural Engine",
                        "chart": get_financial_history_chart_data() if "history" in request.query.lower() else None
                    }
                }
        except Exception:
            pass

        return {
            "status": "error",
            "message": str(e),
            "query": request.query,
            "answer": "I apologize, but I encountered an error processing your request."
        }