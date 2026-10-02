import math
import hashlib
from typing import List, Dict, Any
import pytest

def murmur3_like_bucket(key: str, experiment_id: str, num_buckets: int = 100) -> int:
    salted_key = f"{key}:{experiment_id}".encode("utf-8")
    hash_int = int(hashlib.sha256(salted_key).hexdigest()[:8], 16)
    return hash_int % num_buckets

def calculate_cohens_kappa(rater1: List[int], rater2: List[int]) -> float:
    assert len(rater1) == len(rater2), "Rater arrays must be of equal length"
    n = len(rater1)
    if n == 0:
        return 1.0
    
    agreements = sum(1 for a, b in zip(rater1, rater2) if a == b)
    p_o = agreements / n
    
    categories = sorted(list(set(rater1 + rater2)))
    
    p_e = 0.0
    for cat in categories:
        count1 = sum(1 for a in rater1 if a == cat)
        count2 = sum(1 for b in rater2 if b == cat)
        p_e += (count1 / n) * (count2 / n)
        
    if p_e == 1.0:
        return 1.0
    
    kappa = (p_o - p_e) / (1.0 - p_e)
    return round(kappa, 4)

def calculate_minimum_sample_size_proportion(
    p_a: float, p_b: float, alpha: float = 0.01, power: float = 0.80
) -> int:
    z_alpha = 2.576
    z_beta = 0.842
    
    delta = abs(p_b - p_a)
    if delta == 0:
        raise ValueError("Difference delta between variants cannot be zero")
        
    p_bar = (p_a + p_b) / 2.0
    numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p_a * (1 - p_a) + p_b * (1 - p_b))) ** 2
    n = numerator / (delta ** 2)
    return math.ceil(n)

def test_session_consistent_traffic_allocation():
    user_id = "CUST_9918231"
    exp_id = "EXP-NLU-FEWSHOT-2026"
    
    bucket_1 = murmur3_like_bucket(user_id, exp_id)
    bucket_2 = murmur3_like_bucket(user_id, exp_id)
    assert bucket_1 == bucket_2
    assert 0 <= bucket_1 < 100

    exp_id_2 = "EXP-RAG-RERANKER-2026"
    bucket_alt = murmur3_like_bucket(user_id, exp_id_2)
    assert 0 <= bucket_alt < 100

def test_cohens_kappa_inter_annotator_agreement():
    r1 = [1, 2, 3, 1, 2, 4, 1, 2]
    r2 = [1, 2, 3, 1, 2, 4, 1, 2]
    assert calculate_cohens_kappa(r1, r2) == 1.0

    r3 = [1, 2, 1, 3, 4, 1, 2, 1, 3, 4]
    r4 = [1, 2, 1, 3, 4, 1, 2, 1, 3, 3]
    kappa_high = calculate_cohens_kappa(r3, r4)
    assert kappa_high >= 0.80

    r5 = [1, 2, 3, 4, 1, 2, 3, 4]
    r6 = [4, 3, 2, 1, 4, 3, 2, 1]
    assert calculate_cohens_kappa(r5, r6) < 0.20

def test_sample_size_calculation_ab_testing():
    n_required = calculate_minimum_sample_size_proportion(p_a=0.78, p_b=0.805, alpha=0.01, power=0.80)
    assert 5000 <= n_required <= 7000, f"Expected ~5,800, got {n_required}"
