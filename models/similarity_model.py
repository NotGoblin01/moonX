"""
Prototype Similarity Model for MoonBase Planner
================================================
Compares a planetary target (Moon/Mars) with Earth analog locations using
normalized multi-feature semantic and parametric comparisons.

IMPORTANT NOTICE:
This module is a transparent prototype heuristic model built for hackathon exploration
and software scaffolding. It is NOT scientifically validated NASA AI or peer-reviewed
mission selection software.
"""

import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

# Configurable Weights Object
# Default weights:
# Terrain: 25%
# Slope: 15%
# Temperature: 15%
# Geology: 20%
# Aridity: 15%
# Surface Conditions: 10%
DEFAULT_ANALOG_WEIGHTS: Dict[str, float] = {
    "terrain": 0.25,
    "slope": 0.15,
    "temperature": 0.15,
    "geology": 0.20,
    "aridity": 0.15,
    "surface_conditions": 0.10
}

# Domain keyword taxonomy for transparent heuristic token overlap
FEATURE_KEYWORDS: Dict[str, List[str]] = {
    "terrain": [
        "crater", "lava", "tube", "basalt", "desert", "plateau", "canyon", "valley",
        "shield", "volcano", "caldera", "delta", "basin", "periglacial", "polar", "dune",
        "plain", "scree", "scarp", "subterranean", "cave"
    ],
    "geology": [
        "basalt", "breccia", "anorthosite", "permafrost", "carbonate", "clay", "smectite",
        "sulfate", "silicate", "perchlorate", "evaporite", "iron", "oxide", "sandstone",
        "pyroclastic", "ignimbrite", "dolerite", "halite", "volcanic", "glass"
    ],
    "aridity": [
        "hyper-arid", "arid", "semi-arid", "desiccated", "vacuum", "dry", "polar", "sublimation"
    ],
    "surface_conditions": [
        "dust", "regolith", "rubble", "scree", "boulder", "pavement", "cinder", "frost",
        "ice", "shadow", "radiation", "darkness", "dune", "crust", "shatter"
    ]
}

def extract_slope_mean(slope_str: str) -> float:
    """Extracts numeric average slope degrees from textual descriptions like '2° - 8°'."""
    nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", slope_str)]
    if not nums:
        return 10.0
    return sum(nums) / len(nums)

def extract_temp_extremes(temp_str: str) -> Tuple[float, float]:
    """Extracts min and max temperatures in Celsius from textual strings."""
    # Search for patterns like '-233°C to -53°C'
    c_matches = re.findall(r"(-?\d+)\s*°C", temp_str)
    if len(c_matches) >= 2:
        vals = [float(v) for v in c_matches]
        return min(vals), max(vals)
    elif len(c_matches) == 1:
        v = float(c_matches[0])
        return v, v
    return -20.0, 20.0

def calculate_token_similarity(text_a: str, text_b: str, domain_key: str) -> float:
    """Calculates normalized keyword and semantic overlap score between 0.0 and 100.0."""
    norm_a = set(re.findall(r"[a-z\-]+", text_a.lower()))
    norm_b = set(re.findall(r"[a-z\-]+", text_b.lower()))

    # Domain vocabulary filter
    vocab = set(FEATURE_KEYWORDS.get(domain_key, []))
    keywords_a = norm_a.intersection(vocab)
    keywords_b = norm_b.intersection(vocab)

    inter = len(keywords_a.intersection(keywords_b))
    
    # Specific strong affinities in planetary science analogs
    direct_pair_matches = [
        ("crater", "crater"),
        ("tube", "tube"),
        ("basalt", "basalt"),
        ("hyper-arid", "hyper-arid"),
        ("permafrost", "permafrost"),
        ("polar", "polar"),
        ("vacuum", "hyper-arid"),
        ("vacuum", "arid"),
        ("delta", "sandstone"),
        ("clays", "salts"),
        ("caldera", "shield")
    ]
    bonus = 0.0
    for term_a, term_b in direct_pair_matches:
        if (term_a in norm_a and term_b in norm_b) or (term_b in norm_a and term_a in norm_b):
            bonus += 18.0

    if not keywords_a and not keywords_b:
        gen_inter = len(norm_a.intersection(norm_b))
        return min(100.0, 50.0 + gen_inter * 8.0 + bonus)

    union = len(keywords_a.union(keywords_b))
    overlap_pct = (inter / union * 100.0) if union > 0 else 40.0
    
    score = 52.0 + (overlap_pct * 0.40) + bonus
    return min(100.0, max(35.0, score))

def calculate_slope_similarity(target_slope_str: str, analog_slope_str: str) -> Tuple[float, str]:
    """Computes normalized slope similarity based on angular difference."""
    t_slope = extract_slope_mean(target_slope_str)
    a_slope = extract_slope_mean(analog_slope_str)

    diff = abs(t_slope - a_slope)
    # Exponential decay distance: 0 deg diff -> 100, 30 deg diff -> ~50
    score = max(30.0, min(100.0, 100.0 - (diff * 2.2)))
    explanation = f"Target avg slope ~{t_slope:.1f}° vs Earth analog ~{a_slope:.1f}° (difference {diff:.1f}°)"
    return round(score, 1), explanation

def calculate_temperature_similarity(target_temp_str: str, analog_temp_str: str) -> Tuple[float, str]:
    """Computes normalized temperature similarity based on thermal envelope alignment."""
    t_min, t_max = extract_temp_extremes(target_temp_str)
    a_min, a_max = extract_temp_extremes(analog_temp_str)

    # Compare midpoint and range spread
    t_mid = (t_min + t_max) / 2.0
    a_mid = (a_min + a_max) / 2.0
    mid_diff = abs(t_mid - a_mid)

    # Planetary cold targets (like Moon/Mars) are rewarded for extreme sub-zero analogs
    if t_mid < -40.0:
        if a_min < -15.0:
            score = 92.0 - min(40.0, mid_diff * 0.25)
        else:
            score = 65.0 - min(30.0, mid_diff * 0.2)
    else:
        score = max(35.0, 100.0 - (mid_diff * 0.45))

    explanation = f"Target thermal range [{t_min:.0f}°C to {t_max:.0f}°C] vs Earth analog [{a_min:.0f}°C to {a_max:.0f}°C]"
    return round(score, 1), explanation

@dataclass
class FeatureScoreResult:
    feature: str
    weight_percent: float
    score: float
    weighted_score: float
    details: str

@dataclass
class AnalogComparisonResult:
    earth_analog_id: str
    earth_analog_name: str
    target_id: str
    target_name: str
    overall_analog_score: float
    feature_scores: Dict[str, Dict[str, Any]]
    explanation: str
    weights_used: Dict[str, float]
    model_type: str = "Prototype Weighted Multi-Feature Similarity Model (Demo Only)"

def evaluate_analog_similarity(
    target: Dict[str, Any],
    analog: Dict[str, Any],
    weights: Dict[str, float] = None
) -> AnalogComparisonResult:
    """
    Compares a planetary target with an Earth analog across the 6 normalized features:
    - Terrain
    - Slope
    - Temperature
    - Geology
    - Aridity
    - Surface Conditions
    """
    w = weights or DEFAULT_ANALOG_WEIGHTS

    feature_results: Dict[str, Dict[str, Any]] = {}
    weighted_total = 0.0

    # 1. Terrain Comparison (25%)
    t_terrain = target.get("terrain", target.get("terrain_type", ""))
    a_terrain = analog.get("terrain", analog.get("environment_type", ""))
    score_terrain = round(calculate_token_similarity(t_terrain, a_terrain, "terrain"), 1)
    weight_terrain = w.get("terrain", 0.25)
    weighted_terrain = score_terrain * weight_terrain
    weighted_total += weighted_terrain
    feature_results["terrain"] = {
        "score": score_terrain,
        "weight_percent": weight_terrain * 100.0,
        "weighted_score": round(weighted_terrain, 2),
        "target_value": t_terrain,
        "analog_value": a_terrain,
        "explanation": f"Evaluated morphological structures: {t_terrain.split(';')[0]} vs {a_terrain.split(';')[0]}"
    }

    # 2. Slope Comparison (15%)
    t_slope = target.get("slope", "5° - 20°")
    a_slope = analog.get("slope", "5° - 15°")
    score_slope, slope_exp = calculate_slope_similarity(t_slope, a_slope)
    weight_slope = w.get("slope", 0.15)
    weighted_slope = score_slope * weight_slope
    weighted_total += weighted_slope
    feature_results["slope"] = {
        "score": score_slope,
        "weight_percent": weight_slope * 100.0,
        "weighted_score": round(weighted_slope, 2),
        "target_value": t_slope,
        "analog_value": a_slope,
        "explanation": slope_exp
    }

    # 3. Temperature Comparison (15%)
    t_temp = target.get("temperature", target.get("temperature_range", "-100°C to 20°C"))
    a_temp = analog.get("temperature", "-10°C to 25°C")
    score_temp, temp_exp = calculate_temperature_similarity(t_temp, a_temp)
    weight_temp = w.get("temperature", 0.15)
    weighted_temp = score_temp * weight_temp
    weighted_total += weighted_temp
    feature_results["temperature"] = {
        "score": score_temp,
        "weight_percent": weight_temp * 100.0,
        "weighted_score": round(weighted_temp, 2),
        "target_value": t_temp,
        "analog_value": a_temp,
        "explanation": temp_exp
    }

    # 4. Geology Comparison (20%)
    t_geology = target.get("geology", target.get("key_traits", ""))
    if isinstance(t_geology, list):
        t_geology = ", ".join(t_geology)
    a_geology = analog.get("geology", "")
    score_geology = round(calculate_token_similarity(t_geology, a_geology, "geology"), 1)
    weight_geology = w.get("geology", 0.20)
    weighted_geology = score_geology * weight_geology
    weighted_total += weighted_geology
    feature_results["geology"] = {
        "score": score_geology,
        "weight_percent": weight_geology * 100.0,
        "weighted_score": round(weighted_geology, 2),
        "target_value": t_geology,
        "analog_value": a_geology,
        "explanation": f"Mineralogical and lithological comparison: {a_geology[:60]}..."
    }

    # 5. Aridity Comparison (15%)
    t_aridity = target.get("aridity", "Vacuum desiccated hyper-arid")
    a_aridity = analog.get("aridity", "Arid")
    score_aridity = round(calculate_token_similarity(t_aridity, a_aridity, "aridity"), 1)
    weight_aridity = w.get("aridity", 0.15)
    weighted_aridity = score_aridity * weight_aridity
    weighted_total += weighted_aridity
    feature_results["aridity"] = {
        "score": score_aridity,
        "weight_percent": weight_aridity * 100.0,
        "weighted_score": round(weighted_aridity, 2),
        "target_value": t_aridity,
        "analog_value": a_aridity,
        "explanation": f"Desiccation and water absence alignment: {a_aridity}"
    }

    # 6. Surface Conditions Comparison (10%)
    t_surface = target.get("surface_conditions", ", ".join(target.get("key_traits", [])))
    a_surface = analog.get("surface_conditions", "")
    score_surface = round(calculate_token_similarity(t_surface, a_surface, "surface_conditions"), 1)
    weight_surface = w.get("surface_conditions", 0.10)
    weighted_surface = score_surface * weight_surface
    weighted_total += weighted_surface
    feature_results["surface_conditions"] = {
        "score": score_surface,
        "weight_percent": weight_surface * 100.0,
        "weighted_score": round(weighted_surface, 2),
        "target_value": t_surface,
        "analog_value": a_surface,
        "explanation": f"Regolith, dust, and obstacle consistency: {a_surface[:60]}..."
    }

    # Ensure final score is neatly clamped 0 - 100
    final_score = round(max(0.0, min(100.0, weighted_total)), 1)

    # Narrative explanation specifically formatted as: "These environments are similar because..."
    top_features = sorted(feature_results.items(), key=lambda kv: kv[1]["score"], reverse=True)
    best_feat_name, best_feat = top_features[0]
    second_feat_name, second_feat = top_features[1]

    synthesis_reasons = []
    if "terrain" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("they share analogous landforms and topographical obstacles")
    if "geology" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("their unweathered basaltic or mineral compositions mirror one another")
    if "temperature" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("they experience extreme cold or severe thermal cycling")
    if "aridity" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("both environments exhibit extreme desiccation and negligible liquid water")
    if "slope" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("their incline profiles provide comparable traction and mobility challenges")
    if "surface_conditions" in [best_feat_name, second_feat_name]:
        synthesis_reasons.append("surface regolith and dust dynamics impose similar hardware stresses")

    if not synthesis_reasons:
        synthesis_reasons.append("they present comparable environmental stress and operational field challenges")

    reason_phrase = " and ".join(synthesis_reasons)
    clean_analog_exp = analog.get('explanation', '').replace('DEMO DATA: ', '')

    explanation = (
        f"These environments are similar because {reason_phrase}, with highest alignment in "
        f"{best_feat_name.replace('_', ' ')} ({best_feat['score']:.0f}%) and "
        f"{second_feat_name.replace('_', ' ')} ({second_feat['score']:.0f}%). "
        f"{clean_analog_exp}"
    )

    return AnalogComparisonResult(
        earth_analog_id=analog.get("id", ""),
        earth_analog_name=analog.get("name", ""),
        target_id=target.get("id", ""),
        target_name=target.get("name", ""),
        overall_analog_score=final_score,
        feature_scores=feature_results,
        explanation=explanation,
        weights_used=w
    )
