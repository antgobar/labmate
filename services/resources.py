import os

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

CURRENT_DIRECTORY = os.getcwd()
templates = Jinja2Templates(directory=os.path.join(CURRENT_DIRECTORY, "templates"))
static_files = StaticFiles(directory=os.path.join(CURRENT_DIRECTORY, "static"))
