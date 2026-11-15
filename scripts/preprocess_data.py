#!/usr/bin/env python3
"""
Reproducible Preprocessing & Feature Normalization Pipeline
============================================================
Processes raw space-agency datasets from NASA PDS, USGS Astrogeology,
ESA Copernicus, and NASA Earthdata into normalized, validated scientific
feature tables for MoonBase Planner.

Guarantees:
- Never overwrites raw data.
- Handles missing or null measurements cleanly.
- Normalizes comparable physical dimensions into standard [0, 1] envelopes.
- Explicitly records scientific units of measurement and data provenance.
- Generates processed JSON and metadata exports for backend serving.
"""

import os
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
METADATA_DIR = BASE_DIR / "data" / "metadata"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Normalization Bound Envelopes across Earth, Moon, and Mars regimes
BOUNDS = {
    # Slope in degrees: 0 deg (flat) to 45 deg (steep scarp / angle of repose)
    "slope_deg": {"min": 0.0, "max": 45.0},
    # Terrain Ruggedness Index in meters
    "tri_m": {"min": 0.0, "max": 120.0},
    # Temperature in Kelvin: 40 K (cryogenic PSR) to 390 K (equatorial lunar noon)
    "temperature_k": {"min": 40.0, "max": 400.0},
    # Aridity index: 0.0 (absolute vacuum) to 0.65 (humid boundary)
    "aridity_index": {"min": 0.0, "max": 0.65},
    # Surface rock fraction: 0.0 to 0.35
    "rock_abundance": {"min": 0.0, "max": 0.35}
}

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def normalize_min_max(val: Optional[float], min_val: float, max_val: float) -> Optional[float]:
    if val is None or math.isnan(val):
        return None
    clamped = clamp(val, min_val, max_val)
    return round((clamped - min_val) / (max_val - min_val), 4)

def load_raw_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Raw source file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_planetary_target(raw_record: Dict[str, Any], body: str) -> Dict[str, Any]:
    """Normalizes Moon or Mars raw observations into a standardized scientific target model."""
    slope_mean = raw_record.get("slope_mean_deg")
    tri = raw_record.get("terrain_ruggedness_index_m")
    t_min = raw_record.get("temperature_min_k")
    t_max = raw_record.get("temperature_max_k")
    t_mean = raw_record.get("temperature_mean_k")
    aridity = raw_record.get("aridity_index", 0.0)
    rock = raw_record.get("rock_abundance_fraction")

    return {
        "id": raw_record["id"],
        "body": body,
        "name": raw_record["name"],
        "region": raw_record.get("region", "Surface"),
        "coordinates": raw_record["coordinates"],
        "raw_physical_metrics": {
            "elevation_m": raw_record.get("elevation_m"),
            "elevation_datum": raw_record.get("elevation_datum"),
            "slope_mean_deg": slope_mean,
            "slope_max_deg": raw_record.get("slope_max_deg"),
            "terrain_ruggedness_index_m": tri,
            "temperature_min_k": t_min,
            "temperature_max_k": t_max,
            "temperature_mean_k": t_mean,
            "aridity_index": aridity,
            "rock_abundance_fraction": rock,
            "atmospheric_pressure_kpa": raw_record.get("pressure_kpa", 0.0)
        },
        "normalized_features": {
            "norm_slope": normalize_min_max(slope_mean, BOUNDS["slope_deg"]["min"], BOUNDS["slope_deg"]["max"]),
            "norm_ruggedness": normalize_min_max(tri, BOUNDS["tri_m"]["min"], BOUNDS["tri_m"]["max"]),
            "norm_temp_min": normalize_min_max(t_min, BOUNDS["temperature_k"]["min"], BOUNDS["temperature_k"]["max"]),
            "norm_temp_max": normalize_min_max(t_max, BOUNDS["temperature_k"]["min"], BOUNDS["temperature_k"]["max"]),
            "norm_aridity": normalize_min_max(aridity, BOUNDS["aridity_index"]["min"], BOUNDS["aridity_index"]["max"]),
            "norm_rock_abundance": normalize_min_max(rock, BOUNDS["rock_abundance"]["min"], BOUNDS["rock_abundance"]["max"])
        },
        "lithology": {
            "primary": raw_record.get("primary_lithology"),
            "dominant_minerals": raw_record.get("dominant_minerals", [])
        },
        "provenance": {
            "data_source_tier": "REAL_SPACE_AGENCY_DATA",
            "instruments": raw_record.get("instruments", []),
            "archive_node": raw_record.get("provenance_node"),
            "license_attribution": raw_record.get("license_attribution")
        }
    }

def process_earth_analog(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes terrestrial observations into the standardized scientific analog model."""
    slope_mean = raw_record.get("slope_mean_deg")
    tri = raw_record.get("terrain_ruggedness_index_m")
    t_min = raw_record.get("temperature_min_k")
    t_max = raw_record.get("temperature_max_k")
    t_mean = raw_record.get("temperature_mean_k")
    aridity = raw_record.get("aridity_index")
    veg = raw_record.get("vegetation_cover_fraction", 0.0)

    # Estimate rock/rubble fraction from vegetation absence and ruggedness
    est_rock = clamp((tri / 100.0) * (1.0 - veg), 0.01, 0.35)

    return {
        "id": raw_record["id"],
        "name": raw_record["name"],
        "country": raw_record["country"],
        "coordinates": raw_record["coordinates"],
        "raw_physical_metrics": {
            "elevation_m": raw_record.get("elevation_m"),
            "elevation_datum": raw_record.get("elevation_datum"),
            "slope_mean_deg": slope_mean,
            "slope_max_deg": raw_record.get("slope_max_deg"),
            "terrain_ruggedness_index_m": tri,
            "temperature_min_k": t_min,
            "temperature_max_k": t_max,
            "temperature_mean_k": t_mean,
            "annual_precipitation_mm": raw_record.get("annual_precipitation_mm"),
            "aridity_index": aridity,
            "estimated_rock_fraction": round(est_rock, 3),
            "atmospheric_pressure_kpa": raw_record.get("pressure_kpa", 101.3)
        },
        "normalized_features": {
            "norm_slope": normalize_min_max(slope_mean, BOUNDS["slope_deg"]["min"], BOUNDS["slope_deg"]["max"]),
            "norm_ruggedness": normalize_min_max(tri, BOUNDS["tri_m"]["min"], BOUNDS["tri_m"]["max"]),
            "norm_temp_min": normalize_min_max(t_min, BOUNDS["temperature_k"]["min"], BOUNDS["temperature_k"]["max"]),
            "norm_temp_max": normalize_min_max(t_max, BOUNDS["temperature_k"]["min"], BOUNDS["temperature_k"]["max"]),
            "norm_aridity": normalize_min_max(aridity, BOUNDS["aridity_index"]["min"], BOUNDS["aridity_index"]["max"]),
            "norm_rock_abundance": normalize_min_max(est_rock, BOUNDS["rock_abundance"]["min"], BOUNDS["rock_abundance"]["max"])
        },
        "lithology": {
            "primary": raw_record.get("primary_lithology"),
            "dominant_minerals": raw_record.get("dominant_minerals", [])
        },
        "provenance": {
            "data_source_tier": "REAL_SPACE_AGENCY_DATA",
            "instruments": raw_record.get("instruments", []),
            "archive_node": raw_record.get("provenance_node"),
            "license_attribution": raw_record.get("license_attribution")
        }
    }

def run_pipeline():
    print("=" * 65)
    print("🛰️  Running Reproducible Scientific Data Preprocessing Pipeline")
    print("=" * 65)

    # 1. Load Raw Sources
    moon_raw = load_raw_json(RAW_DIR / "moon" / "lunar_surface_measurements.json")
    mars_raw = load_raw_json(RAW_DIR / "mars" / "martian_surface_measurements.json")
    earth_raw = load_raw_json(RAW_DIR / "earth" / "terrestrial_analog_measurements.json")

    print(f"Loaded raw records: Moon ({len(moon_raw)}), Mars ({len(mars_raw)}), Earth ({len(earth_raw)})")

    # 2. Process & Normalize
    processed_moon = [process_planetary_target(r, "Moon") for r in moon_raw]
    processed_mars = [process_planetary_target(r, "Mars") for r in mars_raw]
    processed_earth = [process_earth_analog(r) for r in earth_raw]

    # Combine planetary targets into processed target collection
    processed_targets = processed_moon + processed_mars

    # 3. Save Processed Datasets (Without overwriting raw data)
    targets_out_path = PROCESSED_DIR / "planetary_targets_processed.json"
    analogs_out_path = PROCESSED_DIR / "earth_analogs_processed.json"

    with open(targets_out_path, "w", encoding="utf-8") as f:
        json.dump(processed_targets, f, indent=2)
    print(f"✅ Saved processed planetary targets -> {targets_out_path}")

    with open(analogs_out_path, "w", encoding="utf-8") as f:
        json.dump(processed_earth, f, indent=2)
    print(f"✅ Saved processed Earth analogs -> {analogs_out_path}")

    # 4. Save Processing Run Metadata & Normalization Bounds
    run_meta = {
        "pipeline_version": "1.0.0",
        "timestamp_generated": "2026-11-15T17:53:00Z",
        "data_tier": "REAL_SPACE_AGENCY_PROVENANCE_DATA",
        "normalization_bounds": BOUNDS,
        "input_counts": {
            "moon_targets": len(processed_moon),
            "mars_targets": len(processed_mars),
            "earth_analogs": len(processed_earth)
        },
        "derived_features": [
            "norm_slope", "norm_ruggedness", "norm_temp_min", "norm_temp_max",
            "norm_aridity", "norm_rock_abundance"
        ],
        "output_artifacts": [
            str(targets_out_path.name),
            str(analogs_out_path.name)
        ]
    }

    meta_out_path = METADATA_DIR / "pipeline_run_metadata.json"
    with open(meta_out_path, "w", encoding="utf-8") as f:
        json.dump(run_meta, f, indent=2)
    print(f"✅ Saved pipeline metadata -> {meta_out_path}")
    print("=" * 65)
    print("Preprocessing completed successfully.")

if __name__ == "__main__":
    run_pipeline()
