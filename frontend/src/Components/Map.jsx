import { useEffect, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";

import { getApiJson } from "@/lib/api";
import "leaflet/dist/leaflet.css";
import "./Map.css";

function quartierTooltip(feature, layer) {
  const properties = feature?.properties || {};
  const tooltip = document.createElement("span");
  tooltip.textContent = [properties.name, properties.commune_name].filter(Boolean).join(" · ") || "Quartier d’Abidjan";
  layer.bindTooltip(tooltip);
}

function Map({ retryKey }) {
  const [quartiers, setQuartiers] = useState(null);

  useEffect(() => {
    let active = true;
    getApiJson("/quartiers?limit=1000")
      .then((collection) => {
        if (active) setQuartiers(collection);
      })
      .catch(() => {
        if (active) setQuartiers({ type: "FeatureCollection", features: [] });
      });
    return () => { active = false; };
  }, [retryKey]);

  return (
    <MapContainer
      center={[5.36, -4.01]}
      zoom={11}
      className="abidjan-map"
      scrollWheelZoom
      aria-label="Carte interactive d’Abidjan"
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {quartiers?.features?.length > 0 && (
        <GeoJSON
          key={quartiers.features.length}
          data={quartiers}
          onEachFeature={quartierTooltip}
          style={{ color: "#28664f", weight: 1, opacity: 0.8, fillColor: "#589c80", fillOpacity: 0.08 }}
        />
      )}
    </MapContainer>
  );
}

export default Map;
