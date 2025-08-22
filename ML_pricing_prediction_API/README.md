---
title: Pricing Optimization API
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Pricing Optimization API

This is a production-ready **FastAPI** service that serves your **scikit-learn Pipeline**.
It exposes:
- `POST /predict` — batch predictions
- `GET /docs` — interactive Swagger UI
- `GET /` — simple health check

## Why this setup?
- The saved artifact `RF_model.joblib` contains both preprocessing and the model, so serving is consistent with training.
- The API accepts mixed types (strings/ints/bools/floats) and converts them into a **pandas DataFrame** with the **exact** column names used at training, allowing `ColumnTransformer` to work reliably.

## Expected input format
- Body: `{"input": [[f1, f2, ..., fN], ...]}` — 2D list (batch of rows).
- **Order matters**: the order must match `feature_names` saved in your bundle.
- Booleans must be JSON booleans (`true`/`false`) — not strings.

**Example**
```json
{
  "input": [[
    "Peugeot",
    174631,
    120,
    "diesel",
    "black",
    "convertible",
    true,
    true,
    false,
    false,
    false,
    false,
    true
  ]]
}
