"""
Mission Recommendation Engine for MoonBase Planner
===================================================
Classifies Earth analog locations and planetary targets into 6 core space mission operational categories:
1. Rover testing
2. Astronaut field training
3. Equipment testing
4. Geological research
5. Navigation testing
6. Surface operations

CRITICAL GUARDRAIL COMPLIANCE:
- Do NOT claim that any location is officially approved, certified, or designated by NASA or any space agency.
- Strictly use sanctioned forward-looking and evaluative wording:
    * "Potentially useful for..."
    * "Could support..."
    * "Suitable for prototype testing based on the selected criteria."
- All recommendation rationales are grounded strictly in available physical parameters
  (terrain morphology, slope, thermal range, lithology/mineralogy, aridity, surface conditions).
"""

from typing import Dict, Any, List, Optional
import re

# Approved mission categories
MISSION_CATEGORIES = [
    "Rover testing",
    "Astronaut field training",
    "Equipment testing",
    "Geological research",
    "Navigation testing",
    "Surface operations"
]

NON_AGENCY_DISCLAIMER = (
    "Recommendations are generated algorithmically based on physical environmental metrics. "
    "This does not represent official certification, endorsement, or operational approval by NASA, ESA, or any space agency."
)

def _extract_numbers(text: str) -> List[float]:
    """Helper to extract integer or float numbers from strings."""
    if not text:
        return []
    matches = re.findall(r"[-+]?\d*\.?\d+", text)
    return [float(m) for m in matches if m]

def evaluate_rover_testing(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Rover Testing:
    Grounding: Steep or variable slopes, ruggedness index, boulders/rocks, loose regolith, fine dust.
    """
    reasons = []
    slope_str = str(analog.get("slope", "")).lower()
    surface_str = str(analog.get("surface_conditions", "")).lower()
    terrain_str = str(analog.get("terrain", "")).lower()

    # Slope / Ruggedness check
    slope_vals = _extract_numbers(slope_str)
    max_slope = max(slope_vals) if slope_vals else (processed_data.get("raw_physical_metrics", {}).get("slope_max_deg", 0) if processed_data else 0)
    if max_slope >= 15:
        reasons.append(f"Slope gradients up to {max_slope:.0f}° provide realistic high-angle wheel slip and chassis tilt challenges.")
    elif max_slope > 0:
        reasons.append(f"Low-to-moderate grade terrain ({max_slope:.0f}°) allows sustained rover endurance driving and wheel traction trials.")

    # Surface mobility check
    if any(k in surface_str for k in ["dust", "sand", "regolith", "lag", "gravel", "cinder", "tephra", "dunes", "scree"]):
        reasons.append(f"Surface substrate featuring {surface_str.split(',')[0]} replicates extraterrestrial wheel sinkage and abrasive mobility conditions.")

    if any(k in terrain_str for k in ["boulder", "crater", "lava", "volcanic", "dune", "salar"]):
        reasons.append(f"Topography with {terrain_str.split(',')[0]} tests obstacle avoidance sensors, autonomous hazard bypass, and rover suspension.")

    if not reasons:
        reasons.append("Terrain profile offers unobstructed ground tracks for prototype drivetrain calibration.")

    return {
        "category": "Rover testing",
        "suitability_statement": "Potentially useful for rover chassis durability, traction modeling, and autonomous mobility trials.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Topographic Ruggedness & Substrate Mechanical Properties"
    }

def evaluate_astronaut_field_training(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Astronaut Field Training:
    Grounding: Expansive terrain, geological exploration complexity, EVA suit ergonomic challenge, isolated planetary analogs.
    """
    reasons = []
    terrain_str = str(analog.get("terrain", "")).lower()
    geo_str = str(analog.get("geology", "")).lower()
    temp_str = str(analog.get("temperature", "")).lower()

    if any(k in terrain_str for k in ["crater", "valley", "plateau", "caldera", "desert", "tube", "glacier"]):
        reasons.append(f"Expansive landscape of {terrain_str.split('(')[0].strip()} mimics macroscopic field traverses and spatial scale during simulated EVAs.")

    if any(k in geo_str for k in ["breccia", "basalt", "pyroclastic", "permafrost", "carbonate", "evaporite", "dolerite", "ignimbrite"]):
        reasons.append(f"Exposed {geo_str.split(',')[0]} provides realistic field sampling targets for training crew in planetary science identification.")

    if any(k in temp_str for k in ["-", "sub-zero", "freezing", "polar", "extreme"]):
        reasons.append("Environmental thermal stress tests crew endurance, suit dexterity, and life-support logistics in adverse conditions.")

    if not reasons:
        reasons.append("Isolated geography offers high-fidelity planetary expedition simulation conditions.")

    return {
        "category": "Astronaut field training",
        "suitability_statement": "Could support extravehicular activity (EVA) simulation, pressurized suit mobility, and crew field-science drills.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Geological Diversity & EVA Traversal Complexity"
    }

def evaluate_equipment_testing(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Equipment Testing:
    Grounding: Thermal extremes (cryogenic/high heat), fine abrasive dust, desiccation, UV, drill substrate resistance.
    """
    reasons = []
    temp_str = str(analog.get("temperature", "")).lower()
    surface_str = str(analog.get("surface_conditions", "")).lower()
    aridity_str = str(analog.get("aridity", "")).lower()

    # Thermal stress
    if any(k in temp_str for k in ["-50", "-40", "-20", "-10", "sub-zero", "cryogenic"]):
        reasons.append(f"Sub-zero thermal range ({analog.get('temperature')}) stresses battery chemistry, seals, lubricants, and cryogenic mechanisms.")
    elif any(k in temp_str for k in ["35", "40", "45", "50", "diurnal"]):
        reasons.append(f"Extreme diurnal thermal swings ({analog.get('temperature')}) test component expansion, contraction, and radiative heatsinks.")

    # Dust & regolith abrasion
    if any(k in surface_str for k in ["dust", "perchlorate", "fine", "abrasive", "salt", "ash", "silica"]):
        reasons.append(f"Surface environment with {surface_str.split(',')[0]} challenges mechanical joint seals, optical lenses, and solar array dust accumulation.")

    # Desiccation
    if any(k in aridity_str for k in ["hyper-arid", "arid", "<1", "<10", "<5"]):
        reasons.append("Severe atmospheric desiccation provides an environment to assess material moisture outgassing and sensor drift.")

    if not reasons:
        reasons.append("Harsh ambient conditions permit stress-testing payload structural enclosures.")

    return {
        "category": "Equipment testing",
        "suitability_statement": "Suitable for prototype testing based on the selected criteria of thermal extremes, dust intrusion, and mechanical endurance.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Thermal Range, Dust Abrasion & Atmospheric Aridity"
    }

def evaluate_geological_research(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Geological Research:
    Grounding: Lithology, impact melt rocks, unweathered basalts, clays, carbonates, hydrothermal deposits, permafrost.
    """
    reasons = []
    geo_str = str(analog.get("geology", "")).lower()
    terrain_str = str(analog.get("terrain", "")).lower()

    if any(k in geo_str for k in ["impact", "breccia", "melt", "shatter"]):
        reasons.append(f"Impact cratering lithology ({analog.get('geology').split(',')[0]}) offers an analog for lunar and martian impact shock metamorphism.")
    elif any(k in geo_str for k in ["basalt", "tholeiitic", "lava", "volcanic"]):
        reasons.append(f"Mafic volcanic bedrock ({analog.get('geology').split(',')[0]}) mirrors planetary flood basalts and lunar mare lava flows.")
    elif any(k in geo_str for k in ["perchlorate", "evaporite", "clay", "sulfate", "carbonate"]):
        reasons.append(f"Mineral assemblages with {geo_str.split(',')[0]} represent chemical precipitates analogous to ancient martian lacustrine basins.")

    if any(k in terrain_str for k in ["permafrost", "ice", "polar", "patterned"]):
        reasons.append("Cryogenic and permafrost structures provide physical models for ground ice preservation and volatile sequestration.")

    if not reasons:
        reasons.append("Bedrock exposures allow in-situ geochemical spectrometry and petrographic field comparisons.")

    return {
        "category": "Geological research",
        "suitability_statement": "Could support comparative planetology, spectroscopic instrument calibration, and sample return protocol development.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Lithology & Mineralogical Parallels"
    }

def evaluate_navigation_testing(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Navigation Testing:
    Grounding: Visual feature density, high-contrast or repetitive landscapes, low sun elevation shadows, GPS-denied environments (lava tubes).
    """
    reasons = []
    terrain_str = str(analog.get("terrain", "")).lower()
    slope_str = str(analog.get("slope", "")).lower()

    if any(k in terrain_str for k in ["tube", "cave", "subsurface"]):
        reasons.append("Subterranean lava tube structures provide a rigorous GPS-denied environment for LiDAR SLAM and autonomous underground mapping.")
    elif any(k in terrain_str for k in ["polar", "ice", "crater"]):
        reasons.append("High-latitude low-incident solar angles create extreme shadow elongation for testing visual odometry and crater-relative navigation.")
    elif any(k in terrain_str for k in ["desert", "dune", "salar", "plain", "flat"]):
        reasons.append("Low-texture or repetitive landscape geometries challenge optical flow algorithms and require robust celestial or inertial navigation.")
    else:
        reasons.append("Topographic relief provides recognizable visual horizons for testing landmark triangulation and orbital-to-ground image registration.")

    if any(k in slope_str for k in ["steep", "20", "25", "30", "wall"]):
        reasons.append(f"Steep elevation drops ({analog.get('slope')}) provide 3D depth-map calibration for hazard detection sensors.")

    return {
        "category": "Navigation testing",
        "suitability_statement": "Potentially useful for visual odometry, optical navigation algorithms, LiDAR SLAM, and terrain-relative localization.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Optical Contrast, Visual Texture & Sensor SLAM Performance"
    }

def evaluate_surface_operations(analog: Dict[str, Any], target: Dict[str, Any], processed_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates suitability for Surface Operations:
    Grounding: Habitat siting, communication line-of-sight, resource extraction drills, logistics in remote hyper-isolated conditions.
    """
    reasons = []
    terrain_str = str(analog.get("terrain", "")).lower()
    aridity_str = str(analog.get("aridity", "")).lower()
    surface_str = str(analog.get("surface_conditions", "")).lower()

    if any(k in terrain_str for k in ["plain", "plateau", "basin", "salar", "floor"]):
        reasons.append(f"Relatively planar zones ({terrain_str.split('(')[0].strip()}) provide viable ground footprint for prototype inflatable habitat and solar array deployment.")

    if any(k in surface_str for k in ["permafrost", "salt", "dust", "regolith"]):
        reasons.append(f"Surface materials ({surface_str.split(',')[0]}) allow evaluating In-Situ Resource Utilization (ISRU) regolith bagging and berm construction.")

    if any(k in aridity_str for k in ["hyper-arid", "polar", "desert"]):
        reasons.append("Extreme remoteness and environmental hostility simulate operational communication latency, power budget constraints, and autonomous logistics.")

    if not reasons:
        reasons.append("Remote outpost geography models long-duration isolated surface expedition protocols.")

    return {
        "category": "Surface operations",
        "suitability_statement": "Suitable for prototype testing based on the selected criteria of habitat deployment, ISRU modeling, and isolated operational logistics.",
        "data_grounded_reasons": reasons,
        "primary_metric": "Basecamp Siting Feasibility & Autonomous Logistics Dynamics"
    }


def generate_mission_recommendations(
    analog: Dict[str, Any],
    target: Dict[str, Any],
    selected_mission_type: str = "Rover testing",
    processed_analogs: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Generates structured recommendations for all 6 mission categories for a given analog location.
    Prioritizes the selected mission type at the top of the list, followed by other categories.
    Each item strictly contains:
      - mission_category
      - suitability_statement (using approved non-agency wording)
      - data_grounded_reasons (derived strictly from physical parameters)
      - is_selected_mission (boolean flag)
      - primary_metric
    """
    # Find matching processed data if available
    proc_data = None
    if processed_analogs:
        for p in processed_analogs:
            if p.get("id") == analog.get("id"):
                proc_data = p
                break

    evaluators = [
        evaluate_rover_testing,
        evaluate_astronaut_field_training,
        evaluate_equipment_testing,
        evaluate_geological_research,
        evaluate_navigation_testing,
        evaluate_surface_operations
    ]

    all_recommendations = []
    selected_norm = (selected_mission_type or "").strip().lower()

    for eval_fn in evaluators:
        rec = eval_fn(analog, target, proc_data)
        cat_name = rec["category"]
        is_sel = (cat_name.lower() in selected_norm) or (selected_norm in cat_name.lower())
        
        # Package in standardized schema structure
        all_recommendations.append({
            "mission_category": cat_name,
            "suitability_statement": rec["suitability_statement"],
            "data_grounded_reasons": rec["data_grounded_reasons"],
            "is_selected_mission": is_sel,
            "primary_metric": rec["primary_metric"],
            "disclaimer": NON_AGENCY_DISCLAIMER
        })

    # Sort so the user's selected mission type appears first, followed by others
    all_recommendations.sort(key=lambda r: 0 if r["is_selected_mission"] else 1)

    return all_recommendations
