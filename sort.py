"""
sort.py

Contains AI-suggested and optimized implementations for sorting a list of dictionaries by a key.
Includes examples and a short analysis.
"""
from operator import itemgetter
from typing import Any, Dict, Iterable, List, Optional

# AI-suggested implementation (concise)
def sort_dicts_by_key_ai(lst: Iterable[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """Return a new list sorted by dict[key]. May raise KeyError if some dicts lack the key."""
    return sorted(lst, key=lambda d: d[key], reverse=reverse)


# Optimized in-place implementation using itemgetter
def sort_dicts_by_key_inplace_fast(lst: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """In-place sort using operator.itemgetter (fast, requires that all dicts have `key`)."""
    lst.sort(key=itemgetter(key), reverse=reverse)
    return lst


# Safe in-place implementation that treats missing keys using dict.get
def sort_dicts_by_key_inplace_safe(lst: List[Dict[str, Any]], key: str, reverse: bool = False, missing_value: Optional[Any] = None) -> List[Dict[str, Any]]:
    """In-place sort that treats missing keys as `missing_value`.
    Slightly slower than itemgetter but safe when dicts may omit the key.
    """
    lst.sort(key=lambda d, k=key, mv=missing_value: d.get(k, mv), reverse=reverse)
    return lst


# DSU (decorate-sort-undecorate) to avoid repeated expensive key extraction
def sort_dicts_by_key_dsu(lst: Iterable[Dict[str, Any]], key: str, reverse: bool = False, missing_value: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Return a new list sorted using a decorated list of (key_value, dict) pairs.
    Uses extra memory but computes the key only once per element.
    """
    decorated = [(d.get(key, missing_value), d) for d in lst]
    decorated.sort(key=lambda x: x[0], reverse=reverse)
    return [d for _, d in decorated]


# Example usage
if __name__ == "__main__":
    data = [
        {"name": "alice", "score": 50},
        {"name": "bob", "score": 75},
        {"name": "carol", "score": 65},
        {"name": "dan"},  # missing score
    ]

    print("Original:", data)

    # Non-mutating AI-style
    try:
        print("sorted (ai):", sort_dicts_by_key_ai(data, "score"))
    except KeyError as e:
        print("AI-suggested raised KeyError for missing key:", e)

    # Safe in-place
    copy1 = list(data)
    print("inplace safe:", sort_dicts_by_key_inplace_safe(copy1, "score"))

    # Fast in-place (will raise KeyError on missing keys)
    copy2 = [d for d in data if "score" in d]
    print("inplace fast (filtered):", sort_dicts_by_key_inplace_fast(copy2, "score"))

    # DSU
    print("dsu:", sort_dicts_by_key_dsu(data, "score"))


# Analysis (~200 words)
ANALYSIS = (
    "The AI-suggested implementation (using sorted with a lambda) is concise and readable, "
    "but it allocates a new list and will raise KeyError if any dictionary lacks the requested key. "
    "The optimized in-place approach using `list.sort` with `operator.itemgetter` is typically the most efficient "
    "in common scenarios: it avoids allocating a new list (lower memory overhead) and `itemgetter` is a small C-level callable, "
    "which reduces Python-level call overhead compared with a lambda. If mutation of the input is acceptable and every element contains the key, "
    "this approach gives the best wall-clock performance. When dictionaries may omit the key, the safe in-place variant using `dict.get` "
    "trades a tiny runtime cost for safety and predictable behavior. If computing the sort key is expensive, the DSU pattern (decorate-sort-undecorate) "
    "computes each key once and can be faster overall at the cost of O(n) extra memory. All methods are O(n log n) asymptotically; differences are in constants, memory allocations, and safety. "
    "Choose `itemgetter` + in-place sort for maximum speed and low memory, `sorted(...)` when you need a non-mutating result, and DSU only when key extraction dominates cost."
)

if __name__ == "__main__":
    print("\nAnalysis (~200 words):\n")
    print(ANALYSIS)
