import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2
import openrouteservice
from streamlit_javascript import st_javascript

# Funkcija za računanje udaljenosti
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Inicijalizacija OpenRouteService API
ORS_API_KEY = '5b3ce3597851110001cf62487c119d71037c4e1f983491d829c400f4'
client = openrouteservice.Client(key=ORS_API_KEY)

# Učitavanje podataka
df = pd.read_csv('chargers_london.csv')

# Stilovi
st.markdown("""
<style>
.main {
    background-color: #f0f2f6;
}
h1 {
    color: #2e7d32;
    text-align: center;
}
.stButton>button {
    background-color: #4caf50;
    color: white;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Naslov
st.title("ChargeSmart - Find Your EV Charger")

# Sesijsko stanje za lokaciju
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = 51.5074  # Podrazumevani London
if 'user_lon' not in st.session_state:
    st.session_state.user_lon = -0.1278

# Dugme za dobijanje lokacije
if st.button("Get My Location"):
    # JavaScript za dobijanje lokacije
    location = st_javascript("""
        new Promise((resolve, reject) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({lat: position.coords.latitude, lon: position.coords.longitude});
                    },
                    (error) => {
                        reject(error.message);
                    }
                );
            } else {
                reject("Geolocation not supported.");
            }
        });
    """)
    # Provera da li je lokacija dobijena
    if isinstance(location, dict) and 'lat' in location and 'lon' in location:
        st.session_state.user_lat = location['lat']
        st.session_state.user_lon = location['lon']
        st.query_params['lat'] = str(location['lat'])
        st.query_params['lon'] = str(location['lon'])
    elif isinstance(location, str):
        st.error(f"Error: {location}")
    else:
        st.error("Unable to retrieve location.")

# Provera query parametara
query_params = st.query_params
if 'lat' in query_params and 'lon' in query_params:
    st.session_state.user_lat = float(query_params['lat'])
    st.session_state.user_lon = float(query_params['lon'])

# Unos lokacije
st.write("Your Location:")
user_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=st.session_state.user_lat, key="lat")
user_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=st.session_state.user_lon, key="lon")
st.session_state.user_lat = user_lat
st.session_state.user_lon = user_lon

# Pronalaženje najbliže slobodne punionice
free_chargers = df[df['Status'] == 'Free'].copy()
if not free_chargers.empty:
    free_chargers['Distance'] = free_chargers.apply(
        lambda row: calculate_distance(user_lat, user_lon, row['Latitude'], row['Longitude']),
        axis=1
    )
    nearest_charger = free_chargers.loc[free_chargers['Distance'].idxmin()]
    st.write("Nearest Free Charging Station:")
    st.write(f"- {nearest_charger['Name']} at {nearest_charger['Latitude']}, {nearest_charger['Longitude']}")
    st.write(f"Distance: {nearest_charger['Distance']:.2f} km")

    # Ruta do najbliže punionice koristeći OpenRouteService
    try:
        coords = [[user_lon, user_lat], [nearest_charger['Longitude'], nearest_charger['Latitude']]]
        route = client.directions(coordinates=coords, profile='driving-car', format='json')
        if route:
            distance = route['routes'][0]['summary']['distance'] / 1000  # U km
            duration = route['routes'][0]['summary']['duration'] / 60  # U minutima
            st.write("Directions to the Charger:")
            st.write(f"Total Distance: {distance:.2f} km")
            st.write(f"Estimated Time: {duration:.2f} minutes")
            steps = route['routes'][0]['segments'][0]['steps']
            for i, step in enumerate(steps, 1):
                instruction = step['instruction']
                st.write(f"Step {i}: {instruction}")
        else:
            st.write("No directions available.")
    except Exception as e:
        st.write(f"Error fetching directions: {str(e)}")
else:
    st.write("No free charging stations available.")

# Mapa
m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
for index, row in df.iterrows():
    color = 'green' if row['Status'] == 'Free' else 'red'
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['Name']} - {row['Status']}",
        icon=folium.Icon(color=color)
    ).add_to(m)
folium.Marker(
    location=[user_lat, user_lon],
    popup="Your Location",
    icon=folium.Icon(color='blue')
).add_to(m)
st.write("Charging Stations Map:")
st_folium(m, width=700, height=500)