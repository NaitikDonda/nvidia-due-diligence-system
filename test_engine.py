#!/usr/bin/env python3
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "outputs")

sys.path.insert(0, OUTPUT_PATH)

try:
    from nvidia_engine import analyze_nvidia
    
    print("Testing NVIDIA Research Engine...")
    print("=" * 60)
    
    test_queries = [
        "Should I invest in NVIDIA?",
        "How is NVIDIA financially?",
        "What are NVIDIA's biggest risks?",
        "How does NVIDIA compare with AMD?",
        "What is NVIDIA's valuation?",
        "What does NVIDIA do?",
        "What is NVIDIA's stock outlook?"
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        print("-" * 60)
        
        try:
            result = analyze_nvidia(query)
            
            print(f"Category: {result.get('category')}")
            print(f"Model: {result.get('model')}")
            
            synthesis = result.get('synthesis', {})
            print(f"Recommendation: {synthesis.get('recommendation')}")
            print(f"Confidence: {synthesis.get('confidence')}")
            
            verification = result.get('verification', {})
            print(f"Verification: {verification.get('verification_status')}")
            
            evidence_count = len(result.get('evidence', []))
            print(f"Evidence retrieved: {evidence_count} chunks")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Engine test completed.")
    
except Exception as e:
    print(f"Failed to import engine: {e}")
    import traceback
    traceback.print_exc()
