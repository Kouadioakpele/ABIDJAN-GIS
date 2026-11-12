import { motion } from "motion/react";
import { Bell, MapPinned, Search } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import "./Navbar.css";

function Navbar() {
  return (
    <motion.header
      className="navbar"
      initial={{ y: -12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
    >
      <a className="navbar-logo" href="#dashboard" aria-label="ABJ GIS, accueil">
        <span className="logo-icon"><MapPinned size={19} strokeWidth={1.8} /></span>
        <span className="brand-copy"><strong>ABJ<span>GIS</span></strong><small>Territoire & données</small></span>
      </a>

      <label className="navbar-search">
        <Search size={16} aria-hidden="true" />
        <Input type="search" aria-label="Rechercher une commune" placeholder="Rechercher une commune..." />
      </label>

      <div className="navbar-actions">
        <Button className="notification" variant="ghost" size="icon" aria-label="Notifications">
          <Bell size={18} />
          <i aria-hidden="true" />
        </Button>
        <div className="user-profile">
          <Avatar className="profile-avatar"><AvatarFallback>KA</AvatarFallback></Avatar>
          <div className="profile-copy">
            <strong>Kouadio Akpele</strong>
            <small>Administrateur</small>
          </div>
        </div>
      </div>
    </motion.header>
  );
}

export default Navbar;
