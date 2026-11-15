/**
 * MoonBase Planner — Earth Analog Data Loader & Leaflet Map Controller
 * Loads structured local JSON analog dataset (data/earth_analogs.json)
 * and renders locations on an interactive Leaflet map.
 * 
 * NOTE: All locations and scores represent prototype / demo data for software development.
 */

class EarthAnalogMap {
  constructor(mapElementId, options = {}) {
    this.mapElementId = mapElementId;
    this.dataPath = options.dataPath || "/data/earth_analogs.json";
    this.map = null;
    this.markers = [];
    this.analogs = [];
    this.onSelectCallback = options.onSelect || null;
  }

  // Initialize the Leaflet map
  init() {
    if (!document.getElementById(this.mapElementId)) {
      console.warn(`Map element #${this.mapElementId} not found.`);
      return;
    }

    this.map = L.map(this.mapElementId, {
      zoomControl: true,
      minZoom: 2,
      maxZoom: 16,
      worldCopyJump: true
    }).setView([20.0, 0.0], 2);

    // OpenStreetMap dark basemap
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/" target="_blank">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 19
    }).addTo(this.map);

    this.map.zoomControl.setPosition("topright");
    return this;
  }

  // Determine pin color by analog score
  static getScoreColor(score) {
    if (score >= 90) return "#22c55e"; // High match (green)
    if (score >= 80) return "#38bdf8"; // Moderate match (cyan)
    return "#eab308";                  // Baseline match (yellow)
  }

  // Fetch JSON dataset and render markers
  async loadAndRender(filterCategory = null) {
    try {
      const response = await fetch(this.dataPath);
      if (!response.ok) {
        throw new Error(`Failed to load analog data from ${this.dataPath} (Status: ${response.status})`);
      }

      this.analogs = await response.json();
      
      const toRender = filterCategory
        ? this.analogs.filter(item => item.terrain.toLowerCase().includes(filterCategory.toLowerCase()))
        : this.analogs;

      this.renderMarkers(toRender);
      return toRender;
    } catch (err) {
      console.error("Error loading Earth analog dataset:", err);
      return [];
    }
  }

  // Render analog markers on map
  renderMarkers(items) {
    // Clear existing markers
    this.markers.forEach(marker => this.map.removeLayer(marker));
    this.markers = [];

    const bounds = [];

    items.forEach((item, index) => {
      const lat = item.latitude;
      const lon = item.longitude;
      const score = item.analog_score;
      const color = EarthAnalogMap.getScoreColor(score);

      // Custom Circular Marker with Score Glow
      const customIcon = L.divIcon({
        className: "custom-map-pin",
        html: `
          <div style="
            background: ${color};
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid #ffffff;
            box-shadow: 0 0 16px ${color}, 0 3px 8px rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 800;
            color: #070b14;
          ">
            ${index + 1}
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -16]
      });

      const marker = L.marker([lat, lon], { icon: customIcon }).addTo(this.map);

      // Create rich structured popup
      const popupHtml = this.createPopupContent(item, color);
      marker.bindPopup(popupHtml, { maxWidth: 330 });

      // Click event
      marker.on("click", () => {
        if (typeof this.onSelectCallback === "function") {
          this.onSelectCallback(item, index);
        }
      });

      this.markers.push(marker);
      bounds.push([lat, lon]);
    });

    if (bounds.length > 0) {
      this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 4 });
    }
  }

  // Build Popup HTML using the structured JSON fields
  createPopupContent(item, color) {
    const primaryMission = (item.recommended_missions && item.recommended_missions.length > 0)
      ? item.recommended_missions[0]
      : "General Surface Operations Testing";

    return `
      <div class="popup-container">
        <div class="popup-header">
          <h4 class="popup-title">${item.name}</h4>
          <div class="popup-country">
            <span>📍 ${item.country}</span>
            <span class="popup-category-pill">${item.terrain.split(" ")[0]}</span>
          </div>
        </div>

        <div class="popup-score-row">
          <span class="popup-score-label">Analog Score:</span>
          <span class="popup-score-value" style="color: ${color}; font-weight: 800;">${item.analog_score}%</span>
        </div>

        <div class="popup-mission-box">
          <div class="popup-mission-label">Recommended Mission:</div>
          <div class="popup-mission-text">🎯 ${primaryMission}</div>
        </div>

        <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px; line-height: 1.4;">
          <div><strong>Terrain:</strong> ${item.terrain}</div>
          <div><strong>Geology:</strong> ${item.geology}</div>
          <div><strong>Surface:</strong> ${item.surface_conditions}</div>
        </div>

        <p class="popup-desc">${item.explanation}</p>

        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 0.4rem; margin-top: 0.4rem;">
          <span class="popup-footer-tag">PROTOTYPE DEMO DATA</span>
          <span style="font-size: 10px; color: #64748b;">Not NASA analysis</span>
        </div>
      </div>
    `;
  }

  // Zoom to and open popup for an analog by index
  focusLocation(index) {
    const marker = this.markers[index];
    if (marker) {
      this.map.setView(marker.getLatLng(), 5, { animate: true });
      marker.openPopup();
    }
  }

  // Reset view to encompass all markers
  resetView() {
    if (this.markers.length > 0) {
      const group = new L.featureGroup(this.markers);
      this.map.fitBounds(group.getBounds().pad(0.15));
    } else {
      this.map.setView([20.0, 0.0], 2);
    }
  }
}

// Export for module or global use
if (typeof window !== "undefined") {
  window.EarthAnalogMap = EarthAnalogMap;
}
