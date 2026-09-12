import json
import numpy as np

from db import get_connection
from embeddings import embed, cosine_sim
from heuristics import heuristic_score

BLOCK_THRESHOLD = 0.65
FLAG_THRESHOLD = 0.45

_fingerprint_cache = None  # list of (category, pattern_text, np.array)


def load_fingerprints(force=False):
    global _fingerprint_cache
    if _fingerprint_cache is not None and not force:
        return _fingerprint_cache

    conn = get_connection()
    rows = conn.execute(
        "SELECT CATEGORY, PATTERN_TEXT, EMBEDDING FROM SENTINEL.ATTACK_FINGERPRINTS"
    ).fetchall()
    _fingerprint_cache = [
        (cat, text, np.asarray(json.loads(emb), dtype=np.float32))
        for cat, text, emb in rows
    ]
    return _fingerprint_cache


def similarity_score(prompt: str):
    fingerprints = load_fingerprints()
    if not fingerprints:
        return 0.0, None

    prompt_vec = embed(prompt)
    best_score, best_category = 0.0, None
    for category, _text, vec in fingerprints:
        sim = cosine_sim(prompt_vec, vec)
        if sim > best_score:
            best_score, best_category = sim, category
    return best_score, best_category


def score_prompt(prompt: str):
    h_score, h_category = heuristic_score(prompt)
    s_score, s_category = similarity_score(prompt)

    combined = max(h_score, s_score)
    category = s_category if s_score >= h_score else h_category

    if combined >= BLOCK_THRESHOLD:
        decision = "BLOCK"
    elif combined >= FLAG_THRESHOLD:
        decision = "FLAG"
    else:
        decision = "ALLOW"

    return {
        "heuristic_score": round(h_score, 4),
        "similarity_score": round(s_score, 4),
        "matched_category": category,
        "decision": decision,
    }
