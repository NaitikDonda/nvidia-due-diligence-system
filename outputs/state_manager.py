"""
Simple state manager for dynamic learning capability.
Stores facts that can be learned from user queries.
"""

# Simple in-memory state store
_state_store = {}

def update_fact(key, value):
    """Update a fact in the state store."""
    _state_store[key] = value
    print(f"State updated: {key} = {value}")

def get_fact(key):
    """Get a fact from the state store."""
    return _state_store.get(key)

def clear_state():
    """Clear all facts from the state store."""
    _state_store.clear()
    print("State cleared")

def get_all_facts():
    """Get all facts from the state store."""
    return _state_store.copy()
