
# MoonBase Planner — Planetary Analog Finder & Results Dashboard

An open-access decision support tool and hackathon prototype designed to identify, quantify, and map terrestrial environments on Earth that share physical, geological, and environmental characteristics with candidate exploration zones on the Moon and Mars.

Grounded in peer-reviewed open space agency data from the **NASA Planetary Data System (PDS)**, **USGS Astrogeology**, **NASA Earthdata LP DAAC**, and **CGIAR-CSI**.

---

## 1. Project Structure

```text
moon/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application initialization & static mounting
│   │   ├── routes.py                  # API endpoints (GET /api/health, POST /api/analyze, POST /api/compare, etc.)
│   │   └── schemas.py                 # Pydantic v2 validation models
│   ├── main.py                        # Alternative app entry point
│   └── run.py                         # Convenience development server launcher
├── data/
│   ├── earth_analogs.json             # Benchmark Earth analog catalog with rich narratives
│   ├── planetary_targets.json         # Moon & Mars exploration target sites
│   ├── processed/
│   │   ├── earth_analogs_processed.json       # Real space-agency normalized continuous feature vectors
│   │   └── planetary_targets_processed.json   # Real space-agency normalized target feature vectors
│   ├── raw/                           # Raw instrument inputs (LOLA, MOLA, SRTM, MODIS, Aridity)
│   └── metadata/
│       ├── data_sources_manifest.json         # Authoritative catalog of official space-agency sources & licenses
│       ├── data_provenance_manifest.json      # Provenance, instrument nodes, and measurement units
│       └── pipeline_run_metadata.json         # Normalization bounds, derived keys, and pipeline records
├── frontend/
│   ├── index.html                     # Space-themed interactive landing page
│   ├── explorer.html                  # Interactive Results Dashboard & Planetary Analog Explorer
│   ├── about.html                     # Transparent Methodology & Official Data Sources registry
│   ├── css/
│   │   ├── homepage.css               # Landing page responsive styling
│   │   ├── styles.css                 # Results dashboard, workflow breadcrumb, map & card styling
│   │   └── methodology.css            # Methodology, LaTeX equations, and data tables styling
│   └── js/
│       ├── app.js                     # Main state machine, API fetcher, Leaflet map renderer, & Demo Mode
│       └── analog_map_loader.js       # Standalone reusable Leaflet analog map loader component
├── models/
│   ├── similarity_model.py            # Normalized multi-feature weighted heuristic prototype scoring model
│   ├── knn_similarity.py              # Scikit-Learn K-Nearest Neighbors (KNN) & Cosine vector similarity engine
│   ├── mission_recommender.py         # 6-category operational mission classification engine with non-agency guardrails
│   └── explanation_layer.py           # Concise, data-grounded "Why This Location?" checkmark generator
├── scripts/
│   └── preprocess_data.py             # Reproducible data normalization and feature extraction pipeline
├── requirements.txt                   # Production Python package dependencies
└── README.md                          # Comprehensive documentation
```

---

## 2. How to Run Frontend & Backend

Because FastAPI directly serves the modern static frontend files, both the backend API and frontend UI run seamlessly from a single unified server.

### Prerequisites
- Python 3.9+ installed (`python --version`)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Setup & Run
```bash
# 1. Clone repository & navigate to project root
cd moon

# 2. (Optional) Create & activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Start the application
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
# Or alternately:
python backend/run.py
```

### Accessing the Web Application
Open your web browser and navigate to:
- **Homepage:** `http://localhost:8000/` or `http://localhost:8000/index.html`
- **Results Dashboard & Explorer:** `http://localhost:8000/explorer.html`
- **Methodology & Data Sources:** `http://localhost:8000/about.html`
- **Interactive Swagger API Documentation:** `http://localhost:8000/docs`
- **API Health Check:** `http://localhost:8000/api/health`

---

## 3. Required Packages

Installed via `requirements.txt`:
- `fastapi>=0.110.0`: Modern high-performance asynchronous web framework
- `uvicorn>=0.28.0`: Lightning-fast ASGI production web server
- `pydantic>=2.0.0`: Data validation, serialization, and type enforcement
- `pandas>=2.0.0`: Data manipulation and preprocessing
- `numpy>=1.24.0`: Multidimensional array operations and vector math
- `scikit-learn>=1.3.0`: K-Nearest Neighbors (KNN) and Cosine distance algorithms
- `python-multipart>=0.0.9`: Multipart form data parsing for FastAPI

---

## 4. Environment Variables

The application is designed to be **zero-config** for local hackathon evaluations. Optional environment variables for containerized deployments:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the Uvicorn web server |
| `HOST` | `0.0.0.0` | Host interface binding |
| `DEBUG` | `False` | Enable verbose Uvicorn reloading |

*Note: No proprietary third-party API keys or private cloud credentials are required; all orbital and terrestrial datasets are bundled locally in `data/`.*

---

## 5. Known Limitations & Scientific Guardrails

1. **Environmental Feature Analogy vs. Habitability:**
   - MoonBase Planner evaluates statistical proximity across physical variables (slope, ruggedness, temperature, aridity, lithology, and surface regolith).
   - It is **explicitly NOT** a prediction of biological habitability, extraterrestrial life support, or human survival.
2. **Atmospheric & Gravitational Disparities:**
   - Earth has a 1-bar N₂/O₂ atmosphere and $1.0g$ gravity.
   - The Moon operates in a near-total vacuum with $0.166g$ gravity.
   - Mars has $\sim 6\text{ mbar}$ CO₂ and $0.38g$ gravity.
   - Ballistic particle dynamics and atmospheric aerodynamics differ fundamentally.
3. **Radiation Environment:**
   - Earth's magnetosphere shields surface analog sites from Galactic Cosmic Rays (GCRs) and Solar Particle Events (SPEs).
4. **Non-Agency Operational Endorsement:**
   - Mission recommendations use strict forward-looking wording (*"Potentially useful for..."*, *"Could support..."*, *"Suitable for prototype testing based on the selected criteria"*).
   - Recommendations do not imply official operational certification or designation by NASA, ESA, or any space agency.

---

## 6. Final Testing & Verification Status

| Component | Status | Verification Summary |
| :--- | :---: | :--- |
| **Data Integrity** | **PASS** | 11 Earth Analogs, 6 Planetary Targets, Provenance Manifest, Data Sources Manifest, and Processing Pipeline metadata verified with 100% field completeness and documented SI units. |
| **Machine Learning Engine** | **PASS** | `EnvironmentalKNNMatcher` and normalized multi-feature weighted heuristic model tested across all targets with verified boundary checks ($0 \le \text{Score} \le 100$). |
| **Mission Recommender** | **PASS** | Evaluated across 6 target categories; non-agency phrasing and dynamic sorting validated. |
| **FastAPI Backend** | **PASS** | All routes tested: `/api/health`, `/api/earth-analogs`, `/api/earth-analogs/{id}`, `/api/targets`, `/api/data-sources`, `/api/provenance`, `POST /api/analyze`, and `POST /api/compare`. |
| **Frontend & Navigation** | **PASS** | Tested `index.html`, `explorer.html`, and `about.html`. Tested 6-step workflow breadcrumbs, interactive Leaflet Carto Dark map, Demo Mode buttons, and error retry handlers. |
| **Security Audit** | **PASS** | Zero hardcoded API keys, private tokens, or secrets found. Strict Pydantic input validation on all payloads. |
| **Responsiveness & UX** | **PASS** | Fully responsive layout tested down to mobile viewports ($<768\text{px}$) with `:focus-visible` accessibility support. |
=======
# MoonX
Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars
>>>>>>> faca87796b20b276318eb65f5b8358943b36fe78
