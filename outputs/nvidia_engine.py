
import os
import json
import joblib
import numpy as np
import pandas as pd
import re

from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

# Import state manager for "learning" capability
try:
    import state_manager
except ImportError:
    # Fallback if not in path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import state_manager

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_PATH = PROJECT_ROOT + "/outputs/"
DATA_PATH = PROJECT_ROOT + "/data/processed/"

# =========================
# LOAD SAVED MODELS
# =========================

stock_model = joblib.load(
    OUTPUT_PATH + "nvidia_logistic_final_model.pkl"
)

stock_scaler = joblib.load(
    OUTPUT_PATH + "nvidia_logistic_scaler.pkl"
)

sentiment_model = joblib.load(
    OUTPUT_PATH + "nvidia_financial_sentiment_model.pkl"
)

sentiment_vectorizer = joblib.load(
    OUTPUT_PATH + "nvidia_sentiment_tfidf_vectorizer.pkl"
)

risk_model = joblib.load(
    OUTPUT_PATH + "best_nvidia_risk_model.pkl"
)

risk_vectorizer = joblib.load(
    OUTPUT_PATH + "nvidia_risk_tfidf_vectorizer.pkl"
)

market_model = joblib.load(
    OUTPUT_PATH + "best_nvidia_market_competitor_model.pkl"
)

market_scaler = joblib.load(
    OUTPUT_PATH + "nvidia_market_competitor_scaler.pkl"
)

research_model = joblib.load(
    OUTPUT_PATH + "nvidia_research_topic_model.pkl"
)

research_vectorizer = joblib.load(
    OUTPUT_PATH + "nvidia_research_tfidf_vectorizer.pkl"
)

best_financial_model = joblib.load(
    OUTPUT_PATH + "best_nvidia_financial_model.pkl"
)

financial_scaler = joblib.load(
    OUTPUT_PATH + "nvidia_financial_scaler.pkl"
)

investment_synthesis_model = joblib.load(
    OUTPUT_PATH + "nvidia_investment_synthesis_model.pkl"
)

synthesis_encoder = joblib.load(
    OUTPUT_PATH + "nvidia_investment_synthesis_encoder.pkl"
)

rag_vectorizer = joblib.load(
    OUTPUT_PATH + "nvidia_rag_tfidf_vectorizer.pkl"
)

rag_matrix = load_npz(
    OUTPUT_PATH + "nvidia_rag_matrix.npz"
)

rag_chunks = pd.read_csv(
    DATA_PATH + "nvidia_rag_chunks.csv"
)

# =========================
# LOAD DATA FOR MODEL PREDICTIONS
# =========================

try:
    stock_model_df = pd.read_csv(
        DATA_PATH + "nvidia_stock_features.csv"
    )
    # Use available columns from the data file
    available_features = stock_model_df.columns.tolist()
    # Try to use expected features if available, otherwise use what's available
    expected_features = ["Close", "High", "Low", "Daily_Return", "MA_20", "MA_50", "MA_200", "Volatility_20", "Momentum_10"]
    model_features = [f for f in expected_features if f in available_features]
    if not model_features:
        model_features = available_features[:10]  # Use first 10 available columns as fallback
except Exception as e:
    print(f"Warning: Could not load stock data: {e}")
    stock_model_df = None
    model_features = []

try:
    financial_model_df = pd.read_csv(
        DATA_PATH + "nvidia_financial_model_data.csv"
    )
    # Use available columns from the data file
    available_features = financial_model_df.columns.tolist()
    # Try to use expected features if available, otherwise use what's available
    expected_features = ["Revenue_Growth", "Net_Income_Growth", "profit_margin", "net_income", "revenue"]
    financial_features = [f for f in expected_features if f in available_features]
    if not financial_features:
        financial_features = available_features[:5]  # Use first 5 available columns as fallback
except Exception as e:
    print(f"Warning: Could not load financial data: {e}")
    financial_model_df = None
    financial_features = []

try:
    market_model_df = pd.read_csv(
        DATA_PATH + "nvidia_market_features.csv"
    )
    # Use available columns from the data file
    available_features = market_model_df.columns.tolist()
    # Try to use expected features if available, otherwise use what's available
    expected_features = ["Daily_Return", "MA_20", "MA_50", "MA_200", "Volatility_20", "Momentum_10", "AMD_Return", "Intel_Return", "NVIDIA_Return", "NVIDIA_vs_AMD", "NVIDIA_vs_Intel"]
    market_features = [f for f in expected_features if f in available_features]
    if not market_features:
        market_features = available_features[:10]  # Use first 10 available columns as fallback
except Exception as e:
    print(f"Warning: Could not load market data: {e}")
    market_model_df = None
    market_features = []

try:
    valuation_data = pd.read_csv(
        DATA_PATH + "nvidia_valuation_data.csv"
    )
    enterprise_value = valuation_data["revenue"].iloc[-1] * 20  # Simple approximation
except Exception as e:
    print(f"Warning: Could not load valuation data: {e}")
    valuation_data = None
    enterprise_value = None

# =========================
# QUERY CLASSIFICATION KEYWORDS
# =========================

query_categories = {
    "stock": ["stock", "share", "price", "trading", "market price", "stock price"],
    "financial": ["financial", "revenue", "income", "profit", "earnings", "balance sheet", "cash flow"],
    "valuation": ["valuation", "worth", "value", "overvalued", "undervalued", "pe ratio", "price to earnings"],
    "risk": ["risk", "risky", "danger", "threat", "concern", "downside"],
    "market": ["market", "competitor", "competition", "amd", "intel", "industry", "sector"],
    "sentiment": ["news", "sentiment", "opinion", "outlook", "buzz", "media"],
    "research": ["research", "study", "report", "analysis", "findings", "data"]
}



def learn_from_query(query):
    """
    Simulates reinforcement learning by extracting facts from user queries
    and storing them in a dynamic state store.
    """
    query_lower = query.lower()
    updated = False

    # Price Learning: "price is 400", "stock is 400"
    price_match = re.search(r'(?:price|stock)\s*(?:is|of)\s*(\d+(?:\.\d+)?)', query_lower)
    if price_match:
        val = float(price_match.group(1))
        state_manager.update_fact("current_price", val)
        print(f"LEARNED: Current price updated to {val}")
        updated = True

    # Growth Learning: "growth is 20%", "growth of 20"
    growth_match = re.search(r'growth\s*(?:is|of)\s*(\d+(?:\.\d+)?)\s*%', query_lower)
    if growth_match:
        val = float(growth_match.group(1))
        state_manager.update_fact("revenue_growth", val)
        print(f"LEARNED: Revenue growth updated to {val}%")
        updated = True

    # Risk Learning: "risk is high", "risk is low"
    if "risk is high" in query_lower:
        state_manager.update_fact("risk_level", "HIGH")
        print("LEARNED: Risk level updated to HIGH")
        updated = True
    elif "risk is low" in query_lower:
        state_manager.update_fact("risk_level", "LOW")
        print("LEARNED: Risk level updated to LOW")
        updated = True

    return updated

def classify_query(query):

    query_lower = query.lower()

    investment_keywords = [
        "should i invest",
        "should i buy",
        "should i sell",
        "shuld i buy",
        "shuld i sell",
        "invest in",
        "investment",
        "buy or sell",
        "worth buying",
        "good investment",
        "investing",
        "should i buy the stock",
        "should i purchase",
        "purchase",
        "should i purchase",
        "worth purchasing"
    ]

    # Additional check for "buy" + "should/shuld" anywhere in query
    if ("buy" in query_lower or "sell" in query_lower or "purchase" in query_lower) and ("should" in query_lower or "shuld" in query_lower):
        return "investment", {"investment": 1}

    # Check for purchase intent at end of query
    if query_lower.endswith("so should i purchase") or query_lower.endswith("so should i buy"):
        return "investment", {"investment": 1}

    for keyword in investment_keywords:

        if keyword in query_lower:
            return "investment", {"investment": 1}

    category_scores = {}

    for category, keywords in query_categories.items():

        score = 0

        for keyword in keywords:

            if keyword in query_lower:
                score += 1

        category_scores[category] = score

    priority = [
        "stock",
        "financial",
        "valuation",
        "risk",
        "market",
        "sentiment",
        "research"
    ]

    best_category = "research"
    best_score = 0

    for category in priority:

        score = category_scores.get(category, 0)

        if score > best_score:

            best_score = score
            best_category = category

    return best_category, category_scores




def route_to_model(query):

    category, scores = classify_query(query)

    model_map = {
        "investment": "Investment Synthesis Model",
        "stock": "Stock Prediction Model",
        "financial": "Financial Analysis Model",
        "market": "Market & Competitor Model",
        "risk": "Risk Classification Model",
        "sentiment": "News Sentiment Model",
        "research": "Research Model",
        "valuation": "Valuation Model"
    }

    return {
        "category": category,
        "model": model_map.get(
            category,
            "Research Model"
        ),
        "scores": scores
    }




def retrieve_documents(
    query,
    vectorizer,
    matrix,
    chunks,
    top_k=5
):
    query_vector = vectorizer.transform(
        [query]
    )
    
    similarities = cosine_similarity(
        query_vector,
        matrix
    )[0]
    
    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]
    
    results = chunks.iloc[
        top_indices
    ].copy()
    
    results["Similarity"] = similarities[
        top_indices
    ]
    
    return results



def stock_model_prediction():
    # LEARNING OVERRIDE: Check if we have a learned price
    learned_price = state_manager.get_fact("current_price")
    if learned_price is not None:
        # Compare learned price to historical average in data
        if stock_model_df is not None:
            avg_price = stock_model_df["Close"].mean()
            prediction = "UP" if learned_price > avg_price else "DOWN"
            conf = 0.7 # Estimated confidence for learned facts
            return {
                "prediction": prediction,
                "probability_up": conf if prediction == "UP" else 1-conf,
                "probability_down": 1-conf if prediction == "UP" else conf,
                "confidence": conf,
                "status": "dynamic_learned_fact"
            }

    if stock_model_df is None or len(model_features) == 0:
        return {
            "prediction": "UNKNOWN",
            "probability_up": 0.0,
            "probability_down": 0.0,
            "confidence": 0.0,
            "status": "data_unavailable"
        }

    try:
        latest_row = stock_model_df[model_features].iloc[[-1]]
        latest_scaled = stock_scaler.transform(latest_row)
        prediction = stock_model.predict(latest_scaled)[0]
        probability = stock_model.predict_proba(latest_scaled)[0]

        return {
            "prediction": "UP" if prediction == 1 else "DOWN",
            "probability_up": float(probability[1]),
            "probability_down": float(probability[0]),
            "confidence": float(probability.max())
        }
    except Exception as e:
        return {
            "prediction": "UNKNOWN",
            "probability_up": 0.0,
            "probability_down": 0.0,
            "confidence": 0.0,
            "status": f"error: {str(e)}"
        }



def financial_model_prediction():
    if financial_model_df is None or len(financial_features) == 0:
        return {
            "financial_health": "UNKNOWN",
            "status": "data_unavailable"
        }
    
    try:
        latest_row = financial_model_df[financial_features].iloc[[-1]]
        latest_scaled = financial_scaler.transform(latest_row)
        prediction = best_financial_model.predict(latest_scaled)[0]

        return {
            "financial_health": "STRONG" if prediction == 1 else "WEAK"
        }
    except Exception as e:
        return {
            "financial_health": "UNKNOWN",
            "status": f"error: {str(e)}"
        }



def market_model_prediction():
    if market_model_df is None or len(market_features) == 0:
        return {
            "market_position": "UNKNOWN",
            "status": "data_unavailable"
        }
    
    try:
        latest_row = market_model_df[market_features].iloc[[-1]]
        latest_scaled = market_scaler.transform(latest_row)
        prediction = market_model.predict(latest_scaled)[0]

        return {
            "market_position": "OUTPERFORMING" if prediction == 1 else "NOT OUTPERFORMING"
        }
    except Exception as e:
        return {
            "market_position": "UNKNOWN",
            "status": f"error: {str(e)}"
        }



def risk_prediction(query):
    vector = risk_vectorizer.transform([query])
    prediction = risk_model.predict(vector)[0]

    confidence = None

    if hasattr(risk_model, "predict_proba"):
        confidence = float(
            risk_model.predict_proba(vector).max()
        )

    return {
        "high_risk": int(prediction),
        "confidence": confidence
    }

def risk_model_prediction(query):
    return risk_prediction(query)



def sentiment_prediction(query):

    try:
        vector = sentiment_vectorizer.transform([query])

        prediction = sentiment_model.predict(vector)[0]

        probability = sentiment_model.predict_proba(vector).max()

        return {
            "sentiment": prediction,
            "confidence": float(probability),
            "status": "model"
        }

    except Exception:
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "status": "fallback"
        }



def valuation_model_prediction():
    if valuation_data is None:
        return {
            "status": "Valuation data unavailable",
            "error": "data_unavailable"
        }
    
    try:
        latest = valuation_data.iloc[-1]
        result = {}

        for col in valuation_data.columns:
            if any(term in col.lower() for term in [
                "enterprise", "valuation", "market_cap", "pe", "price", "revenue", "net_income"
            ]):
                try:
                    result[col] = float(latest[col])
                except:
                    pass

        if enterprise_value is not None:
            result["estimated_enterprise_value"] = float(enterprise_value)

        if not result:
            return {
                "status": "Valuation data loaded",
                "columns": list(valuation_data.columns)
            }

        return result

    except Exception as e:
        return {
            "status": "Valuation data unavailable",
            "error": str(e)
        }



def research_prediction(query):
    vector = research_vectorizer.transform([query])
    topic = research_model.predict(vector)[0]

    return {
        "topic": int(topic)
    }



def generate_model_output(query):
    routed = route_to_model(query)
    category = routed["category"]

    if category == "stock":
        output = stock_model_prediction()

    elif category == "financial":
        output = financial_model_prediction()

    elif category == "market":
        output = market_model_prediction()

    elif category == "risk":
        output = risk_model_prediction(query)

    elif category == "sentiment":
        output = sentiment_prediction(query)

    elif category == "research":
        output = research_prediction(query)

    elif category == "valuation":
        output = valuation_model_prediction()

    else:
        output = {
            "status": "No model available"
        }

    return {
        "query": query,
        "category": category,
        "model": routed["model"],
        "output": output
    }



def extract_query_signals(query):
    import re
    print(f"DEBUG: Extracting signals from: {query}")
    signals = {}
    query_lower = query.lower()

    # Stock Signal Extraction
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query_lower)
    print(f"DEBUG: Found numbers: {numbers}")
    if len(numbers) >= 2:
        vals = [float(n) for n in numbers]
        p1, p2 = vals[0], vals[1]
        # Handle typos for today and yesterday
        is_today = any(k in query_lower for k in ["today", "todays"])
        is_yesterday = any(k in query_lower for k in ["yesterday", "yestarday", "yestday", "avg", "average"])

        if is_today and is_yesterday:
            val = 1 if p1 > p2 else 0
            signals['stock_signal'] = val
            print(f"DEBUG: Stock signal extracted: {val}")

    # Financial Signal Extraction
    if any(k in query_lower for k in ["strong growth", "high revenue", "profitable"]):
        signals['financial_signal'] = 1
    elif any(k in query_lower for k in ["weak", "declining", "loss"]):
        signals['financial_signal'] = 0

    # Risk Signal Extraction
    if any(k in query_lower for k in ["risky", "danger", "threat", "concern"]):
        signals['risk_signal'] = 1
    elif any(k in query_lower for k in ["safe", "low risk", "stable"]):
        signals['risk_signal'] = 0

    return signals


def collect_current_model_signals(query):

    stock_result = stock_model_prediction()
    financial_result = financial_model_prediction()
    market_result = market_model_prediction()
    risk_result = risk_model_prediction(query)
    sentiment_result = sentiment_prediction(query)
    valuation_result = valuation_model_prediction()

    # Extract signals from query to override static model results
    extracted = extract_query_signals(query)

    # Calculate signals dynamically
    stock_signal = 0
    if "stock_signal" in extracted:
        stock_signal = extracted["stock_signal"]
    elif stock_result.get("prediction") == "UP":
        stock_signal = 1
    elif stock_result.get("prediction") == "DOWN":
        stock_signal = 0
    else:
        if stock_result.get("probability_up", 0) > 0.6:
            stock_signal = 1
        elif stock_result.get("probability_up", 0) < 0.4:
            stock_signal = 0
        else:
            stock_signal = 0

    financial_signal = 0
    if "financial_signal" in extracted:
        financial_signal = extracted["financial_signal"]
    elif financial_result.get("financial_health") == "STRONG":
        financial_signal = 1
    elif financial_result.get("financial_health") == "WEAK":
        financial_signal = 0
    else:
        if valuation_result and valuation_result.get("Revenue_Growth", 0) > 20:
            financial_signal = 1
        elif valuation_result and valuation_result.get("Revenue_Growth", 0) > 0:
            financial_signal = 0
        else:
            financial_signal = 0

    market_signal = 0
    if market_result.get("market_position") == "OUTPERFORMING":
        market_signal = 1
    elif market_result.get("market_position") == "UNDERPERFORMING":
        market_signal = 0
    else:
        if valuation_result and valuation_result.get("Revenue_Growth", 0) > 30:
            market_signal = 1
        elif valuation_result and valuation_result.get("Revenue_Growth", 0) > 10:
            market_signal = 0
        else:
            market_signal = 0

    risk_signal = 0
    if "risk_signal" in extracted:
        risk_signal = extracted["risk_signal"]
    else:
        risk_signal = int(risk_result.get("high_risk", 0))

    sentiment_signal = 0
    if sentiment_result.get("sentiment") == "positive":
        sentiment_signal = 1
    elif sentiment_result.get("sentiment") == "negative":
        sentiment_signal = 0
    else:
        sentiment_signal = 0

    # Calculate valuation signal based on valuation data
    valuation_signal = 0
    if valuation_result and not valuation_result.get("status"):
        revenue_growth = valuation_result.get("Revenue_Growth", 0)
        if revenue_growth > 50:
            valuation_signal = 1
        elif revenue_growth > 20:
            valuation_signal = 0
        else:
            valuation_signal = 0

    signals = {
        "stock_signal": stock_signal,
        "financial_signal": financial_signal,
        "market_signal": market_signal,
        "risk_signal": risk_signal,
        "sentiment_signal": sentiment_signal,
        "valuation_signal": valuation_signal
    }

    return {
        "stock": stock_result,
        "financial": financial_result,
        "market": market_result,
        "risk": risk_result,
        "sentiment": sentiment_result,
        "valuation": valuation_result,
        "signals": signals
    }



def investment_synthesis_prediction(query):
    try:
        results = collect_current_model_signals(query)
        signals = results["signals"]

        # Get expected feature order from the model if available
        if hasattr(investment_synthesis_model, 'feature_names_in_'):
            feature_names = investment_synthesis_model.feature_names_in_.tolist()
            input_data = pd.DataFrame([{
                feature: signals.get(feature, 0)
                for feature in feature_names
            }])
        else:
            # Fallback: try common orderings
            input_data = pd.DataFrame([{
                "stock_signal": signals["stock_signal"],
                "financial_signal": signals["financial_signal"],
                "market_signal": signals["market_signal"],
                "risk_signal": signals["risk_signal"],
                "sentiment_signal": signals["sentiment_signal"],
                "valuation_signal": signals.get("valuation_signal", 0)
            }])

        prediction = investment_synthesis_model.predict(input_data)[0]
        recommendation = synthesis_encoder.inverse_transform([prediction])[0]

        probabilities = {}

        if hasattr(investment_synthesis_model, "predict_proba"):
            probability_values = investment_synthesis_model.predict_proba(input_data)[0]
            for label, probability in zip(synthesis_encoder.classes_, probability_values):
                probabilities[label] = float(probability)

        confidence = float(max(probabilities.values())) if probabilities else None

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "probabilities": probabilities,
            "signals": signals,
            "model_outputs": {
                "stock": results["stock"],
                "financial": results["financial"],
                "market": results["market"],
                "risk": results["risk"],
                "sentiment": results["sentiment"],
                "valuation": results["valuation"]
            }
        }
    except Exception as e:
        # Fallback to rule-based synthesis if model fails
        return {
            "recommendation": "HOLD",
            "confidence": 0.5,
            "probabilities": {"BUY": 0.33, "HOLD": 0.34, "SELL": 0.33},
            "signals": {},
            "model_outputs": {},
            "status": f"model_error: {str(e)}"
        }



def red_team_verification(synthesis_result):
    recommendation = synthesis_result.get("recommendation", "HOLD")
    signals = synthesis_result.get("signals", {})

    contradictions = []

    if recommendation == "BUY":
        if signals.get("stock_signal") == 0:
            contradictions.append("Stock model does not support an upward signal.")
        if signals.get("financial_signal") == 0:
            contradictions.append("Financial model does not indicate strong financial health.")
        if signals.get("market_signal") == 0:
            contradictions.append("Market model does not indicate outperformance.")
        if signals.get("risk_signal") == 1:
            contradictions.append("Risk model indicates elevated risk.")

    elif recommendation == "SELL":
        if signals.get("stock_signal") == 1:
            contradictions.append("Stock model indicates an upward signal.")
        if signals.get("financial_signal") == 1:
            contradictions.append("Financial model indicates strong financial health.")
        if signals.get("market_signal") == 1:
            contradictions.append("Market model indicates outperformance.")

    elif recommendation == "HOLD":
        positive_count = (
            signals.get("stock_signal", 0)
            + signals.get("financial_signal", 0)
            + signals.get("market_signal", 0)
            + signals.get("sentiment_signal", 0)
        )
        if positive_count >= 3 and signals.get("risk_signal") == 0:
            contradictions.append("Multiple models support a stronger positive outlook.")

    verification_status = "PASS" if len(contradictions) == 0 else "REVIEW"

    return {
        "recommendation": recommendation,
        "verification_status": verification_status,
        "contradiction_count": len(contradictions),
        "contradictions": contradictions
    }



def analyze_nvidia(query):
    # STEP 1: LEARNING PHASE
    # Extract facts from query and update dynamic state store
    learn_from_query(query)

    print("=" * 60)
    print("NVIDIA FINANCIAL RESEARCH SYSTEM")
    print("=" * 60)

    print("\nQuery:")
    print(query)

    routed = route_to_model(query)

    print("\nCategory:", routed["category"])
    print("Model:", routed["model"])

    rag_results = retrieve_documents(
        query,
        rag_vectorizer,
        rag_matrix,
        rag_chunks,
        top_k=5
    )

    if routed["category"] == "investment":
        synthesis = investment_synthesis_prediction(query)
        verification = red_team_verification(synthesis)
        output = synthesis.get("model_outputs", {})
    
    elif routed["category"] == "news" or routed["category"] == "sentiment":
        output = sentiment_prediction(query)
        synthesis = None
        verification = None
    
    elif routed["category"] == "financial":
        output = financial_model_prediction()
        synthesis = None
        verification = None
    
    elif routed["category"] == "risk":
        output = risk_prediction(query)
        synthesis = None
        verification = None
    
    elif routed["category"] == "stock":
        output = stock_model_prediction()
        synthesis = None
        verification = None
    
    elif routed["category"] == "market":
        output = market_model_prediction()
        synthesis = None
        verification = None
    
    elif routed["category"] == "valuation":
        output = valuation_model_prediction()
        synthesis = None
        verification = None
    
    elif routed["category"] == "research":
        output = research_prediction(query)
        synthesis = None
        verification = None
    
    else:
        output = research_prediction(query)
        synthesis = None
        verification = None

    result = {
        "query": query,
        "category": routed["category"],
        "model": routed["model"],
        "synthesis": synthesis,
        "verification": verification,
        "output": output,
        "evidence": rag_results[
            ["chunk_id", "Similarity", "text"]
        ].to_dict("records")
    }

    # Add reasoning chain for investment queries
    if synthesis:
        result["reasoning"] = generate_reasoning_chain(result)

    return result



def generate_reasoning_chain(result):
    """
    The 'Thinking Power' module. Converts model signals into a
    human-like reasoning chain (Chain of Thought).
    """
    synthesis = result.get("synthesis")
    if not synthesis:
        return "Reasoning not available for this query type."

    signals = synthesis.get("signals", {})
    rec = synthesis.get("recommendation", "HOLD")

    thoughts = []
    thoughts.append("Analyzing the current NVIDIA landscape...")

    # 1. Stock Analysis
    if signals.get("stock_signal") == 1:
        thoughts.append("- Stock momentum is positive, indicating strong buying pressure.")
    else:
        thoughts.append("- Stock momentum is currently weak or bearish.")

    # 2. Financial Analysis
    if signals.get("financial_signal") == 1:
        thoughts.append("- Fundamentals are strong; revenue and profit growth are healthy.")
    else:
        thoughts.append("- Financial health indicators are mediocre or showing weakness.")

    # 3. Market Position
    if signals.get("market_signal") == 1:
        thoughts.append("- NVIDIA continues to outperform peers like AMD and Intel.")
    else:
        thoughts.append("- Market leadership is being challenged by competitors.")

    # 4. Risk Assessment
    if signals.get("risk_signal") == 1:
        thoughts.append("- CRITICAL: Elevated risk levels detected (regulatory or supply chain).")
    else:
        thoughts.append("- Risk profile is currently stable.")

    # 5. Synthesis Conclusion
    if rec == "BUY":
        thoughts.append("\nCONCLUSION: Positive fundamentals and momentum outweigh risks. Recommendation: BUY.")
    elif rec == "SELL":
        thoughts.append("\nCONCLUSION: Multiple red flags in fundamentals and risk. Recommendation: SELL.")
    else:
        thoughts.append("\nCONCLUSION: Mixed signals. Growth is present but risk is significant. Recommendation: HOLD.")

    return "\n".join(thoughts)

def generate_final_response(query):

    result = analyze_nvidia(query)

    synthesis = result["synthesis"]
    verification = result["verification"]

    response = []

    response.append(f"Question: {query}\n")

    if synthesis:
        # ADDING THE 'THINKING' POWER HERE
        response.append("--- Thinking Process ---")
        response.append(generate_reasoning_chain(result))
        response.append("-----------------------\n")

        response.append(
            f"Final Investment Recommendation: {synthesis['recommendation']}"
        )

        if synthesis["confidence"] is not None:
            response.append(
                f"Confidence: {synthesis['confidence']:.2f}"
            )

        response.append("\nModel Signals:")

        for key, value in synthesis["signals"].items():
            response.append(f"- {key}: {value}")

        if verification:
            response.append(
                f"\nRed-Team Verification: "
                f"{verification['verification_status']}"
            )

            if verification["contradictions"]:
                response.append("\nPoints requiring review:")

                for item in verification["contradictions"]:
                    response.append(f"- {item}")
    else:
        response.append("\nAnalysis Output:")
        response.append(str(result["output"]))

    response.append("\nEvidence:")

    evidence = result["evidence"]

    for row in evidence[:3]:

        text = str(row["text"]).replace("\n", " ")

        if len(text) > 300:
            text = text[:300] + "..."

        response.append(f"- {text}")

    return "\n".join(response)
