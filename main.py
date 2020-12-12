from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get_initial_dataset")
async def get_initial_dataset():
    with open('Marshes.geojson', 'r') as file:
        response_data = file.read()
        return response_data


@app.get("/submit_geojson")
async def submit_geojson():
    pass