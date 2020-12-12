from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware

from settings import settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request":
                                                         request, "gmap_key":
                                                         settings.gmap_key})


@app.get("/get_initial_dataset")
async def get_initial_dataset():
    with open('static/Marshes.geojson', 'r') as file:
        response_data = file.read()
        return response_data


@app.post("/analyze_bounds")
async def analyze_bounds():
    pass
