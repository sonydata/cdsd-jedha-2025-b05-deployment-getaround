# pricing_app.py
import streamlit as st
import requests
import json

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Getaround Rental Pricing Prediction",
    #page_icon="🚗",
    layout="centered"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .prediction-result {
        background-color: #d4edda;
        padding: 2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        text-align: center;
        margin: 2rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== API CONFIGURATION ==========
API_URL = "https://sony9316-getaround-pricing-api.hf.space/predict"

# ========== MAIN APP ==========
st.markdown('<h1 class="main-header">🚗 Prédiction du prix de location</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
Remplissez les informations suivantes pour obtenir une estimation du prix de location par jour.
</div>
""", unsafe_allow_html=True)

# ========== FORM INPUTS ==========
with st.form("prediction_form"):
    st.markdown("### Caractéristiques du véhicule")
    
    # Car model
    model_key = st.selectbox(
        "Modèle de voiture",
        options=["Peugeot", "Audi", "BMW", "Volkswagen", "Mercedes", "Ford", "Opel", "Renault", "Toyota", "Nissan"],
        index=0
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mileage
        mileage = st.number_input(
            "Kilométrage", 
            min_value=0, 
            max_value=500000, 
            value=50000,
            step=1000
        )
        
        # Engine power
        engine_power = st.number_input(
            "Puissance moteur (CV)", 
            min_value=50, 
            max_value=500, 
            value=100,
            step=10
        )
        
        # Fuel type
        fuel = st.selectbox(
            "Type de carburant",
            options=["diesel", "petrol", "electric", "hybrid"],
            index=0
        )
    
    with col2:
        # Paint color
        paint_color = st.selectbox(
            "Couleur",
            options=["black", "white", "grey", "blue", "red", "silver", "brown", "green"],
            index=0
        )
        
        # Car type
        car_type = st.selectbox(
            "Type de voiture",
            options=["sedan", "convertible", "suv", "coupe", "estate", "hatchback"],
            index=0
        )
    
    st.markdown("### Équipements et options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        private_parking_available = st.checkbox("Parking privé disponible", value=True)
        has_gps = st.checkbox("GPS", value=True)
        has_air_conditioning = st.checkbox("Climatisation", value=True)
        automatic_car = st.checkbox("Boîte automatique", value=False)
    
    with col2:
        has_getaround_connect = st.checkbox("Getaround Connect", value=True)
        has_speed_regulator = st.checkbox("Régulateur de vitesse", value=True)
        winter_tires = st.checkbox("Pneus hiver", value=False)
    
    # Submit button
    submitted = st.form_submit_button("Prédire le prix optimal", use_container_width=True)

# ========== API CALL AND RESULTS ==========
if submitted:
    # Prepare the data for API call
    data = {
        "input": [
            {
                "model_key": model_key,
                "mileage": mileage,
                "engine_power": engine_power,
                "fuel": fuel,
                "paint_color": paint_color,
                "car_type": car_type,
                "private_parking_available": private_parking_available,
                "has_gps": has_gps,
                "has_air_conditioning": has_air_conditioning,
                "automatic_car": automatic_car,
                "has_getaround_connect": has_getaround_connect,
                "has_speed_regulator": has_speed_regulator,
                "winter_tires": winter_tires,
            }
        ]
    }
    
    try:
        with st.spinner("Prédiction en cours..."):
            # Make API request
            response = requests.post(API_URL, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                predicted_price = result["prediction"][0]
                
                st.markdown(f"""
                <div class="prediction-result">
                <h2>💰 Prix estimé</h2>
                <h1 style="color: #28a745; margin: 1rem 0;">{predicted_price:.2f} € / jour</h1>
                <p>Prix de location journalier recommandé pour ce véhicule</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display summary of inputs
                with st.expander("📋 Résumé des caractéristiques"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Modèle:** {model_key}")
                        st.write(f"**Kilométrage:** {mileage:,} km")
                        st.write(f"**Puissance:** {engine_power} CV")
                        st.write(f"**Carburant:** {fuel}")
                        st.write(f"**Couleur:** {paint_color}")
                        st.write(f"**Type:** {car_type}")
                    
                    with col2:
                        st.write(f"**Parking privé:** {'Oui' if private_parking_available else 'Non'}")
                        st.write(f"**GPS:** {'Oui' if has_gps else 'Non'}")
                        st.write(f"**Climatisation:** {'Oui' if has_air_conditioning else 'Non'}")
                        st.write(f"**Boîte auto:** {'Oui' if automatic_car else 'Non'}")
                        st.write(f"**Connect:** {'Oui' if has_getaround_connect else 'Non'}")
                        st.write(f"**Régulateur:** {'Oui' if has_speed_regulator else 'Non'}")
                
            else:
                st.markdown(f"""
                <div class="error-box">
                <strong>Erreur API ({response.status_code}):</strong> {response.text}
                </div>
                """, unsafe_allow_html=True)
                
    except requests.exceptions.RequestException as e:
        st.markdown(f"""
        <div class="error-box">
        <strong>Erreur de connexion:</strong> Impossible de contacter l'API de prédiction.
        <br><small>Détails: {str(e)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
        <strong>Erreur:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)

# ========== SIDEBAR INFO ==========
with st.sidebar:
    st.markdown("## ℹ️ Information")
    st.markdown("""
    Cette application utilise un modèle de machine learning pour prédire 
    le prix optimal de location d'un véhicule basé sur ses caractéristiques.
    """)
    
    st.markdown("### 🔗 API")
    st.markdown(f"**Endpoint:** [Hugging Face Space]({API_URL.replace('/predict', '')})")
    
    st.markdown("### 📊 Modèle")
    st.markdown("Random Forest optimisé pour la prédiction de prix")
    
    with st.expander("🔧 Caractéristiques utilisées"):
        features = [
            "Modèle de voiture",
            "Kilométrage", 
            "Puissance moteur",
            "Type de carburant",
            "Couleur",
            "Type de véhicule",
            "Parking privé",
            "GPS",
            "Climatisation", 
            "Boîte automatique",
            "Getaround Connect",
            "Régulateur de vitesse",
            "Pneus hiver"
        ]
        for i, feature in enumerate(features, 1):
            st.write(f"{i}. {feature}")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
<p><strong>Getaround Pricing Optimization</strong> - Powered by Machine Learning</p>
</div>
""", unsafe_allow_html=True)