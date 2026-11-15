from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Coordinates(BaseModel):
    lat: float
    lon: float

class TargetFeatures(BaseModel):
    terrain: Optional[str] = Field(None, description="Terrain morphology, e.g. Impact crater, basaltic plain")
    slope: Optional[str] = Field(None, description="Slope inclination profile, e.g. 5° - 25°")
    temperature: Optional[str] = Field(None, description="Thermal range, e.g. -233°C to -53°C")
    geology: Optional[str] = Field(None, description="Lithology and mineralogy, e.g. Anorthosite, breccia")
    aridity: Optional[str] = Field(None, description="Desiccation level, e.g. Vacuum hyper-arid")
    surface_conditions: Optional[str] = Field(None, description="Surface regolith/dust characteristics")

class PlanetaryTarget(BaseModel):
    id: str
    body: str
    name: str
    region: str
    coordinates: Optional[Coordinates] = None
    terrain: Optional[str] = None
    terrain_type: Optional[str] = None
    slope: Optional[str] = None
    temperature: Optional[str] = None
    temperature_range: Optional[str] = None
    geology: Optional[str] = None
    aridity: Optional[str] = None
    surface_conditions: Optional[str] = None
    radiation_level: Optional[str] = None
    volatiles: Optional[str] = None
    sunlight: Optional[str] = None
    key_traits: Optional[List[str]] = None

class EarthAnalog(BaseModel):
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    terrain: str
    slope: str
    temperature: str
    geology: str
    aridity: str
    surface_conditions: str
    analog_score: float = Field(..., ge=0.0, le=100.0)
    recommended_missions: List[str]
    explanation: str
    dataset_type: Optional[str] = "prototype_demo_data"

class FeatureScoreDetail(BaseModel):
    score: float
    weight_percent: float
    weighted_score: float
    target_value: str
    analog_value: str
    explanation: str

class MatchExplanation(BaseModel):
    category: str
    score: float
    details: str

class MLKNNDetail(BaseModel):
    ml_rank: int
    knn_similarity_score: float
    knn_euclidean_distance: float
    cosine_similarity_score: float
    target_vector_profile: Optional[Dict[str, float]] = None
    analog_vector_profile: Optional[Dict[str, float]] = None
    model_name: str = "K-Nearest Neighbors (KNN Euclidean & Cosine Space)"
    habitability_disclaimer: str = "Statistical proximity in normalized environmental feature space. Not a prediction of biological habitability."

class MissionRecommendationDetail(BaseModel):
    mission_category: str = Field(..., description="Target operational category, e.g. Rover testing")
    suitability_statement: str = Field(..., description="Compliant forward-looking statement e.g. Potentially useful for...")
    data_grounded_reasons: List[str] = Field(..., description="Concrete reasons derived strictly from physical features")
    is_selected_mission: bool = False
    primary_metric: Optional[str] = None
    disclaimer: Optional[str] = None

class AnalogMatchResult(BaseModel):
    rank: Optional[int] = None
    earth_analog: EarthAnalog
    similarity_score: float = Field(..., ge=0.0, le=100.0)
    primary_reasons: Optional[List[str]] = None
    breakdown: Optional[List[MatchExplanation]] = None
    feature_scores: Dict[str, FeatureScoreDetail]
    ml_knn_metrics: Optional[MLKNNDetail] = None
    explanation: str
    why_points: Optional[List[str]] = Field(default_factory=list, description="Verified checkmark reasons based strictly on feature values")
    recommended_missions: List[str]
    mission_applications: Optional[List[str]] = None
    mission_recommendations: Optional[List[MissionRecommendationDetail]] = Field(default_factory=list, description="Structured 6-category mission recommendations")

# Request / Response Models for API endpoints
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dataset_records: int
    model_type: str

class AnalyzeRequest(BaseModel):
    planet: str = Field(..., description="Target planetary body: Moon or Mars")
    target_region: str = Field(..., description="Target candidate region name or ID")
    target_features: Optional[TargetFeatures] = Field(None, description="Optional custom feature overrides")
    mission_type: Optional[str] = Field("Rover testing", description="Mission objective focus")

class AnalyzeResponse(BaseModel):
    planet: str
    target_region: str
    mission_type: str
    overall_analog_score: float
    top_analog: AnalogMatchResult
    top_matches: List[AnalogMatchResult]
    feature_level_scores: Dict[str, FeatureScoreDetail]
    explanation: str
    recommended_mission_applications: List[str]
    mission_recommendations: Optional[List[MissionRecommendationDetail]] = Field(default_factory=list, description="Top analog classified mission applications")
    metadata: Dict[str, Any]

class CompareRequest(BaseModel):
    planet: str = Field(..., description="Target planetary body: Moon or Mars")
    target_region: str = Field(..., description="Target candidate region name or ID")
    earth_analog_id: str = Field(..., description="ID of the Earth analog location to compare against")
    target_features: Optional[TargetFeatures] = Field(None, description="Optional custom feature overrides")
    mission_type: Optional[str] = Field("Rover testing", description="Mission objective focus")

class CompareResponse(BaseModel):
    planet: str
    target_region: str
    earth_analog: EarthAnalog
    overall_analog_score: float
    feature_comparisons: Dict[str, FeatureScoreDetail]
    explanation: str
    recommended_missions: List[str]
    mission_recommendations: Optional[List[MissionRecommendationDetail]] = Field(default_factory=list, description="Classified mission applications")
    model_type: str = "Prototype Multi-Feature Similarity Model (Demo Only)"

class AnalysisResponse(BaseModel):
    target: PlanetaryTarget
    matches: List[AnalogMatchResult]
    metadata: Dict[str, Any]
