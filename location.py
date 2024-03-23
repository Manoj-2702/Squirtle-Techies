import folium
from geopy.geocoders import Nominatim
from IPython.display import HTML

bangalore_coords = (12.9716, 77.5946)
map_bangalore = folium.Map(location=bangalore_coords, zoom_start=10)

place_to_locate = "jeevan nagar, Bangalore"

geolocator = Nominatim(user_agent="my_app")
location = geolocator.geocode(place_to_locate)

if location:
    folium.Marker(
        location=[location.latitude, location.longitude],
        tooltip=place_to_locate,
        popup=place_to_locate
    ).add_to(map_bangalore)

map_html = map_bangalore._repr_html_()
print(location)
HTML(map_html)
