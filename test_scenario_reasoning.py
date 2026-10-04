import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "outputs"))

from nvidia_engine import analyze_nvidia

def run_tests():
    print("=== TEST 1: Deep Discount Scenario ($20 yesterday, $21 today, $120 avg) ===")
    q1 = "if I want to purchase the stocks, yestarday is was 20$ and todays it is 21$ and the average price of stock is 120$ so should I purchase?"
    res1 = analyze_nvidia(q1)
    print("Recommendation:", res1.get("synthesis", {}).get("recommendation"))
    print("Confidence:", res1.get("synthesis", {}).get("confidence"))
    print("Reasoning:\n", res1.get("reasoning"))
    print("Evidence Count:", len(res1.get("evidence", [])))
    print()

    print("=== TEST 2: High Premium Scenario ($500 yesterday, $450 today, $120 avg) ===")
    q2 = "if I want to purchase the stocks, yestarday is was 500$ and todays it is 450$ and the average price of stock is 120$ so should I purchase?"
    res2 = analyze_nvidia(q2)
    print("Recommendation:", res2.get("synthesis", {}).get("recommendation"))
    print("Confidence:", res2.get("synthesis", {}).get("confidence"))
    print("Reasoning:\n", res2.get("reasoning"))
    print("Evidence Count:", len(res2.get("evidence", [])))
    print()

if __name__ == "__main__":
    run_tests()
