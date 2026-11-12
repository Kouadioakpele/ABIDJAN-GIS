import { BarChart3, FileUp, Layers3, Map, MapPinned, Settings2, UsersRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import "./Sidebar.css";

const plannedItems = [
  { label: "Communes", icon: MapPinned },
  { label: "Couches", icon: Layers3 },
  { label: "Importer GeoJSON", icon: FileUp },
  { label: "Utilisateurs", icon: UsersRound },
];

function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Navigation principale">
      <nav className="sidebar-menu">
        <p className="sidebar-label">ESPACE DE TRAVAIL</p>
        <a href="#dashboard" className="sidebar-item active" aria-current="page">
          <BarChart3 size={17} /> <span>Vue générale</span>
        </a>
        <a href="#carte" className="sidebar-item">
          <Map size={17} /> <span>Carte interactive</span>
        </a>

        <Separator className="sidebar-separator" />
        <p className="sidebar-label sidebar-label--secondary">GESTION</p>
        {plannedItems.map(({ label, icon: Icon }) => (
          <div className="sidebar-item sidebar-item--disabled" key={label} aria-disabled="true" title="Fonctionnalité bientôt disponible">
            <Icon size={17} /> <span>{label}</span>
            <Badge variant="outline" className="coming-soon">À venir</Badge>
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-item sidebar-item--disabled" aria-disabled="true" title="Fonctionnalité bientôt disponible">
          <Settings2 size={17} /> <span>Paramètres</span>
          <Badge variant="outline" className="coming-soon">À venir</Badge>
        </div>
        <div className="sidebar-footer"><span className="footer-mark"><MapPinned size={13} /></span><span>ABJ GIS <small>Version 1.0</small></span></div>
      </div>
    </aside>
  );
}

export default Sidebar;
