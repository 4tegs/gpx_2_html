import os
import sys
import folium
import folium.plugins
from folium.plugins import MarkerCluster, MeasureControl      # enable for MeasureControl

# ...................................................
# Where do I find my utils to be imported? Set your path here!
# this are our standard utilities, used for several scripts from 4tegs
sys.path.append("C:\\SynologyDrive\\Python\\00_import_utils")
import utils                                                    

# ------------------------------------------------------------------------------------------
#   ____                _         _   _ _____ __  __ _       __  __
#  / ___|_ __ ___  __ _| |_ ___  | | | |_   _|  \/  | |     |  \/  | __ _ _ __
# | |   | '__/ _ \/ _` | __/ _ \ | |_| | | | | |\/| | |     | |\/| |/ _` | '_ \
# | |___| | |  __/ (_| | ||  __/ |  _  | | | | |  | | |___  | |  | | (_| | |_) |
#  \____|_|  \___|\__,_|\__\___| |_| |_| |_| |_|  |_|_____| |_|  |_|\__,_| .__/
#                                                                        |_|
# ------------------------------------------------------------------------------------------
def create_map():
    '''
    Input: Will use GPX from parameter 1
    Output: An HTML File with tracks and waypoints
    '''
    gpx = utils.mein_gpx(None)
    display_color = gpx.display_color
    gpx1 = gpx.gpx
    # Calculate the center of the map. Weighted on Tracks as they need more of the space.
    if gpx1.tracks:
        coords = [(p.latitude, p.longitude)
                  for p in gpx1.tracks[0].segments[0].points]
    elif gpx1.waypoints:
        coords = [(w.latitude, w.longitude) for w in gpx1.waypoints]
    else:
        # Default center if no waypoints or tracks are available
        coords = [(0, 0)]
    latitudes, longitudes = zip(*coords)
    map_center = (sum(latitudes) / len(latitudes),
                  sum(longitudes) / len(longitudes))

    my_map = folium.Map(location=map_center, zoom_start=9, tiles= None)
    
    folium.plugins.Fullscreen(
        position="topright",
        title="Fullscreen On",
        title_cancel="Fullscreen Off",
        force_separate_button=True,
    ).add_to(my_map)

    
    #  Add Standard OpenStreetmap German Layout tile layer 
    folium.TileLayer(tiles= "OpenStreetMap.DE",name="OpenStreetMap", show=True).add_to(my_map)
    # Add a Satellite tile layer
    folium.TileLayer("Esri.WorldImagery", name="Satellite", show=False).add_to(my_map)
    # Add Opentopo as a layer
    folium.TileLayer("OpenTopoMap", name="OpenTopoMap", show=False).add_to(my_map)
    
    # ................................................................................................
    # In case you want to provide MapBox Satellite images on your map, you need to have a 
    #       MapBox API Access Token. You can receive it from Mapbox.com
    #       There is a free version available too.
    # 
    # Remove remarks and add your key
    # ................................................................................................
    # folium.TileLayer(
    #     tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=your_token_HERE',
    #     attr='Mapbox',
    #     name='Mapbox Satellite',
    #     show=False
    # ).add_to(my_map)
    
    # ................................................................................................

    # Remove remark if you want to add a measure Control to your map
    # my_map.add_child(MeasureControl())

    # Lade deine eigene Translation Tabelle
    translate_table = utils.load_json(None)
    my_path_to_icon = "http://motorradtouren.de/pins/"
    my_point_symbol_dict = translate_table.get("points")
    
    icon_group = folium.FeatureGroup(name="Waypoints", show=True).add_to(my_map)
    for waypoint in gpx1.waypoints:
        # If the waypoint.symbol can be found in the Json Table for Waypoints then get the Waypoint reference for the pin
        try:
            icon_url = my_path_to_icon + (my_point_symbol_dict[waypoint.symbol])
        # if the waypoint.symbol can NOT be found in the Json Table, find the icon_url for the default value
        except:
            icon_url = my_path_to_icon + (my_point_symbol_dict["Default"])
            print('---------------------------------------------------------------------------------------------')
            print('               GPX Symbol used but not found in translation table: ' + str(waypoint.symbol))
            print('               Default value used')
            print('---------------------------------------------------------------------------------------------\n\n')

        # Marker with a custom icon from a remote URL
        my_popup = f'<div style="width: 300px; max_height: 500px;"><p>{str(waypoint.comment)}</p></html>'
        folium.Marker(location=(waypoint.latitude, waypoint.longitude), popup=folium.Popup(my_popup, max_width=300), tooltip=str(waypoint.name), icon=folium.CustomIcon(icon_image=icon_url, icon_size=(36, 36))).add_to(icon_group)

    track_group = folium.FeatureGroup(name="Tracks", show=True).add_to(my_map)
    # Add tracks as polylines with different colors
    for i, track in enumerate(gpx1.tracks):
        if len(display_color) == 0:         # For tracks without color - so not from Garmin
            color = "DarkMagenta"           # set default value
        else:
            color = display_color[i].text   # Get Garmin Color of track
        for segment in track.segments:
            points = [(point.latitude, point.longitude) for point in segment.points]
            folium.PolyLine(locations=points, weight=5, color=color).add_to(track_group)

    folium.LayerControl().add_to(my_map)
    html_name = gpx.gpx_path_with_name_no_suffix + ".html"
    my_map.save(html_name)
    return

if __name__ == "__main__":
    os.system('cls')
    my_script = utils.IchSelbst()
    my_map = create_map()
