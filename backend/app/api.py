import json
import re
import tempfile
from pathlib import Path

import geopandas as gpd
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from .extensions import db
from .models import Commune, GeoLayer, Quartier
from .services.geodata import import_layer


api = Blueprint("api", __name__)
ALLOWED_EXTENSIONS = {"geojson", "json", "gpkg", "zip"}
MAX_GEOJSON_PAGE_SIZE = 2_000
MAX_LAYER_PAGE_SIZE = 5_000


@api.errorhandler(SQLAlchemyError)
def database_error(_error):
    db.session.rollback()
    current_app.logger.exception("Une requête PostgreSQL/PostGIS a échoué.")
    return jsonify({"error": "La base PostgreSQL/PostGIS est indisponible ou non initialisée."}), 503


@api.errorhandler(413)
def upload_too_large(_error):
    return jsonify({"error": "Le fichier dépasse la taille maximale autorisée (50 Mo)."}), 413


def _geojson_response(frame):
    return current_app.response_class(
        frame.to_json(drop_id=True, to_wgs84=True),
        mimetype="application/geo+json",
    )


def _int_arg(name, default, minimum, maximum):
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default
    return min(max(value, minimum), maximum)


@api.get("/health")
def health():
    try:
        postgis_version = db.session.scalar(text("SELECT PostGIS_Full_Version()"))
        return jsonify({"status": "ok", "database": "connected", "postgis": postgis_version})
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("La vérification PostgreSQL/PostGIS a échoué.")
        return jsonify({"status": "unavailable", "database": "disconnected"}), 503


@api.get("/dashboard/stats")
def dashboard_stats():
    try:
        communes = db.session.scalar(select(func.count()).select_from(Commune)) or 0
        quartiers = db.session.scalar(select(func.count()).select_from(Quartier)) or 0
        layers = db.session.scalar(select(func.count()).select_from(GeoLayer)) or 0
        geojson_files = db.session.scalar(
            select(func.count()).select_from(GeoLayer).where(GeoLayer.source_format.in_(["geojson", "json"]))
        ) or 0
        return jsonify({
            "communes": communes,
            "quartiers": quartiers,
            "layers": layers,
            "geojson_files": geojson_files,
            "users": None,
        })
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Lecture des statistiques impossible.")
        return jsonify({"error": "Le schéma de la base n’est pas initialisé."}), 503


@api.get("/communes")
def communes_geojson():
    frame = gpd.read_postgis(
        text("SELECT id, name, geom FROM communes ORDER BY name"),
        con=db.engine,
        geom_col="geom",
    )
    return _geojson_response(frame)


@api.get("/quartiers")
def quartiers_geojson():
    limit = _int_arg("limit", MAX_GEOJSON_PAGE_SIZE, 1, MAX_GEOJSON_PAGE_SIZE)
    offset = _int_arg("offset", 0, 0, 10_000_000)
    frame = gpd.read_postgis(
        text("SELECT id, name, commune_name, geom FROM quartiers ORDER BY name LIMIT :limit OFFSET :offset"),
        con=db.engine,
        geom_col="geom",
        params={"limit": limit, "offset": offset},
    )
    return _geojson_response(frame)


@api.get("/layers")
def list_layers():
    layers = db.session.scalars(select(GeoLayer).order_by(GeoLayer.created_at.desc())).all()
    return jsonify({"items": [layer.to_dict() for layer in layers]})


@api.post("/layers")
def create_layer():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Sélectionnez un fichier géographique à importer."}), 400

    filename = secure_filename(uploaded.filename)
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Formats acceptés : GeoJSON, GeoPackage ou ZIP de shapefile."}), 415

    layer_name = (request.form.get("name") or Path(filename).stem).strip()
    if not layer_name:
        return jsonify({"error": "Le nom de la couche est obligatoire."}), 400

    try:
        with tempfile.TemporaryDirectory(prefix="abj-gis-") as temp_dir:
            path = Path(temp_dir) / filename
            uploaded.save(path)
            layer = import_layer(
                path,
                name=layer_name,
                requested_crs=request.form.get("crs"),
            )
            db.session.commit()
        return jsonify(layer.to_dict()), 201
    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 422
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Enregistrement de la couche dans PostGIS impossible.")
        return jsonify({"error": "Impossible d’enregistrer la couche dans PostgreSQL/PostGIS."}), 503
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Import géographique échoué.")
        return jsonify({"error": "Le fichier n’a pas pu être lu ou converti."}), 422


@api.get("/layers/<string:layer_id>/features")
def layer_features(layer_id):
    layer = db.session.get(GeoLayer, layer_id)
    if layer is None:
        return jsonify({"error": "Couche introuvable."}), 404
    if not re.fullmatch(r"layer_[0-9a-f]{32}", layer.table_name):
        current_app.logger.error("Nom de table spatial inattendu pour la couche %s", layer.id)
        return jsonify({"error": "La couche ne peut pas être lue."}), 500

    limit = _int_arg("limit", 1_000, 1, MAX_LAYER_PAGE_SIZE)
    offset = _int_arg("offset", 0, 0, 10_000_000)
    statement = text(
        f'SELECT feature_id, properties, geom FROM "{layer.table_name}" '
        "ORDER BY feature_id LIMIT :limit OFFSET :offset"
    )
    frame = gpd.read_postgis(
        statement,
        con=db.engine,
        geom_col="geom",
        params={"limit": limit, "offset": offset},
    )
    collection = json.loads(frame.to_json(drop_id=True, to_wgs84=True))
    for feature in collection["features"]:
        raw_properties = feature["properties"].get("properties")
        feature["properties"] = json.loads(raw_properties) if raw_properties else {}
    collection["numberReturned"] = len(collection["features"])
    collection["numberMatched"] = layer.feature_count
    return jsonify(collection)
