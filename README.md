# ABJ GIS

Application cartographique pour le district autonome d’Abidjan : interface React/Vite, API Flask et stockage spatial PostgreSQL/PostGIS.

## Démarrage local

### 1. Base PostgreSQL/PostGIS

Docker Desktop doit être installé et démarré pour cette option :

```powershell
docker compose up -d database
```

La base utilise `abj_gis` / `abj_gis_dev_password` pour le développement local. Pour utiliser une autre instance PostgreSQL, modifiez `DATABASE_URL` dans `backend/.env`.

### 2. API Flask

Utilisez Python 3.12, puis depuis PowerShell :

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app app init-db
flask --app app seed-abidjan
flask --app app run --debug --port 5000
```

Le shapefile source se trouve dans `backend/data`. La commande `seed-abidjan` agrège les 270 quartiers et les limites communales présentes dans ce jeu de données. Il contient 10 communes distinctes ; ce chiffre reflète la couverture du fichier, pas nécessairement celle de tout le district.

### 3. Interface React

Dans un autre terminal :

```powershell
cd frontend
npm install
npm run dev
```

L’URL de l’API peut être modifiée dans `frontend/.env.local` avec `VITE_API_URL` (par défaut `http://localhost:5000/api`).

## API disponible

- `GET /api/health` — état PostgreSQL/PostGIS
- `GET /api/dashboard/stats` — nombres de communes, quartiers et couches
- `GET /api/communes` — limites communales en GeoJSON
- `GET /api/quartiers` — quartiers en GeoJSON (`limit` et `offset` acceptés)
- `GET /api/layers` — couches importées
- `POST /api/layers` — import GeoJSON, GeoPackage ou ZIP de shapefile (`multipart/form-data`, champ `file`)
- `GET /api/layers/<id>/features` — entités d’une couche importée

Les imports sont reprojetés en EPSG:4326, contrôlés/réparés avec Shapely, puis écrits dans PostGIS avec GeoPandas. Les tables d’import utilisent des noms générés par le serveur.

> Cette première version est prévue pour le développement local. L’authentification et les migrations de schéma restent à ajouter avant une mise en production.
