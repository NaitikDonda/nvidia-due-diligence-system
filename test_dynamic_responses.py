import sys
import os

# Add outputs directory to path to import the generated engine
sys.path.append(os.path.join(os.getcwd(), "outputs"))

try:
    from nvidia_engine import analyze_nvidia
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

queries = [
    "if todays stock of nvidia is 500 dollars and yestarday was 250 so should I buy the stock",
    "if stock of today is 20 dollars and avg is 120 so shuld I buy"
]

for q in queries:
    print(f"\nQuery: {q}")
    result = analyze_nvidia(q)
    if result['synthesis']:
        print(f"Recommendation: {result['synthesis']['recommendation']}")
        print(f"Signals: {result['synthesis']['signals']}")
    else:
        print("No synthesis result")
