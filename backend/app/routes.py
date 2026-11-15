import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas import (
    HealthResponse,
    EarthAnalog,
    PlanetaryTarget,
    AnalyzeRequest,
    AnalyzeResponse,
    CompareRequest,
    CompareResponse,
    AnalysisResponse,
    AnalogMatchResult,
    FeatureScoreDetail
)
from models.similarity_model import (
    evaluate_analog_similarity,
    DEFAULT_ANALOG_WEIGHTS
)
from models.knn_similarity import get_knn_matcher, VECTOR_FEATURE_KEYS
from models.explanation_layer import generate_location_explanation_points
from models.mission_recommender import generate_mission_recommendations

router = APIRouter()

# Data loaders
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def load_json(subpath: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / subpath
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

EARTH_ANALOGS = load_json("earth_analogs.json")
PLANETARY_TARGETS = load_json("planetary_targets.json")
PROCESSED_EARTH_ANALOGS = load_json("processed/earth_analogs_processed.json")
PROCESSED_PLANETARY_TARGETS = load_json("processed/planetary_targets_processed.json")
PROVENANCE_MANIFEST = load_json("metadata/data_provenance_manifest.json")

# ==========================================
# GET /api/provenance
# ==========================================
@router.get("/provenance")
def get_dataset_provenance():
    """Retrieve official space agency provenance, instruments, and measurement units."""
    manifest_path = DATA_DIR / "metadata" / "data_sources_manifest.json"
    if not manifest_path.exists():
        manifest_path = DATA_DIR / "metadata" / "data_provenance_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "Metadata manifest missing"}

# ==========================================
# GET /api/data-sources
# ==========================================
@router.get("/data-sources")
def get_official_data_sources():
    """Retrieve structured list of official external NASA, USGS, ESA, and open scientific datasets."""
    sources_path = DATA_DIR / "metadata" / "data_sources_manifest.json"
    if sources_path.exists():
        with open(sources_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"datasets": []}

# ==========================================
# GET /api/processed-analogs
# ==========================================
@router.get("/processed-analogs")
def get_processed_earth_analogs():
    """Retrieve normalized real space-agency processed Earth analog records."""
    return PROCESSED_EARTH_ANALOGS

def find_target_by_identifier(planet: str, identifier: str) -> Dict[str, Any]:
    """Finds a planetary target by exact id or fuzzy name match."""
    norm_id = identifier.strip().lower()
    norm_planet = planet.strip().lower()

    # Match by ID or exact name on same planet
    for t in PLANETARY_TARGETS:
        if t["body"].lower() == norm_planet:
            if t["id"].lower() == norm_id or t["name"].lower() == norm_id:
                return t

    # Substring match
    for t in PLANETARY_TARGETS:
        if t["body"].lower() == norm_planet:
            if norm_id in t["id"].lower() or norm_id in t["name"].lower():
                return t

    # Fallback to any matching target
    for t in PLANETARY_TARGETS:
        if t["id"].lower() == norm_id or norm_id in t["name"].lower():
            return t

    return None

# ==========================================
# 1. GET /api/health
# ==========================================
@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint confirming API service and dataset status."""
    return {
        "status": "healthy",
        "service": "MoonBase Planner — Planetary Analog Finder API",
        "version": "0.1.0",
        "dataset_records": len(EARTH_ANALOGS),
        "model_type": "Prototype Weighted Multi-Feature Similarity Model (Demo Only)"
    }

# ==========================================
# 2. GET /api/earth-analogs
# ==========================================
@router.get("/earth-analogs", response_model=List[EarthAnalog])
def get_all_earth_analogs():
    """Retrieve full catalog of Earth analog locations."""
    return EARTH_ANALOGS

# ==========================================
# 3. GET /api/earth-analogs/{id}
# ==========================================
@router.get("/earth-analogs/{id}", response_model=EarthAnalog)
def get_earth_analog_by_id(id: str):
    """Retrieve a specific Earth analog location by ID."""
    for analog in EARTH_ANALOGS:
        if analog["id"].lower() == id.lower():
            return analog
    raise HTTPException(status_code=404, detail=f"Earth analog '{id}' not found.")

# ==========================================
# 4. POST /api/analyze
# ==========================================
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_planetary_target(request: AnalyzeRequest):
    """
    Accepts:
      planet, target_region, target_features, mission_type
    
    Workflow:
      1. Load Earth analog data
      2. Compare target characteristics
      3. Calculate similarity scores
      4. Rank Earth locations
      5. Return top matching locations
      6. Return feature-level scores
      7. Return explanations
      8. Return recommended mission applications
    """
    # 1. Resolve or construct planetary target
    base_target = find_target_by_identifier(request.planet, request.target_region)
    if not base_target:
        # Construct synthetic target if not in demo seed
        base_target = {
            "id": request.target_region.lower().replace(" ", "-"),
            "body": request.planet.capitalize(),
            "name": request.target_region,
            "region": "Custom Analysis Target",
            "terrain": "Unclassified planetary terrain",
            "slope": "5° - 20°",
            "temperature": "-100°C to 20°C",
            "geology": "Basaltic regolith and silicates",
            "aridity": "Vacuum hyper-arid",
            "surface_conditions": "Fine regolith dust and boulder fragments"
        }
    else:
        base_target = dict(base_target)

    # Apply any custom feature overrides from request.target_features
    if request.target_features:
        f = request.target_features
        if f.terrain: base_target["terrain"] = f.terrain
        if f.slope: base_target["slope"] = f.slope
        if f.temperature: base_target["temperature"] = f.temperature
        if f.geology: base_target["geology"] = f.geology
        if f.aridity: base_target["aridity"] = f.aridity
        if f.surface_conditions: base_target["surface_conditions"] = f.surface_conditions

    # 2 & 3. Compare characteristics and calculate scores using modular similarity model
    # Also evaluate via Machine Learning K-Nearest Neighbors (KNN) in normalized 6D space
    knn_matcher = get_knn_matcher()
    knn_results_map = {}
    try:
        knn_matches = knn_matcher.find_nearest_analogs(base_target, top_k=len(EARTH_ANALOGS))
        knn_results_map = {m["analog_id"]: m for m in knn_matches}
    except Exception as e:
        print("KNN matcher warning:", e)

    ranked_results: List[AnalogMatchResult] = []
    for analog in EARTH_ANALOGS:
        sim_res = evaluate_analog_similarity(base_target, analog, DEFAULT_ANALOG_WEIGHTS)

        # Convert feature score dictionaries to schema models
        feature_dict = {
            k: FeatureScoreDetail(**v) for k, v in sim_res.feature_scores.items()
        }

        # Attach ML KNN vector metrics if available
        knn_meta = knn_results_map.get(analog["id"])

        # Generate concise explanation bullet points based strictly on feature values
        why_bullets = generate_location_explanation_points(
            sim_res.feature_scores,
            mission_type=request.mission_type,
            analog_missions=analog.get("recommended_missions", [])
        )

        # Generate 6-category structured mission recommendations
        mission_recs = generate_mission_recommendations(
            analog=analog,
            target=base_target,
            selected_mission_type=request.mission_type,
            processed_analogs=PROCESSED_EARTH_ANALOGS
        )

        match_item = AnalogMatchResult(
            rank=0,
            earth_analog=EarthAnalog(**analog),
            similarity_score=sim_res.overall_analog_score,
            feature_scores=feature_dict,
            ml_knn_metrics=knn_meta,
            explanation=sim_res.explanation,
            why_points=why_bullets,
            recommended_missions=analog.get("recommended_missions", ["General Mission Simulation"]),
            mission_applications=analog.get("recommended_missions", ["General Mission Simulation"]),
            mission_recommendations=mission_recs
        )
        ranked_results.append(match_item)

    # 4. Rank Earth locations descending by score
    ranked_results.sort(key=lambda m: m.similarity_score, reverse=True)
    for idx, item in enumerate(ranked_results):
        item.rank = idx + 1

    top_match = ranked_results[0]

    return AnalyzeResponse(
        planet=base_target["body"],
        target_region=base_target["name"],
        mission_type=request.mission_type,
        overall_analog_score=top_match.similarity_score,
        top_analog=top_match,
        top_matches=ranked_results[:6], # Top matching locations
        feature_level_scores=top_match.feature_scores,
        explanation=top_match.explanation,
        recommended_mission_applications=top_match.recommended_missions,
        mission_recommendations=top_match.mission_recommendations,
        metadata={
            "weights": DEFAULT_ANALOG_WEIGHTS,
            "total_analogs_compared": len(EARTH_ANALOGS),
            "scoring_models": {
                "feature_weighted_model": "Multi-Feature Normalized Weighted Model (Terrain, Slope, Temp, Geology, Aridity, Surface)",
                "ml_similarity_model": "K-Nearest Neighbors (KNN Euclidean & Cosine Distance over 6D Normalized Space)"
            },
            "disclaimer": "Models identify statistical and environmental analogs based on physical parameters. NOT a prediction of biological habitability."
        }
    )

# ==========================================
# 5. POST /api/compare
# ==========================================
@router.post("/compare", response_model=CompareResponse)
def compare_target_with_analog(request: CompareRequest):
    """
    Directly compares a target region with a specific Earth analog location.
    Returns 6 feature comparisons, overall analog score, explanation, and recommended missions.
    """
    # Find analog
    analog = None
    for a in EARTH_ANALOGS:
        if a["id"].lower() == request.earth_analog_id.lower():
            analog = a
            break
    if not analog:
        raise HTTPException(status_code=404, detail=f"Earth analog '{request.earth_analog_id}' not found.")

    # Find target
    base_target = find_target_by_identifier(request.planet, request.target_region)
    if not base_target:
        base_target = {
            "id": request.target_region.lower().replace(" ", "-"),
            "body": request.planet.capitalize(),
            "name": request.target_region,
            "region": "Custom Analysis Target",
            "terrain": "Unclassified planetary terrain",
            "slope": "5° - 20°",
            "temperature": "-100°C to 20°C",
            "geology": "Basaltic regolith and silicates",
            "aridity": "Vacuum hyper-arid",
            "surface_conditions": "Fine regolith dust and boulder fragments"
        }
    else:
        base_target = dict(base_target)

    # Apply custom overrides
    if request.target_features:
        f = request.target_features
        if f.terrain: base_target["terrain"] = f.terrain
        if f.slope: base_target["slope"] = f.slope
        if f.temperature: base_target["temperature"] = f.temperature
        if f.geology: base_target["geology"] = f.geology
        if f.aridity: base_target["aridity"] = f.aridity
        if f.surface_conditions: base_target["surface_conditions"] = f.surface_conditions

    sim_res = evaluate_analog_similarity(base_target, analog, DEFAULT_ANALOG_WEIGHTS)
    feature_dict = {
        k: FeatureScoreDetail(**v) for k, v in sim_res.feature_scores.items()
    }

    mission_recs = generate_mission_recommendations(
        analog=analog,
        target=base_target,
        selected_mission_type=request.mission_type,
        processed_analogs=PROCESSED_EARTH_ANALOGS
    )

    return CompareResponse(
        planet=base_target["body"],
        target_region=base_target["name"],
        earth_analog=EarthAnalog(**analog),
        overall_analog_score=sim_res.overall_analog_score,
        feature_comparisons=feature_dict,
        explanation=sim_res.explanation,
        recommended_missions=analog.get("recommended_missions", ["General Surface Operations"]),
        mission_recommendations=mission_recs
    )

# Retain existing GET helper routes for frontend backwards compatibility
@router.get("/targets", response_model=List[PlanetaryTarget])
def get_all_targets(body: Optional[str] = None):
    if body and isinstance(body, str):
        return [t for t in PLANETARY_TARGETS if t["body"].lower() == body.lower()]
    return PLANETARY_TARGETS

@router.get("/targets/{target_id}", response_model=PlanetaryTarget)
def get_target(target_id: str):
    for t in PLANETARY_TARGETS:
        if t["id"] == target_id:
            return t
    raise HTTPException(status_code=404, detail=f"Target '{target_id}' not found.")

@router.get("/analogs", response_model=List[EarthAnalog])
def get_analogs_alias():
    return EARTH_ANALOGS

@router.get("/analogs/{analog_id}", response_model=EarthAnalog)
def get_analog_alias(analog_id: str):
    return get_earth_analog_by_id(analog_id)

@router.get("/analyze/{target_id}")
def analyze_target_get_alias(target_id: str, mission_type: Optional[str] = Query(None)):
    target = None
    for t in PLANETARY_TARGETS:
        if t["id"] == target_id:
            target = t
            break
    if not target:
        raise HTTPException(status_code=404, detail=f"Target '{target_id}' not found.")

    req = AnalyzeRequest(
        planet=target["body"],
        target_region=target["id"],
        mission_type=mission_type or "Rover testing"
    )
    post_res = analyze_planetary_target(req)
    
    # Return structure matching frontend explorer expectation
    return {
        "target": target,
        "matches": [m.dict() for m in post_res.top_matches],
        "metadata": post_res.metadata
    }
