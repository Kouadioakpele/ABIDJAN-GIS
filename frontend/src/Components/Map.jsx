import { MapContainer, TileLayer } from "react-leaflet";

import "leaflet/dist/leaflet.css";

function Map() {
  return (
    <MapContainer
      center={[5.36, -4.01]}
      zoom={11}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  );
}

export default Map;
