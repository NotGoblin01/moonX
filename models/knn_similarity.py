"""
Machine Learning & Environmental Vector Similarity Component
============================================================
Implements a multi-dimensional K-Nearest Neighbors (KNN) and Cosine Vector
similarity engine using Scikit-Learn and NumPy over processed planetary features.

Features compared in normalized Euclidean/Cosine space:
  - Normalized Slope [0, 1]
  - Normalized Terrain Ruggedness (TRI) [0, 1]
  - Normalized Min Temperature (Cryogenic/Cold limit) [0, 1]
  - Normalized Max Temperature [0, 1]
  - Normalized Aridity Index [0, 1]
  - Normalized Rock / Surface Roughness [0, 1]

DISCLAIMER:
This model identifies statistical and environmental analogs based strictly
on the selected physical features. It is NOT a prediction of biological habitability,
life-support viability, or human survivability.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

VECTOR_FEATURE_KEYS = [
    "norm_slope",
    "norm_ruggedness",
    "norm_temp_min",
    "norm_temp_max",
    "norm_aridity",
    "norm_rock_abundance"
]

class EnvironmentalKNNMatcher:
    def __init__(self, n_neighbors: int = 5, metric: str = "euclidean"):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.analogs_catalog: List[Dict[str, Any]] = []
        self.feature_matrix: np.ndarray = np.empty((0, len(VECTOR_FEATURE_KEYS)))
        self.model: Optional[NearestNeighbors] = None
        self._load_and_fit()

    def _load_and_fit(self):
        processed_file = DATA_DIR / "processed" / "earth_analogs_processed.json"
        if not processed_file.exists():
            return

        with open(processed_file, "r", encoding="utf-8") as f:
            self.analogs_catalog = json.load(f)

        if not self.analogs_catalog:
            return

        matrix = []
        for item in self.analogs_catalog:
            norm_feats = item.get("normalized_features", {})
            vec = [float(norm_feats.get(k, 0.5) or 0.5) for k in VECTOR_FEATURE_KEYS]
            matrix.append(vec)

        self.feature_matrix = np.array(matrix, dtype=np.float32)

        # Fit Scikit-Learn NearestNeighbors
        k = min(self.n_neighbors, len(self.analogs_catalog))
        self.model = NearestNeighbors(n_neighbors=k, metric=self.metric, algorithm="auto")
        self.model.fit(self.feature_matrix)

    def extract_vector(self, target_data: Dict[str, Any]) -> np.ndarray:
        """Extracts 6D normalized feature vector from a target dictionary."""
        norm_feats = target_data.get("normalized_features")
        if norm_feats:
            vec = [float(norm_feats.get(k, 0.5) or 0.5) for k in VECTOR_FEATURE_KEYS]
            return np.array(vec, dtype=np.float32).reshape(1, -1)

        # Fallback if raw target metrics are passed
        raw = target_data.get("raw_physical_metrics", {})
        slope = float(raw.get("slope_mean_deg", 10.0)) / 45.0
        tri = float(raw.get("terrain_ruggedness_index_m", 25.0)) / 120.0
        t_min = (float(raw.get("temperature_min_k", 200.0)) - 40.0) / 360.0
        t_max = (float(raw.get("temperature_max_k", 280.0)) - 40.0) / 360.0
        aridity = float(raw.get("aridity_index", 0.0)) / 0.65
        rock = float(raw.get("rock_abundance_fraction", 0.1)) / 0.35

        vec = [
            np.clip(slope, 0.0, 1.0),
            np.clip(tri, 0.0, 1.0),
            np.clip(t_min, 0.0, 1.0),
            np.clip(t_max, 0.0, 1.0),
            np.clip(aridity, 0.0, 1.0),
            np.clip(rock, 0.0, 1.0)
        ]
        return np.array(vec, dtype=np.float32).reshape(1, -1)

    def find_nearest_analogs(self, target_data: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the KNN model for closest Earth analogs in environmental feature space.
        Returns ranked analogs, Euclidean distances, and ML-derived similarity scores (0 - 100).
        """
        if self.model is None or len(self.analogs_catalog) == 0:
            self._load_and_fit()
            if self.model is None:
                return []

        target_vec = self.extract_vector(target_data)
        k = min(top_k, len(self.analogs_catalog))

        distances, indices = self.model.kneighbors(target_vec, n_neighbors=k)
        distances = distances[0]
        indices = indices[0]

        # In normalized 6D unit hypercube, max Euclidean distance between opposite corners is sqrt(6) ≈ 2.449
        max_dist = np.sqrt(len(VECTOR_FEATURE_KEYS))

        results = []
        for rank, (dist, idx) in enumerate(zip(distances, indices), start=1):
            analog = self.analogs_catalog[idx]
            analog_vec = self.feature_matrix[idx]

            # Invert Euclidean distance into similarity percentage [0, 100]
            # Exponential decay scaling gives smooth discrimination for close neighbors
            similarity_pct = round(float(np.exp(-1.5 * (dist / max_dist)) * 100.0), 1)

            # Cosine similarity validation
            cos_sim = float(
                np.dot(target_vec[0], analog_vec) / 
                (np.linalg.norm(target_vec[0]) * np.linalg.norm(analog_vec) + 1e-7)
            )
            cos_sim_pct = round(float(np.clip(cos_sim, 0.0, 1.0) * 100.0), 1)

            results.append({
                "ml_rank": rank,
                "analog_id": analog["id"],
                "analog_name": analog["name"],
                "country": analog["country"],
                "knn_euclidean_distance": round(float(dist), 4),
                "knn_similarity_score": similarity_pct,
                "cosine_similarity_score": cos_sim_pct,
                "target_vector_profile": {
                    k: round(float(target_vec[0][i]), 3) for i, k in enumerate(VECTOR_FEATURE_KEYS)
                },
                "analog_vector_profile": {
                    k: round(float(analog_vec[i]), 3) for i, k in enumerate(VECTOR_FEATURE_KEYS)
                },
                "disclaimer": "Identifies statistical proximity in normalized feature space. Not a prediction of biological habitability."
            })

        return results

# Singleton instance
_knn_instance: Optional[EnvironmentalKNNMatcher] = None

def get_knn_matcher() -> EnvironmentalKNNMatcher:
    global _knn_instance
    if _knn_instance is None:
        _knn_instance = EnvironmentalKNNMatcher(n_neighbors=10)
    return _knn_instance
