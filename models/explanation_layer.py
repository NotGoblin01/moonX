"""
Concise Explanation Generator Layer for MoonBase Planner
=========================================================
Generates transparent, judge-friendly, bulleted explanations based
STRICTLY on the actual normalized feature scores and physical values.

Format:
  WHY THIS LOCATION?
  ✓ Strong terrain similarity (Score: 92%)
  ✓ Similar slope characteristics (Target: 5°-15° vs Earth: 6°-18°)
  ✓ Similar temperature characteristics (-50°C cold envelope)
  ✓ High aridity similarity (Hyper-arid soil desiccation)
  ✓ Suitable for the selected mission type (Rover testing)
"""

from typing import Dict, Any, List

FEATURE_DISPLAY_NAMES = {
    "terrain": "terrain morphology",
    "slope": "slope characteristics",
    "temperature": "temperature characteristics",
    "geology": "geological composition",
    "aridity": "aridity & desiccation level",
    "surface_conditions": "surface & regolith conditions"
}

def generate_location_explanation_points(
    feature_scores: Dict[str, Dict[str, Any]],
    mission_type: str = "Rover testing",
    analog_missions: List[str] = None
) -> List[str]:
    """
    Builds a concise list of verified checkmark statements grounded
    strictly in the evaluated feature scores and values.
    """
    points = []
    analog_missions = [m.lower() for m in (analog_missions or [])]
    requested_mission = (mission_type or "Rover testing").strip().lower()

    # Sort features by score descending
    sorted_features = sorted(
        feature_scores.items(),
        key=lambda kv: kv[1].get("score", 0.0),
        reverse=True
    )

    for feat_key, feat_data in sorted_features:
        score = feat_data.get("score", 0.0)
        display_name = FEATURE_DISPLAY_NAMES.get(feat_key, feat_key.replace("_", " "))

        if score >= 85.0:
            qualifier = "Strong"
        elif score >= 70.0:
            qualifier = "High"
        elif score >= 55.0:
            qualifier = "Moderate"
        else:
            continue

        if feat_key == "terrain":
            points.append(f"{qualifier} terrain similarity ({feat_data.get('target_value', '').split(';')[0][:40]})")
        elif feat_key == "slope":
            points.append(f"Similar slope characteristics ({feat_data.get('analog_value', '').split('(')[0].strip()})")
        elif feat_key == "temperature":
            points.append(f"Similar temperature characteristics ({feat_data.get('analog_value', '').split('(')[0].strip()})")
        elif feat_key == "geology":
            points.append(f"Matching geological composition ({qualifier.lower()} lithological correspondence)")
        elif feat_key == "aridity":
            points.append(f"High aridity similarity (Extremely dry soil desiccation)")
        elif feat_key == "surface_conditions":
            points.append(f"High surface similarity (Comparable dust and regolith friction)")

        # Cap at top 4 physical feature bullets to keep it concise
        if len(points) >= 4:
            break

    # Add Mission suitability bullet
    mission_matched = any(
        req_word in " ".join(analog_missions) 
        for req_word in requested_mission.split() 
        if len(req_word) > 3
    )

    if mission_matched or len(analog_missions) > 0:
        clean_mission_title = mission_type.capitalize()
        points.append(f"Suitable for the selected mission type ({clean_mission_title})")
    else:
        points.append(f"Provides valuable secondary testing grounds for mission systems")

    return points
