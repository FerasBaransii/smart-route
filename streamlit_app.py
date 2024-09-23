import streamlit as st
from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import st_folium

# Function to get latitude and longitude of an address location
def get_coordinates(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    results = response.json().get('results')
    if results:
        location = results[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None

# Function to get routes from Google Maps API
def get_routes(start_coords, waypoints, end_coords, api_key):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{start_coords[0]},{start_coords[1]}",
        "destination": f"{end_coords[0]},{end_coords[1]}",
        "key": api_key,
        "waypoints": '|'.join([f"{lat},{lon}" for lat, lon in waypoints]) if waypoints else None,
        "alternatives": "true"
    }
    response = requests.get(base_url, params=params)
    return response.json()


# Function to generate Google Maps embed URL for multiple routes
def generate_map_url(start_coords, end_coords=None, waypoints=None, api_key=None):
    base_url = "https://www.google.com/maps/embed/v1/directions"
    params = f"?key={api_key}&origin={start_coords[0]},{start_coords[1]}&destination={end_coords[0]},{end_coords[1]}"
    if waypoints:
        waypoints_str = '|'.join([f"{lat},{lon}" for lat, lon in waypoints])
        params += f"&waypoints={waypoints_str}"
    return base_url + params


# Initialize waypoints in session state
if 'waypoints' not in st.session_state:
    st.session_state['waypoints'] = []

# Define the available locations
locations = {
    "Tel Aviv": [32.0853, 34.7818],
    "Jerusalem": [31.7683, 35.2137],
    "Haifa": [32.7940, 34.9896],
    "Eilat": [29.5581, 34.9482],
    "Beersheba": [31.2529, 34.7915],
    "Nazareth": [32.6996, 35.3035]
}

# Streamlit App Title
st.title("Interactive Route Planner")

# Example Google Maps API key (replace with your own key)
api_key = "YourApiKey"

# Sidebar for location selection
selected_location = st.sidebar.selectbox(
    "Choose a location to start the map:",
    options=list(locations.keys()),
    index=0  # Default is Tel Aviv
)

# Get the coordinates of the selected location
start_lat, start_lon = locations[selected_location]

# Layout with two columns
col1, col2 = st.columns([3, 1])

with col1:
    # Create an interactive map centered at the selected location
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)

    # Add markers if they exist in session state
    if 'start_point' in st.session_state and st.session_state['start_point']:
        folium.Marker(st.session_state['start_point'], tooltip="Start Point").add_to(m)

    if 'waypoints' in st.session_state:
        for idx, waypoint in enumerate(st.session_state['waypoints']):
            folium.Marker(waypoint, tooltip=f"Waypoint {idx + 1}").add_to(m)

    if 'dest1_point' in st.session_state and st.session_state['dest1_point']:
        folium.Marker(st.session_state['dest1_point'], tooltip="Destination 1").add_to(m)

    # Display the map and capture clicks
    clicked_location = st_folium(m, width=700, height=500)

    # Check if a click occurred and capture the location
    if clicked_location and clicked_location.get('last_clicked'):
        lat, lon = clicked_location['last_clicked']['lat'], clicked_location['last_clicked']['lng']
        
        # Allow users to set or update start or end points directly on click
        if clicked_location and clicked_location.get('last_clicked'):
            lat, lon = clicked_location['last_clicked']['lat'], clicked_location['last_clicked']['lng']
            
            # Allow users to set or update start, waypoint, or end points
            if st.button("Set Start Point"):
                st.session_state['start_point'] = (lat, lon)
                st.write(f"Start Point set at: {st.session_state['start_point']}")

            if st.button("Set End Point"):
                st.session_state['dest1_point'] = (lat, lon)
                st.write(f"Destination 1 set at: {st.session_state['dest1_point']}")

            if st.button("Add Waypoint"):
                st.session_state['waypoints'].append((lat, lon))
                st.write(f"Waypoint {len(st.session_state['waypoints'])} added at: {lat}, {lon}")

    # Add buttons to clear the points
    if st.button("Clear Start Point"):
        st.session_state['start_point'] = None
        st.write("Start Point cleared.")

    if st.button("Clear Destination 1"):
        st.session_state['dest1_point'] = None
        st.write("Destination 1 cleared.")

    if st.button("Clear Waypoints"):
        st.session_state['waypoints'] = []
        st.write("All waypoints cleared.")

    # Reset button to clear all markers
    if st.button("Reset Markers"):
        st.session_state['start_point'] = None
        st.session_state['waypoints'] = []
        st.session_state['dest1_point'] = None
        st.success("All markers cleared.")
    
with col2:
    st.write("## Location Input")
    
    # User inputs for start and end locations
    start_address = st.text_input("Enter your starting location:")
    end_address = st.text_input("Enter your destination location:")
    waypoint_address = st.text_input("Enter a waypoint location (optional):")

    # Debugging: Print input values
    st.write("Start Address:", start_address)
    st.write("End Address:", end_address)

    # Button to use the entered addresses
    if st.button("Set Start and Destination"):
        if start_address and end_address:
            start_coords = get_coordinates(start_address, api_key)
            end_coords = get_coordinates(end_address, api_key)
            
            if start_coords and end_coords:
                st.session_state['start_point'] = start_coords
                st.session_state['dest1_point'] = end_coords
                st.success("Start and destination set!")
            else:
                st.error("Unable to find coordinates for the provided addresses.")
        else:
            st.error("Please enter both start and destination addresses.")

    
    # Button to add waypoint
    if st.button("Add Waypoint1"):
        if waypoint_address:
            waypoint_coords = get_coordinates(waypoint_address, api_key)
            if waypoint_coords:
                st.session_state['waypoints'].append(waypoint_coords)
                st.success(f"Waypoint added: {waypoint_address}")
            else:
                st.error("Unable to find coordinates for the waypoint.")
        else:
            st.error("Please enter a waypoint address.")


if 'start_point' in st.session_state and st.session_state['start_point'] and 'dest1_point' in st.session_state and st.session_state['dest1_point']:
    start_coords = st.session_state['start_point']
    dest1_coords = st.session_state['dest1_point']

    # Get route for the segments
    waypoints = st.session_state['waypoints'] if st.session_state['waypoints'] else None
    route1 = get_routes(start_coords, waypoints, dest1_coords, api_key)
    
    if route1['status'] == 'OK':
        # Initialize total distance and duration
        total_distance = 0
        total_duration = 0

        st.markdown("### Route Segment Details")

        # Iterate over each leg of the journey
        for idx, leg in enumerate(route1['routes'][0]['legs']):
            start_address = leg['start_address']
            end_address = leg['end_address']
            distance = leg['distance']['text']
            duration = leg['duration']['text']

            # Add up the total distance and duration
            total_distance += leg['distance']['value']
            total_duration += leg['duration']['value']

            # Display the distance and duration for each segment
            st.markdown(
                f"""
                **Segment {idx + 1}:**  
                From **{start_address}** to **{end_address}**  
                **Distance:** {distance}  
                **Duration:** {duration}
                """
            )
        
        # Convert total distance to kilometers and total duration to minutes
        total_distance_km = total_distance / 1000  # Convert meters to kilometers
        total_duration_min = total_duration / 60  # Convert seconds to minutes

        # Display the total distance and duration for the entire route
        st.markdown(
            f"""
            ### Total Route Details:
            **Total Distance:** {total_distance_km:.2f} km  
            **Total Duration:** {total_duration_min:.2f} minutes
            """
        )

        # Display the map with the route and waypoints
        map_url = generate_map_url(start_coords, dest1_coords, waypoints, api_key)
        st.write("**Map Route:**")
        st.components.v1.iframe(map_url, width=700, height=500)
    else:
        st.error("Could not find route to the destination. Please check the location and try again.")
else:
    st.write("Please select both a start point and a first destination to display the route.")
