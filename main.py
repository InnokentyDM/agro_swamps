from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware
from pydantic.main import BaseModel

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


class GeoData(BaseModel):
    geo_data: str


@app.post("/analyze_bounds")
async def analyze_bounds(geo_data: GeoData):
    # Координаты точек, которые приходят с карты
    # Тут нужно вызвать код для анализа и вернуть dict с geojson данными,
    # которые отобразятся на карте
    # bermuda для примера
    bermuda = {
        "type": "Feature",
        "properties": {
            "name": "Bermuda Triangle",
            "area": 1150180
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-64.73, 32.31],
                    [-80.19, 25.76],
                    [-66.09, 18.43],
                    [-64.73, 32.31]
                ]
            ]
        }
    }
    return bermuda
