# Getaround — Delay Analysis & Pricing Optimization (Deployment Project)

It covers both **data analysis for delay management** and a **machine learning API for pricing optimization**, deployed online with **Streamlit dashboards** and a **/predict endpoint**.

This repository contains two main components:  

1. **Delay Analysis Dashboard**: data analysis on late returns and rental overlaps, deployed as a Streamlit web app.  
2. **Pricing Optimization**: a Machine Learning pipeline deployed as both a REST API (FastAPI) and a user-facing Streamlit app.  

Both are hosted in production on Hugging Face Spaces.  

---

## 1. Delay Analysis (Streamlit Dashboard)

### Purpose
Quantify the operational and financial impact of late returns and test policies for enforcing a minimum delay between rentals.  

### Analyses implemented
- Percentage of owner revenue affected by enforcing different delay thresholds.  
- Number of rentals blocked under various configurations (all cars vs. *Connect* cars only).  
- Distribution of late check-ins and impact on the next driver.  
- Estimation of problematic cases resolved by different policy thresholds.  

### Deployment
- **Production app**: [Streamlit Delay Analysis](https://huggingface.co/spaces/sony9316/Streamlit-delay-analysis)  
- **Source code**: `Delay_analysis_dashboard_Streamlit/`  
- **Replication**: deploy the folder on Hugging Face Spaces using a **Streamlit template**.  

---

## 2. Pricing Optimization (Machine Learning Model)

### Purpose
Train and deploy a supervised ML model to predict optimal rental prices based on car specifications and equipment.  

### API (FastAPI)
- **Endpoint**: [POST /predict](https://sony9316-getaround-pricing-api.hf.space/predict)  
- **Swagger Docs**: [API Documentation](https://sony9316-getaround-pricing-api.hf.space/docs)  
- **Source code**: `ML_pricing_prediction_API/`  
- **Deployment**: Hugging Face Spaces with **Docker template**.  

### Example API request (inference)

```python
import requests

payload = {
    "input": [{
        "model_key": "Peugeot",
        "mileage": 174631,
        "engine_power": 120,
        "fuel": "diesel",
        "paint_color": "black",
        "car_type": "convertible",
        "private_parking_available": True,
        "has_gps": True,
        "has_air_conditioning": True,
        "automatic_car": False,
        "has_getaround_connect": True,
        "has_speed_regulator": True,
        "winter_tires": False
    }]
}

response = requests.post(
    "https://sony9316-getaround-pricing-api.hf.space/predict",
    json=payload
)

print(response.json())
