from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="ui"
    )

    app.config["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    app.config["RAPIDAPI_KEY"] = os.getenv("RAPIDAPI_KEY")
    app.config["VEHICLE_DB_API_KEY"] = os.getenv("VEHICLE_DB_API_KEY")
    app.config["TESSERACT_PATH"] = os.getenv("TESSERACT_PATH")

    from .routes import main
    app.register_blueprint(main)

    return app
