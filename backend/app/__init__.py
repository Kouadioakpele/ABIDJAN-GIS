import os
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from sqlalchemy import text

from .extensions import db


def create_app(test_config=None):
    backend_dir = Path(__file__).resolve().parents[1]
    load_dotenv(backend_dir / ".env")

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://abj_gis:abj_gis_dev_password@localhost:5432/abidjan_gis",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024))),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    origins = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    from . import models  # noqa: F401
    from .api import api

    app.register_blueprint(api, url_prefix="/api")

    @app.cli.command("init-db")
    def init_db_command():
        """Enable PostGIS and create the initial tables."""
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        db.create_all()
        db.session.commit()
        click.echo("Schéma PostgreSQL/PostGIS initialisé.")

    @app.cli.command("seed-abidjan")
    @click.option(
        "--file",
        "dataset_path",
        type=click.Path(exists=True, path_type=Path),
        default=backend_dir / "data" / "Quartier_Abidjan.shp",
        show_default=True,
        help="Chemin vers le shapefile des quartiers.",
    )
    def seed_abidjan_command(dataset_path):
        """Load the supplied Abidjan neighbourhood data into PostGIS."""
        from .services.geodata import seed_abidjan_dataset

        try:
            counts = seed_abidjan_dataset(dataset_path)
        except (ValueError, FileNotFoundError) as error:
            raise click.ClickException(str(error)) from error
        click.echo(f"Données chargées : {counts['communes']} communes, {counts['quartiers']} quartiers.")

    return app
