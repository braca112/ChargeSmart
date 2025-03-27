import streamlit as st

st.title("Test Geolocation")

# Sesijsko stanje za lokaciju
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None
if 'status' not in st.session_state:
    st.session_state.status = "Waiting for action..."

# JavaScript za geolokaciju
st.markdown("""
<button id="getLocationBtn">Get My Location</button>
<p id="status">Waiting for action...</p>
<script>
document.getElementById("getLocationBtn").onclick = function() {
    document.getElementById("status").innerText = "Checking geolocation support...";
    if (navigator.geolocation) {
        document.getElementById("status").innerText = "Requesting location...";
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                document.getElementById("status").innerText = "Location retrieved: " + lat + ", " + lon;
                // Prosleđivanje lokacije preko query parametara
                const url = new URL(window.location);
                url.searchParams.set("lat", lat);
                url.searchParams.set("lon", lon);
                window.location = url;
            },
            function(error) {
                let errorMessage;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = "User denied the request for Geolocation.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = "Location information is unavailable.";
                        break;
                    case error.TIMEOUT:
                        errorMessage = "The request to get user location timed out.";
                        break;
                    default:
                        errorMessage = "An unknown error occurred.";
                        break;
                }
                document.getElementById("status").innerText = "Error: " + errorMessage;
                const url = new URL(window.location);
                url.searchParams.set("error", errorMessage);
                window.location = url;
            }
        );
    } else {
        document.getElementById("status").innerText = "Geolocation is not supported by your browser.";
        const url = new URL(window.location);
        url.searchParams.set("error", "Geolocation is not supported by your browser.");
        window.location = url;
    }
};
</script>
""", unsafe_allow_html=True)

# Provera query parametara
query_params = st.query_params
if 'lat' in query_params and 'lon' in query_params:
    st.session_state.lat = float(query_params['lat'])
    st.session_state.lon = float(query_params['lon'])
    st.session_state.status = f"Location retrieved: Latitude = {st.session_state.lat}, Longitude = {st.session_state.lon}"
elif 'error' in query_params:
    st.session_state.status = f"Error: {query_params['error']}"

# Prikaz statusa
st.write(st.session_state.status)