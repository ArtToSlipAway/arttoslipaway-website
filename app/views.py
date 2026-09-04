from fastapi.templating import Jinja2Templates
from app.paths import TEMPLATES_DIR
import os

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["demo_mode"] = os.getenv("DEMO_MODE", "false").lower() == "true"
