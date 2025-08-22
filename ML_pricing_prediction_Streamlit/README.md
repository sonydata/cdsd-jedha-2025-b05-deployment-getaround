---
title: Getaround Pricing Streamlit
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: streamlit_app.py
tags:
- streamlit
- machine-learning
- pricing
- getaround
- car-rental
pinned: false
short_description: AI-powered car rental pricing prediction tool
---

# 🚗 Getaround Pricing Prediction

An interactive Streamlit application for predicting optimal car rental prices using machine learning.

## 🎯 Features

- **Interactive Form**: Easy-to-use interface with car specifications
- **Real-time Predictions**: Instant price estimates via ML API
- **French Interface**: Localized for French users

## 🔧 How it Works

1. **Input car details**: Model, mileage, engine power, fuel type, etc.
2. **Select equipment**: GPS, AC, automatic transmission, Getaround Connect
3. **Get prediction**: AI model calculates optimal daily rental price

## 🚀 Technology Stack

- **Frontend**: Streamlit
- **Backend API**: FastAPI (Random Forest model)
- **Deployment**: Hugging Face Spaces
- **Language**: Python

## 📊 Model Features

The ML model considers 13 key features:
- Vehicle specifications (model, mileage, power)
- Equipment and options (GPS, AC, Connect, etc.)
- Physical attributes (color, type, fuel)

## 🔗 Related Links

- **API Endpoint**: [Getaround Pricing API](https://sony9316-getaround-pricing-api.hf.space)
- **Documentation**: Interactive API docs available

## 💡 Usage

Simply fill out the form with your vehicle's characteristics and click "Prédire le prix" to get an instant price recommendation for your car rental listing.

---

*Powered by Machine Learning • Built with ❤️ for the Getaround community*