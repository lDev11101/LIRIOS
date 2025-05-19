from flask import Flask, render_template
from .routes import register_blueprints
import mysql.connector
from dotenv import load_dotenv
import os


def create_app():
    app = Flask(__name__)

    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")

    try:
        db_conect = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        app.config["db_conexion"] = db_conect
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        raise

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    register_blueprints(app)
    return app
