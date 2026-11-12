from datetime import datetime, timezone

from geoalchemy2 import Geometry

from .extensions import db


class Commune(db.Model):
    __tablename__ = "communes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    geom = db.Column(Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False)


class Quartier(db.Model):
    __tablename__ = "quartiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    commune_name = db.Column(db.String(120), nullable=False, index=True)
    geom = db.Column(Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False)


class GeoLayer(db.Model):
    __tablename__ = "geo_layers"

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    source_filename = db.Column(db.String(255), nullable=False)
    source_format = db.Column(db.String(20), nullable=False, index=True)
    source_crs = db.Column(db.String(100), nullable=False)
    geometry_type = db.Column(db.String(80), nullable=False)
    table_name = db.Column(db.String(80), nullable=False, unique=True)
    feature_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source_filename": self.source_filename,
            "source_format": self.source_format,
            "source_crs": self.source_crs,
            "geometry_type": self.geometry_type,
            "feature_count": self.feature_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
