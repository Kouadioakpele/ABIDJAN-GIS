import { Suspense, lazy, useEffect, useState } from "react";
import { useReducedMotion, motion } from "motion/react";
import { ArrowDown, ArrowUpRight, Files, Layers3, MapPinned, RefreshCw, Upload } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getApiJson } from "@/lib/api";
import "./Dashboard.css";

const Map = lazy(() => import("../Components/Map"));

function Dashboard() {
  const reduceMotion = useReducedMotion();
  const [stats, setStats] = useState(null);
  const [apiStatus, setApiStatus] = useState("loading");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    setApiStatus("loading");
    getApiJson("/dashboard/stats")
      .then((data) => {
        if (!active) return;
        setStats(data);
        setApiStatus("connected");
      })
      .catch(() => {
        if (active) setApiStatus("offline");
      });
    return () => { active = false; };
  }, [retry]);
  const intro = reduceMotion
    ? { hidden: { opacity: 1 }, visible: { opacity: 1 } }
    : { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };
  const list = reduceMotion
    ? { hidden: {}, visible: { transition: {} } }
    : { hidden: {}, visible: { transition: { staggerChildren: 0.08, delayChildren: 0.08 } } };
  const item = reduceMotion
    ? { hidden: { opacity: 1 }, visible: { opacity: 1 } }
    : { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.32 } } };

  const showMap = () => document.getElementById("map-canvas")?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  const unavailable = apiStatus === "offline";
  const statCards = [
    { label: "Communes couvertes", value: stats?.communes, detail: "Dans les données chargées", icon: MapPinned, tone: "gold" },
    { label: "Quartiers", value: stats?.quartiers, detail: "Quartiers cartographiés", icon: Layers3, tone: "green" },
    { label: "Couches géographiques", value: stats?.layers, detail: "Couches importées", icon: Files, tone: "cream" },
    { label: "Fichiers GeoJSON", value: stats?.geojson_files, detail: "Fichiers GeoJSON importés", icon: Upload, tone: "muted" },
  ];

  return (
    <div className="dashboard" id="dashboard">
      <motion.section className="dashboard-header" aria-labelledby="dashboard-title" initial="hidden" animate="visible" variants={intro}>
        <div className="dashboard-heading">
          <span className="eyebrow">SYSTÈME D’INFORMATION GÉOGRAPHIQUE</span>
          <h1 id="dashboard-title">Bonjour, Kouadio</h1>
          <p>Retrouvez en un coup d’œil les données du district autonome d’Abidjan.</p>
        </div>
        <div className="dashboard-actions">
          <Badge variant="outline" className={`api-badge api-badge--${apiStatus}`}>
            <span /> {apiStatus === "connected" ? "API connectée" : apiStatus === "loading" ? "Connexion à l’API" : "API hors ligne"}
          </Badge>
          {unavailable && <Button className="retry-button" variant="ghost" size="sm" onClick={() => setRetry((attempt) => attempt + 1)}><RefreshCw size={14} /> Réessayer</Button>}
          <Badge variant="outline" className="district-badge"><span /> Abidjan, Côte d’Ivoire</Badge>
          <Button className="explore-button" size="lg" onClick={showMap}>
            Explorer la carte <ArrowDown size={16} />
          </Button>
        </div>
      </motion.section>

      <motion.section className="stats-grid" aria-label="Résumé des données" variants={list} initial="hidden" animate="visible">
        {statCards.map(({ label, value, detail, icon: Icon, tone }) => (
          <motion.div key={label} variants={item} whileHover={reduceMotion ? undefined : { y: -3 }} transition={{ duration: 0.18 }}>
            <Card className={`stat-card stat-card--${tone}`}>
              <CardHeader className="stat-card-header">
                <CardTitle>{label}</CardTitle>
                <CardAction><span className="stat-icon"><Icon size={18} strokeWidth={1.8} /></span></CardAction>
              </CardHeader>
              <CardContent className="stat-card-content">
                <strong>{value == null ? "—" : Number(value).toLocaleString("fr-FR")}</strong>
                <CardDescription>{unavailable ? "API indisponible" : apiStatus === "loading" ? "Chargement…" : detail}</CardDescription>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.section>

      <motion.section
        className="map-section"
        id="carte"
        aria-labelledby="map-title"
        initial={reduceMotion ? false : { opacity: 0, y: 14 }}
        whileInView={reduceMotion ? undefined : { opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.12 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Card className="map-card">
          <CardHeader className="map-heading">
            <div>
              <span className="eyebrow">EXPLORATION</span>
              <CardTitle id="map-title">Carte du district</CardTitle>
              <CardDescription>Déplacez-vous et zoomez pour explorer Abidjan.</CardDescription>
            </div>
            <CardAction>
              <Badge variant="outline" className="map-badge"><span /> Fond de carte actif</Badge>
            </CardAction>
          </CardHeader>
          <div className="map-canvas" id="map-canvas" role="region" aria-label="Carte interactive d’Abidjan">
            <Suspense fallback={<div className="map-loading" role="status">Chargement de la carte…</div>}>
              <Map retryKey={retry} />
            </Suspense>
          </div>
          <CardContent className="map-footer">
            <span>© OpenStreetMap contributors</span>
            <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
              À propos des données <ArrowUpRight size={13} />
            </a>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  );
}

export default Dashboard;
