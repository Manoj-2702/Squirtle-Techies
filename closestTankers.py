import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from IPython.display import HTML

def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers
with open("/content/datasetLinks.txt", "r") as file:
    lines = file.readlines()

user_location = input("Enter a location: ")

geolocator = Nominatim(user_agent="my_app")
user_coords = geolocator.geocode(user_location)
if user_coords:
    user_coords = (user_coords.latitude, user_coords.longitude)
else:
    print("Location not found.")

bangalore_coords = (12.9716, 77.5946)
map_bangalore = folium.Map(location=bangalore_coords, zoom_start=10)

if user_coords:
    folium.Marker(
        location=user_coords,
        tooltip="Your Location",
        popup=user_location
    ).add_to(map_bangalore)

distances = []
for line in lines:
    parts = line.split(",")
    location_coords = (float(parts[0]), float(parts[1]))
    distance = calculate_distance(user_coords, location_coords)
    distances.append((distance, line))

closest_locations = sorted(distances)[:5]

for distance, line in closest_locations:
    parts = line.split(",")
    latitude = float(parts[0])
    longitude = float(parts[1])
    location_name = parts[2]
    folium.Marker(
        location=[latitude, longitude],
        popup=f"{location_name} (Distance: {distance:.2f} km)"
    ).add_to(map_bangalore)

map_html = map_bangalore._repr_html_()
HTML(map_html)
