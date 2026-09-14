import "./Navbar.css";
function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <span className="logo-icon">🗺</span>
        <span>Abidjan GIS</span>
      </div>

      <div className="navbar-search">
        <span>⌕</span>
        <input type="text" placeholder="Rechercher une commune..." />
      </div>

      <div className="navbar-actions">
        <button className="notification">🔔</button>

        <div className="user-profile">
          <div className="avatar">KA</div>
          <div>
            <strong>Kouadio Akpele</strong>
            <small>Administrateur</small>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
