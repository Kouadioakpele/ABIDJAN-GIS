import "./Sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-menu">
        <a href="#" className="sidebar-item active">
          <span>⌂</span>
          <span>Tableau de bord</span>
        </a>

        <a href="#" className="sidebar-item">
          <span>▣</span>
          <span>Communes</span>
        </a>

        <a href="#" className="sidebar-item">
          <span>⌖</span>
          <span>Carte</span>
        </a>

        <a href="#" className="sidebar-item">
          <span>◈</span>
          <span>GeoJSON</span>
        </a>

        <a href="#" className="sidebar-item">
          <span>♙</span>
          <span>Utilisateurs</span>
        </a>

        <a href="#" className="sidebar-item">
          <span>⚙</span>
          <span>Paramètres</span>
        </a>
      </div>

      <div className="sidebar-bottom">
        <a href="#" className="sidebar-item">
          <span>↪</span>
          <span>Se déconnecter</span>
        </a>
      </div>
    </aside>
  );
}

export default Sidebar;
