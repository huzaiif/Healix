import os
import requests
from dotenv import load_dotenv

load_dotenv()

# We provide some high-quality placeholder images since the Geoapify Places API does not return images
FALLBACK_IMAGES = {
    "hospital": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&auto=format&fit=crop&q=60",
    "clinic": "https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?w=800&auto=format&fit=crop&q=60",
    "doctor": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&auto=format&fit=crop&q=60"
}

def get_care_type_and_category(risk_level: str):
    """Maps the string risk level to a Geoapify healthcare category and our local care type string."""
    risk = risk_level.lower() if risk_level else "unknown"
    if risk in ["high", "critical", "severe"]:
        return "Hospital", "healthcare.hospital", FALLBACK_IMAGES["hospital"]
    elif risk in ["moderate", "medium"]:
        return "Clinic", "healthcare.clinic_or_polyclinic", FALLBACK_IMAGES["clinic"]
    else:
        # Default for Low, Stable, Unknown
        return "Doctor / General Physician", "healthcare.doctor", FALLBACK_IMAGES["doctor"]

def get_healthcare_recommendations(location: str, risk_level: str, disease: str):
    """
    Geocodes the location, finds nearest healthcare centers based on risk level,
    and returns a formatted list of recommendations.
    """
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        return {"error": "GEOAPIFY_API_KEY is missing from .env"}

    # 1. Geocode location
    geocode_url = f"https://api.geoapify.com/v1/geocode/search?text={location}&apiKey={api_key}"
    try:
        geo_response = requests.get(geocode_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get("features"):
            return {"error": "Location not found. Please try entering a more specific city or zip code."}
            
        coords = geo_data["features"][0]["geometry"]["coordinates"]
        lon, lat = coords[0], coords[1]
    except Exception as e:
        return {"error": f"Failed to geocode location: {str(e)}"}

    # 2. Get Places
    care_type_str, category, image_url = get_care_type_and_category(risk_level)
    radius_meters = 50000  # 50km
    
    places_url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{lon},{lat},{radius_meters}&limit=3&apiKey={api_key}"
    try:
        places_response = requests.get(places_url)
        places_response.raise_for_status()
        places_data = places_response.json()
        
        features = places_data.get("features", [])
        if not features:
            return {"error": f"No {care_type_str.lower()}s found within 50km of this location."}
            
        recommendations = []
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("name")
            if not name:
                name = f"Local {care_type_str}"
                
            address = props.get("address_line2", props.get("formatted", "Address not available"))
            # convert meters to miles roughly
            distance_meters = props.get("distance", 0)
            distance_miles = round(distance_meters * 0.000621371, 1)
            
            p_lat = props.get("lat")
            p_lon = props.get("lon")
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            
            reason = f"Recommended for {risk_level.lower()} risk {disease} management."
            
            recommendations.append({
                "name": name,
                "address": address,
                "distance_miles": distance_miles,
                "care_type": care_type_str,
                "reason": reason,
                "image_url": image_url,
                "maps_url": maps_url
            })
            
        return {"success": True, "data": recommendations}
        
    except Exception as e:
        return {"error": f"Failed to retrieve places: {str(e)}"}
