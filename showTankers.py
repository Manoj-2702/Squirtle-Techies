import folium
from geopy.geocoders import Nominatim
from IPython.display import HTML

with open("/content/datasetLinks.txt", "r") as file:
    lines = file.readlines()

bangalore_coords = (12.9716, 77.5946)
map_bangalore = folium.Map(location=bangalore_coords, zoom_start=10)

for line in lines:
    parts = line.split(",")
    latitude = float(parts[0])
    longitude = float(parts[1])
    
    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(parts[2], parse_html=True)  
    ).add_to(map_bangalore)

map_html = map_bangalore._repr_html_()

HTML(map_html)
