import "./Dashboard.css";
import Map from "../Components/Map";
function Dashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Tableau de bord</h1>
          <p>Vue générale des données géographiques d’Abidjan</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Communes</span>
          <strong>13</strong>
          <small>Communes disponibles</small>
        </div>

        <div className="stat-card">
          <span>Couches</span>
          <strong>0</strong>
          <small>Couches géographiques</small>
        </div>

        <div className="stat-card">
          <span>GeoJSON</span>
          <strong>0</strong>
          <small>Fichiers importés</small>
        </div>

        <div className="stat-card">
          <span>Utilisateurs</span>
          <strong>0</strong>
          <small>Utilisateurs enregistrés</small>
        </div>
      </div>

      <div className="map-preview">
        <div>
          <h2>Carte d'Abidjan</h2>
          <p>La carte interactive sera intégrée ici.</p>
        </div>
        <Map />
      </div>
    </div>
  );
}

export default Dashboard;
