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
    return routine(geo_data)

import mercantile
import requests # The requests package allows use to call URLS
import shutil   # shutil will be used to copy the image to the local
import PIL
import PIL.Image
import math
from os import listdir
from os.path import isfile, join
import numpy as np
import rasterio.features
from geojson import Polygon, Feature, FeatureCollection
import os

def routine(geo_data: GeoData):
    rect = eval(geo_data.geo_data)
    tl = [rect[1][0], rect[0][1]]
    br = [rect[0][0], rect[1][1]]
    z = 14


    tl_tiles = mercantile.tile(tl[1],tl[0],z)
    br_tiles = mercantile.tile(br[1],br[0],z)

    x_tile_range = [tl_tiles.x,br_tiles.x];print(x_tile_range)
    y_tile_range = [tl_tiles.y,br_tiles.y];print(y_tile_range)

    origin = mercantile.ul(x_tile_range[0], y_tile_range[0], z)
    bounds = mercantile.bounds(x_tile_range[-1], y_tile_range[-1], z)
    bottomright = (bounds.east, bounds.south)

    os.system('rm -rf ./satellite_images')
    os.system('rm -rf ./elevation_images')
    os.system('rm -rf ./composite_images')

    os.system('mkdir ./elevation_images')
    os.system('mkdir ./satellite_images')
    os.system('mkdir ./composite_images')

    # Loop over the tile ranges
    for i,x in enumerate(range(x_tile_range[0],x_tile_range[1]+1)):
        for j,y in enumerate(range(y_tile_range[0],y_tile_range[1]+1)):
            # Call the URL to get the image back
            r = requests.get('https://api.mapbox.com/v4/mapbox.terrain-rgb/'+str(z)+'/'+str(x)+'/'+str(y)+'@2x.pngraw?access_token=pk.eyJ1IjoibWFyYXRzYXJiYXNvdiIsImEiOiJja2lscjNrbHkwa3F6MzJwOXNkaWtvNXZoIn0.5sDejBO1mrR1k3L8Pv1KWw', stream=True)
            # Next we will write the raw content to an image
            with open('./elevation_images/' + str(i) + '.' + str(j) + '.png', 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f) 
            # Do the same for the satellite data
            r = requests.get('https://api.mapbox.com/v4/mapbox.satellite/'+str(z)+'/'+str(x)+'/'+str(y)+'@2x.pngraw?access_token=pk.eyJ1IjoibWFyYXRzYXJiYXNvdiIsImEiOiJja2lscjNrbHkwa3F6MzJwOXNkaWtvNXZoIn0.5sDejBO1mrR1k3L8Pv1KWw', stream=True)
            with open('./satellite_images/' + str(i) + '.' + str(j) + '.png','wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    for img_name in ['satellite', 'elevation']:
        image_files = ['./'+img_name+'_images/' + f for f in listdir('./'+img_name+'_images/')]
        images = [PIL.Image.open(x) for x in image_files]

        edge_length_x = x_tile_range[1] + 1 - x_tile_range[0]
        edge_length_y = y_tile_range[1] + 1 - y_tile_range[0]
        edge_length_x = max(1,edge_length_x)
        edge_length_y = max(1,edge_length_y)
        width, height = images[0].size

        total_width = width*edge_length_x
        total_height = height*edge_length_y

        composite = PIL.Image.new('RGB', (total_width, total_height))
        print(total_width,total_height)

    #     anim_idx = 0
        y_offset = 0
        for i in range(0,edge_length_x):
            x_offset = 0
            for j in range(0,edge_length_y):
                tmp_img = PIL.Image.open('./'+img_name+'_images/' + str(i) + '.' + str(j) + '.png')
                composite.paste(tmp_img, (y_offset,x_offset))
                x_offset += width
                # composite.save('./animate/'+str(anim_idx).zfill(4)+'.jpg',optimize=True,quality=95)
    #             anim_idx += 1
    #             print(anim_idx)

                
            y_offset += height

        composite.save('./composite_images/'+img_name+'.png')
        
        for i in images:
            i.close()


    elevation = PIL.Image.open('./composite_images/elevation.png')
    elevationColourArray = np.array(elevation.getdata())


    def color_to_height(x):
        return -10000 + ((x[0] * 256 * 256 + x[1] * 256 + x[2]) * 0.1)

    heights = list(map(color_to_height, elevationColourArray))
    heights = np.array(heights).reshape(-1, elevation.width)

    def normalize_array(arr):
        mini = arr.min()
        maxi = arr.max()
        def normalize(x):
            return (x - mini) / (maxi - mini)
        return list(map(normalize, arr))

    normalized_heights = normalize_array(heights)
    normalized_heights = np.stack(normalized_heights, axis=0)


    satellite = PIL.Image.open('./composite_images/satellite.png')
    satelliteColourArray = np.array(elevation.getdata())
    def color_to_brightness(x):
        return 0.2126*x[0] + 0.7152*x[1] + 0.0722*x[2]

    brightness = list(map(color_to_brightness, satelliteColourArray))
    brightness = np.array(brightness).reshape(-1, satellite.width)

    normalized_brightness = normalize_array(brightness)
    normalized_brightness = np.stack(normalized_brightness, axis=0)

    h_median = np.median(normalized_heights)
    b_median = np.median(normalized_brightness)
    def isSwamp(h, b):
        if (h + b) < (h_median + b_median) :
            return True
        return False
    vectIsSwamp = np.vectorize(isSwamp)
    swamp = vectIsSwamp(normalized_heights, normalized_brightness)

    polygons = rasterio.features.shapes(swamp.astype('uint8')*255, mask=swamp.astype('uint8'))
    polygons = list(polygons)
    polygons = list(map(lambda x: x[0], polygons))

    x_coef = (bottomright[0] - origin[0]) / swamp.shape[1]
    y_coef = (bottomright[1] - origin[1]) / swamp.shape[0]
    for i in range(len(polygons)):
        for j in range(len(polygons[i]['coordinates'])):
            for ti in range(len(polygons[i]['coordinates'][j])):
                old = polygons[i]['coordinates'][j][ti]
                polygons[i]['coordinates'][j][ti] = (origin.lng + old[0] * x_coef, origin.lat + old[1] * y_coef)


    geopolygons = list(map(lambda x: Feature(geometry=x), polygons))
    featurecoll = FeatureCollection(geopolygons)
    # with open('myfile.geojson', 'w') as f:
    #     geojson.dump(featurecoll, f)

    return featurecoll

