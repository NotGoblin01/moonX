import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def load_json(filename: str) -> List[Dict[str, Any]]:
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

PLANETARY_TARGETS = load_json("planetary_targets.json")
EARTH_ANALOGS = load_json("earth_analogs.json")

# Rule-based similarity matrix representing initial analog physics/geological affinities
SIMILARITY_MATRIX: Dict[str, Dict[str, Dict[str, Any]]] = {
    "shackleton-crater": {
        "mcmurdo-dry-valleys": {
            "score": 93.4,
            "reasons": [
                "Extreme sub-zero cryosphere analogous to Lunar South Pole permanently shadowed regions (PSRs)",
                "Hyper-arid katabatic winds preventing liquid water, modeling cryogenic sublimation dynamics",
                "Permafrost ice lenses mirroring subsurface trapped volatile reserves"
            ],
            "breakdown": [
                {"category": "Thermal & Cryo-physics", "score": 96.0, "details": "Models cryogenic thermal stress and frozen regolith drill mechanics."},
                {"category": "Geological Structure", "score": 89.0, "details": "Hyper-arid desiccated soil profile free of active precipitation."},
                {"category": "Illumination & Insolation", "score": 95.0, "details": "Prolonged polar darkness and low-angle solar elevation."}
            ]
        },
        "devon-haughton-crater": {
            "score": 91.0,
            "reasons": [
                "Haughton Impact Crater features breccia and shatter cone geology similar to lunar impact terrain",
                "Arctic cold environment testing remote autonomous rover exploration under severe thermal loss"
            ],
            "breakdown": [
                {"category": "Impact Mechanics", "score": 94.0, "details": "Pristine crater morphology and ejecta rim topography."},
                {"category": "Thermal Regime", "score": 84.0, "details": "Sub-zero polar winter testing conditions."},
                {"category": "Operations Cadence", "score": 88.0, "details": "Isolation and limited satellite comms windows."}
            ]
        },
        "hi-seas-mauna-loa": {
            "score": 75.2,
            "reasons": [
                "High elevation low-oxygen environment testing human life support isolation",
                "Volcanic regolith simulant interaction with space suits and mechanical joints"
            ],
            "breakdown": [
                {"category": "Habitat & Human Factors", "score": 92.0, "details": "Closed loop life support isolation trials."},
                {"category": "Terrain Interaction", "score": 68.0, "details": "Basaltic regolith behavior on seals and EVA fabrics."},
                {"category": "Thermal Similarity", "score": 65.0, "details": "Moderate alpine cold rather than true cryogenic PSR levels."}
            ]
        }
    },
    "oceanus-procellarum": {
        "lanzarote-timanfaya": {
            "score": 95.8,
            "reasons": [
                "Uncollapsed volcanic lava tubes with dimensions directly mirroring Marius Hills lunar skylights",
                "Pure basaltic composition and absence of vegetation providing unweathered surface geology"
            ],
            "breakdown": [
                {"category": "Volcanic Speleology", "score": 98.0, "details": "Cave geometry suitable for lunar subsurface habitat anchoring."},
                {"category": "Mineralogy & Basalt", "score": 95.0, "details": "Low-silica basalt flow chemistry comparable to mare volcanism."},
                {"category": "Robotic Cave Ingress", "score": 94.0, "details": "Optimal terrain for tethered drone & climber rover trials."}
            ]
        },
        "cueva-de-los-verdes": {
            "score": 92.5,
            "reasons": [
                "Deep intact volcanic tube corridors offering natural radiation shielding",
                "GPS-denied underground environment for autonomous robotics trials"
            ],
            "breakdown": [
                {"category": "Cave Conduits", "score": 94.0, "details": "Continuous multi-kilometer tube geometry."},
                {"category": "Shielding Testing", "score": 92.0, "details": "Cosmic radiation attenuation modeling."}
            ]
        },
        "hi-seas-mauna-loa": {
            "score": 89.1,
            "reasons": [
                "Extensive pahoehoe and a'a basalt flows analogous to mare plain basalt shields",
                "Subsurface lava tube exploration testing crew navigation without GPS"
            ],
            "breakdown": [
                {"category": "Subsurface Lava Caves", "score": 92.0, "details": "Intact tube networks for shelter simulations."},
                {"category": "Basalt Morphology", "score": 88.0, "details": "Fresh volcanic crust with glassy basalt fragments."},
                {"category": "Dust & Simulant Stress", "score": 87.0, "details": "Abrasive cinder and ash interactions with mechanisms."}
            ]
        }
    },
    "jezero-crater": {
        "atacama-yungay": {
            "score": 94.5,
            "reasons": [
                "Hyper-arid perchlorate and nitrate salt deposits mirroring Martian regolith toxicity",
                "Desiccated clay beds and solar UV radiation levels matching Mars surface conditions",
                "Gold-standard testing ground for Raman and drill life-detection biosensors"
            ],
            "breakdown": [
                {"category": "Geochemistry & Astrobiology", "score": 98.0, "details": "Extreme salt deposits and zero organic decay analogous to Jezero delta."},
                {"category": "Desiccation Dynamics", "score": 95.0, "details": "Ultra-dry soil preserving fossilized microbial biosignatures."},
                {"category": "Atmospheric & UV Stress", "score": 90.0, "details": "Extreme solar UV exposure stressing optical sensors and coatings."}
            ]
        },
        "svalbard-spitsbergen": {
            "score": 91.2,
            "reasons": [
                "Hydrothermal carbonate globules matching ALH84001 Martian meteorite minerals",
                "Cold spring and permafrost lake sediment systems identical to early wet Mars evolution"
            ],
            "breakdown": [
                {"category": "Carbonate Mineralogy", "score": 96.0, "details": "Rare carbonate precipitates identical to Jezero delta mineral suites."},
                {"category": "Glacial Fluvial Transport", "score": 90.0, "details": "Sedimentary sorting in cold braided river channels."},
                {"category": "Astrobiology Protocols", "score": 88.0, "details": "Sterile sample-cache drills and biosignature instrumentation."}
            ]
        },
        "wadi-rum-valley": {
            "score": 89.0,
            "reasons": [
                "Red iron-oxide sandstones and desert flats replicating Jezero floor rocks",
                "Autonomous rover SLAM navigation in terrain with high optical contrast"
            ],
            "breakdown": [
                {"category": "Mineral Color & Optics", "score": 92.0, "details": "Iron oxide mineral staining for vision testing."},
                {"category": "Rock Dispersion", "score": 86.0, "details": "Obstacle avoidance across eroded bedrock."}
            ]
        }
    },
    "olympus-mons": {
        "hi-seas-mauna-loa": {
            "score": 96.2,
            "reasons": [
                "Massive oceanic shield volcano structure mirroring the physical geometry of Olympus Mons",
                "Pahoehoe lava fields, inflated lava tubes, and cinder cone formations",
                "High altitude testing reducing atmospheric pressure and humidity"
            ],
            "breakdown": [
                {"category": "Shield Volcano Volcanism", "score": 98.0, "details": "Identical low-viscosity basalt flow morphologies and collapsed vents."},
                {"category": "Elevation & Atmosphere", "score": 94.0, "details": "Sub-alpine thin atmosphere and heightened solar radiation."},
                {"category": "Regolith & Slag Traverse", "score": 96.0, "details": "Steep incline rover traction and wheel wear testing."}
            ]
        },
        "lanzarote-timanfaya": {
            "score": 91.0,
            "reasons": [
                "Volcanic ash fields, hornitos, and extensive fissure eruption basalt plains",
                "Near-zero vegetation simulating unweathered extraterrestrial volcanic slopes"
            ],
            "breakdown": [
                {"category": "Lava Field Structure", "score": 93.0, "details": "Basaltic scoria cones and lava cascades."},
                {"category": "Mineralogy", "score": 90.0, "details": "Tholeiitic and alkali basalt comparisons to Martian volcanics."},
                {"category": "Operational Suitability", "score": 90.0, "details": "Astronaut traverse planning on abrasive volcanic surfaces."}
            ]
        },
        "mojave-pisgah": {
            "score": 86.4,
            "reasons": [
                "Basaltic cinder cone and rough clinker lava field simulating steep volcanic slopes",
                "Abrasive cinder stress on rover suspension and wheel treads"
            ],
            "breakdown": [
                {"category": "Cinder Slope Mechanics", "score": 90.0, "details": "Traction on loose angular scoria slopes."},
                {"category": "Arid Surface", "score": 84.0, "details": "Low humidity mechanical endurance testing."}
            ]
        }
    },
    "schrodinger-basin": {
        "devon-haughton-crater": {
            "score": 91.5,
            "reasons": [
                "Complex impact crater basin topology matching Schrödinger's peak ring and inner floor ejecta",
                "High-arctic cold desert testing low-temperature field sample extraction"
            ],
            "breakdown": [
                {"category": "Impact Peak-Ring Topography", "score": 95.0, "details": "Elevated central ring and breccia blanket terrain."},
                {"category": "Low-Temp Logistics", "score": 89.0, "details": "Remote communications and polar logistics drills."}
            ]
        },
        "iceland-askja": {
            "score": 89.2,
            "reasons": [
                "Volcanic caldera with unweathered basalt ejecta and hydrothermal vents",
                "Historic astronaut lunar geology field mapping testbed"
            ],
            "breakdown": [
                {"category": "Caldera Geomorphology", "score": 92.0, "details": "High plateau volcanic collapse structure."},
                {"category": "Basalt Sample Caching", "score": 88.0, "details": "Pumice and black basalt sampling drills."}
            ]
        }
    },
    "valles-marineris": {
        "wadi-rum-valley": {
            "score": 93.8,
            "reasons": [
                "Steep sandstone canyon walls and dry sandy corridor floors",
                "Iron-oxide sediment layers analogous to equatorial Martian canyon walls"
            ],
            "breakdown": [
                {"category": "Canyon Wall Stratigraphy", "score": 96.0, "details": "High sheer cliff faces and layered scree slopes."},
                {"category": "Dune & Bedrock Traverse", "score": 92.0, "details": "Navigation between rocky towers and sand drifts."}
            ]
        },
        "atacama-yungay": {
            "score": 92.8,
            "reasons": [
                "Hyper-arid canyon valleys with thick evaporite and sulfate salt strata",
                "Solar radiation and desiccated atmospheric column testing equipment durability"
            ],
            "breakdown": [
                {"category": "Evaporite & Sulfate Geochemistry", "score": 96.0, "details": "Extensive salt beds analogous to layered canyon deposits."},
                {"category": "Hyper-aridity", "score": 94.0, "details": "Near-zero soil moisture preserving layered stratigraphy."}
            ]
        }
    }
}

def calculate_analog_similarity(target_id: str) -> List[Dict[str, Any]]:
    """Calculates analog similarity scores and explanations for a given planetary target."""
    target_match_dict = SIMILARITY_MATRIX.get(target_id, {})
    analogs_by_id = {a["id"]: a for a in EARTH_ANALOGS}
    
    results = []
    
    # Process explicitly matched analogs first
    for analog_id, data in target_match_dict.items():
        if analog_id in analogs_by_id:
            analog = analogs_by_id[analog_id]
            results.append({
                "earth_analog": analog,
                "similarity_score": data["score"],
                "primary_reasons": data["reasons"],
                "breakdown": data["breakdown"],
                "recommended_missions": analog.get("recommended_missions", [])
            })
            
    # For any earth analog not in the top pre-computed matrix, provide a computed baseline score
    for analog_id, analog in analogs_by_id.items():
        if analog_id not in target_match_dict:
            score = float(analog.get("analog_score", 55.0)) * 0.8
            results.append({
                "earth_analog": analog,
                "similarity_score": round(score, 1),
                "primary_reasons": [
                    "General environmental stress and isolated remote field terrain",
                    f"Features {analog.get('terrain', 'unpaved terrain')} useful for secondary robotic testing"
                ],
                "breakdown": [
                    {"category": "Terrain General", "score": 60.0, "details": "General unpaved rugged testbed."},
                    {"category": "Atmospheric Context", "score": 54.0, "details": "Terrestrial atmosphere with secondary stress factors."}
                ],
                "recommended_missions": analog.get("recommended_missions", [])[:2]
            })
            
    # Sort descending by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
            
    # Sort descending by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
