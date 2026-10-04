import sys
import os
sys.path.append(os.path.join(os.getcwd(), "outputs"))
from nvidia_engine import generate_final_response

print("--- TEST 1: Learning a Fact ---")
q1 = "Today's nvidia stock price is 1000 dollars"
print(f"Query: {q1}")
print(generate_final_response(q1))

print("\n\n--- TEST 2: Using Learned Fact for Prediction ---")
q2 = "Should I invest in NVIDIA?"
print(f"Query: {q2}")
print(generate_final_response(q2))
