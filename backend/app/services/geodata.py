import json
import math
import uuid
from pathlib import Path

import geopandas as gpd
import pandas as pd
from geoalchemy2 import Geometry
from shapely import force_2d, make_valid

from ..extensions import db
from ..models import Commune, GeoLayer, Quartier


MAX_FEATURES = 100_000


def _json_value(value):
    if value is None:
        return None
    if hasattr(value, "item"):
        return _json_value(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _normalized_frame(frame, requested_crs=None):
    if frame.empty or frame.geometry.name not in frame.columns:
        raise ValueError("Le fichier ne contient aucune géométrie exploitable.")

    if frame.crs is None:
        if not requested_crs:
            raise ValueError("Le système de coordonnées est absent. Indiquez le champ CRS (ex. EPSG:4326).")
        frame = frame.set_crs(requested_crs)

    source_crs = frame.crs.to_string()
    frame = frame.to_crs(epsg=4326)
    frame = frame.loc[frame.geometry.notna()].copy()
    frame.geometry = frame.geometry.apply(lambda geom: force_2d(make_valid(geom)) if not geom.is_valid else force_2d(geom))
    frame = frame.loc[~frame.geometry.is_empty & frame.geometry.notna()].copy()

    if frame.empty:
        raise ValueError("Aucune géométrie valide n’a été trouvée dans ce fichier.")
    if len(frame) > MAX_FEATURES:
        raise ValueError(f"Le fichier dépasse la limite de {MAX_FEATURES} entités.")

    return frame, source_crs


def _store_layer(frame, *, name, filename, source_format, source_crs):
    geometry_name = frame.geometry.name
    attribute_columns = [column for column in frame.columns if column != geometry_name]
    property_rows = frame[attribute_columns].to_dict(orient="records")
    properties = [
        json.dumps({key: _json_value(value) for key, value in row.items()}, ensure_ascii=False)
        for row in property_rows
    ]

    table_name = f"layer_{uuid.uuid4().hex}"
    upload_frame = gpd.GeoDataFrame(
        {
            "feature_id": [uuid.uuid4().hex for _ in range(len(frame))],
            "properties": properties,
        },
        geometry=frame.geometry,
        crs=frame.crs,
    ).rename_geometry("geom")

    upload_frame.to_postgis(
        table_name,
        con=db.session.connection(),
        if_exists="fail",
        index=False,
        geometry_name="geom",
        dtype={"geom": Geometry("GEOMETRY", srid=4326)},
    )

    geometry_types = sorted(frame.geometry.geom_type.dropna().unique().tolist())
    layer = GeoLayer(
        id=uuid.uuid4().hex,
        name=name,
        source_filename=filename,
        source_format=source_format,
        source_crs=source_crs,
        geometry_type=", ".join(geometry_types),
        table_name=table_name,
        feature_count=len(frame),
    )
    db.session.add(layer)
    return layer


def import_layer(path, *, name=None, requested_crs=None):
    path = Path(path)
    source_format = path.suffix.lower().lstrip(".")
    frame = gpd.read_file(path)
    frame, source_crs = _normalized_frame(frame, requested_crs=requested_crs)
    return _store_layer(
        frame,
        name=(name or path.stem).strip()[:180],
        filename=path.name[:255],
        source_format=source_format,
        source_crs=source_crs,
    )


def seed_abidjan_dataset(path):
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Fichier de données introuvable : {source}")

    frame = gpd.read_file(source)
    columns = {str(column).casefold(): column for column in frame.columns}
    quartier_column = columns.get("quartier")
    commune_column = columns.get("ua_1")
    if not quartier_column or not commune_column:
        raise ValueError("Le jeu de données doit contenir les champs 'Quartier' et 'UA_1'.")

    frame, _source_crs = _normalized_frame(frame)
    frame["name"] = frame[quartier_column].fillna("").astype(str).str.strip().str.title()
    frame["commune_name"] = frame[commune_column].fillna("").astype(str).str.strip().str.title()
    frame = frame.loc[(frame.name != "") & (frame.commune_name != "")].copy()
    frame = frame[["name", "commune_name", frame.geometry.name]].copy()
    frame = frame.rename_geometry("geom")

    commune_frame = frame[["commune_name", "geom"]].dissolve(by="commune_name", as_index=False, sort=True)
    commune_frame["name"] = commune_frame["commune_name"]
    commune_frame = commune_frame[["name", "geom"]].set_geometry("geom")

    db.session.query(Quartier).delete(synchronize_session=False)
    db.session.query(Commune).delete(synchronize_session=False)
    connection = db.session.connection()
    frame.to_postgis(
        "quartiers",
        con=connection,
        if_exists="append",
        index=False,
        geometry_name="geom",
        dtype={"geom": Geometry("GEOMETRY", srid=4326)},
    )
    commune_frame.to_postgis(
        "communes",
        con=connection,
        if_exists="append",
        index=False,
        geometry_name="geom",
        dtype={"geom": Geometry("GEOMETRY", srid=4326)},
    )
    db.session.commit()
    return {"communes": len(commune_frame), "quartiers": len(frame)}
