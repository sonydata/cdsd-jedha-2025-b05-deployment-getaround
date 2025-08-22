# --- imports ---
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib

# --- Load model bundle ---
BUNDLE_FILE = "RF_model.joblib"
bundle = joblib.load(BUNDLE_FILE)
model = bundle["model"]
feature_names = ['model_key', 'mileage', 'engine_power', 'fuel', 'paint_color', 'car_type',
                 'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car',
                 'has_getaround_connect', 'has_speed_regulator', 'winter_tires']
N = len(feature_names)

# --- Move Swagger UI to /api-docs ---
app = FastAPI(
    title="Pricing Optimization API",
    description="See /api-docs for interactive Swagger UI.",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url=None,
)

# ===== Schemas =====
class CarFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

class PredictRequest(BaseModel):
    input: List[CarFeatures]

class PredictResponse(BaseModel):
    prediction: List[float]

# ===== Endpoints =====
@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "See /docs for API documentation."}

@app.post("/predict", response_model=PredictResponse, tags=["inference"])
def predict(payload: PredictRequest):
    try:
        # Convert list of CarFeatures -> DataFrame in correct order
        rows = [[
            car.model_key,
            car.mileage,
            car.engine_power,
            car.fuel,
            car.paint_color,
            car.car_type,
            car.private_parking_available,
            car.has_gps,
            car.has_air_conditioning,
            car.automatic_car,
            car.has_getaround_connect,
            car.has_speed_regulator,
            car.winter_tires
        ] for car in payload.input]

        X_df = pd.DataFrame(rows, columns=feature_names)
        y_pred = model.predict(X_df).tolist()
        return {"prediction": y_pred}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ===== Custom HTML docs at /docs =====
@app.get("/docs", response_class=HTMLResponse, tags=["documentation"])
def custom_docs():
    feature_rows = "\n".join(
        f"<tr><td>{i+1}</td><td><code>{name}</code></td></tr>"
        for i, name in enumerate(feature_names)
    )

    example_request = """{
  "input": [
    {
      "model_key": "Peugeot",
      "mileage": 174631,
      "engine_power": 120,
      "fuel": "diesel",
      "paint_color": "black",
      "car_type": "convertible",
      "private_parking_available": true,
      "has_gps": true,
      "has_air_conditioning": false,
      "automatic_car": false,
      "has_getaround_connect": false,
      "has_speed_regulator": false,
      "winter_tires": true
    }
  ]
}"""
    example_response = '{ "prediction": [42.0] }'

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Pricing Optimization API — Docs</title>
  <style>
    :root {{ --bg:#fff; --ink:#222; --muted:#666; --line:#e6e6e6; }}
    body {{ background:var(--bg); color:var(--ink); font-family:system-ui, sans-serif; }}
    .wrap {{ max-width:900px; margin:40px auto; padding:0 20px; }}
    h1 {{ margin:0 0 8px; font-size:32px; }}
    p.lead {{ color:var(--muted); margin:0 0 24px; }}
    code, pre {{ background:#f7f7f8; border:1px solid var(--line); border-radius:8px; }}
    pre {{ padding:14px; overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; }}
    th {{ background:#fafafa; }}
    .badge {{ font-size:11px; padding:3px 7px; border-radius:6px; border:1px solid var(--line); }}
    .get {{ background:#eef7ff; border-color:#cfe7ff; }}
    .post {{ background:#eef9f0; border-color:#cfeecd; }}
    a.btn {{ padding:6px 10px; border:1px solid var(--line); border-radius:6px; text-decoration:none; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Pricing Optimization API</h1>
    <p class="lead">Predict optimal daily price for a car given its attributes.</p>

    <h2>Endpoints</h2>
    <p><span class="badge post">POST</span> <code>/predict</code> — Send a list of car feature objects</p>
    <p><span class="badge get">GET</span> <code>/</code> — Health check</p>

    <h2>Expected Feature Order (N = {N})</h2>
    <table>
      <thead><tr><th>#</th><th>Feature</th></tr></thead>
      <tbody>{feature_rows}</tbody>
    </table>

    <h2>Example Request</h2>
    <pre><code>{example_request}</code></pre>

    <h2>Example Response</h2>
    <pre><code>{example_response}</code></pre>

    <p>Interactive API docs: <a class="btn" href="/api-docs">Swagger UI</a></p>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)
