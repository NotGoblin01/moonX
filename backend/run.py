import uvicorn
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting MoonBase Planner — Planetary Analog Finder")
    print("🌐 Web Application: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
