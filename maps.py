import folium
from geopy.geocoders import Nominatim

# Create a map centered on Bangalore
bangalore_coords = (12.9716, 77.5946)
map_bangalore = folium.Map(location=bangalore_coords, zoom_start=10)

# Define the place you want to locate
place_to_locate = "MG Road, Bangalore"

# Use the Nominatim geocoder to get the coordinates of the place
geolocator = Nominatim(user_agent="my_app")
location = geolocator.geocode(place_to_locate)

# Add a marker for the located place
if location:
    folium.Marker(
        location=[location.latitude, location.longitude],
        tooltip=place_to_locate,
        popup=place_to_locate
    ).add_to(map_bangalore)

# Save the map as an HTML file
map_bangalore.save("bangalore_map.html")
print("Map saved as bangalore_map.html")