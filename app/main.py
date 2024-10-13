from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routes.admin import router as admin
from app.routes.archives import router as archives
from app.routes.auth import router as auth
from app.routes.contact import router as contact
from app.routes.user import router as user
from app.routes.experiments import router as experiments
from app.routes.measurements import router as measurements
from app.routes.pages import router as pages
from app.routes.samples import router as samples
from app.services.middleware import AuthMiddleware
from app.services.resources import static_files
from app.services.tasks import create_admin_user

create_admin_user()

app = FastAPI()

app.include_router(auth)
app.include_router(pages)
app.include_router(user)
app.include_router(samples)
app.include_router(experiments)
app.include_router(archives)
app.include_router(measurements)
app.include_router(contact)
app.include_router(admin)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", static_files, name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")
