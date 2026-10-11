
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import math

app = FastAPI()

# Allow POST requests from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry: (region, latency_ms, uptime_pct)
DATA = [
    ("apac", 150.65, 98.288), ("apac", 162.99, 99.212),
    ("apac", 200.08, 99.343), ("apac", 115.89, 99.217),
    ("apac", 172.43, 98.526), ("apac", 220.01, 99.083),
    ("apac", 155.51, 98.918), ("apac", 187.01, 99.022),
    ("apac", 172.06, 98.072), ("apac", 200.58, 98.002),
    ("apac", 208.51, 98.281), ("apac", 170.32, 98.949),

    ("emea", 190.54, 98.781), ("emea", 174.34, 98.235),
    ("emea", 159.67, 97.653), ("emea", 179.17, 97.895),
    ("emea", 123.68, 99.033), ("emea", 214.44, 97.516),
    ("emea", 136.49, 98.916), ("emea", 119.63, 98.260),
    ("emea", 152.98, 97.605), ("emea", 237.84, 97.147),
    ("emea", 133.34, 97.323), ("emea", 150.38, 99.466),

    ("amer", 127.70, 98.797), ("amer", 223.83, 98.875),
    ("amer", 141.31, 99.468), ("amer", 127.15, 98.341),
    ("amer", 232.75, 99.177), ("amer", 124.07, 97.935),
    ("amer", 191.71, 98.523), ("amer", 226.91, 98.960),
    ("amer", 153.43, 98.799), ("amer", 123.09, 99.105),
    ("amer", 202.01, 98.544), ("amer", 178.52, 97.171),
]


class Request(BaseModel):
    regions: List[str]
    threshold_ms: float = 180


def percentile95(values):
    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = 0.95 * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)

    return values[lower] + (
        values[upper] - values[lower]
    ) * (position - lower)


@app.get("/")
def read_root():
    return {"message": "Latency API is running"}


@app.post("/api/latency")
def latency(request: Request):
    result = {}

    for region in request.regions:
        records = [
            record for record in DATA
            if record[0].lower() == region.lower()
        ]

        if not records:
            continue

        latencies = [record[1] for record in records]
        uptimes = [record[2] for record in records]

        result[region] = {
            "avg_latency": round(
                sum(latencies) / len(latencies), 2
            ),
            "p95_latency": round(
                percentile95(latencies), 2
            ),
            "avg_uptime": round(
                sum(uptimes) / len(uptimes), 3
            ),
            "breaches": sum(
                value > request.threshold_ms
                for value in latencies
            ),
        }

    return result
