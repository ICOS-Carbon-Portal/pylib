import folium


def generate_html(station_info):
    # Format station's html string using data extracted from the dataframe.
    station_html = """
        <p>
            Station name | id: 
                <a title="CTRL + Click to follow this link." href="{uri}">
                    {name} | {id}
                </a><br>
            Country: {country}<br>
            Elevation: {elevation}<br>
            Project - Theme: {project} - {theme}<br>
        </p>
    """.format(uri=station_info[0], id=station_info[1], name=station_info[2],
               country=station_info[3], elevation=station_info[6], project=station_info[7],
               theme=station_info[8])
    # Render html from string.
    folium_html = folium.Html(station_html, script=True)
    return folium_html
