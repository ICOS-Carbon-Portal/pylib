import folium


def generate_html(station_info):
    # Format station's html string using data extracted from the dataframe.
    station_html = \
        """
        <table border='0'>
            <caption style='font-weight:bold;font-size:18px;padding:15px;'>
                Station Information
            </caption>
            <tr style='background-color:#f8f4f4'>
                <td style="padding:4px"><nobr>Station name</nobr></td>
                <td style="padding:4px"><nobr><a title="{uri}" href="{uri}">
                    {name}
                </a></nobr></td>
            </tr>
            <tr><td style="padding:4px">Station ID</td><td style="padding:4px">{id}</td></tr>
            <tr style='background-color:#f8f4f4'>
                <td style="padding:4px">Country, Country code</td>
                <td style="padding:4px"><nobr>{country_name} - {country_code}</nobr></td>
            </tr>
            <tr>
                <td style="padding:4px"><nobr>Latitude, Longitude, Elevation</nobr></td>
                <td style="padding:4px"><nobr>{latitude}, {longitude}, {elevation}</nobr></td>
            </tr>
            <tr style='background-color:#f8f4f4'>
                <td style="padding:4px">Project</td>
                <td style="padding:4px">{project}</td>
            </tr>
            <tr><td style="padding:4px">Theme</td><td style="padding:4px">{theme}</td></tr>
        </table>
        """.format(uri=station_info[0], name=station_info[2], id=station_info[1],
                   country_name=station_info[9],
                   country_code=station_info[3], latitude=station_info[4],
                   longitude=station_info[5],
                   elevation=station_info[6], project=station_info[7], theme=station_info[8])
    # Render html from string.
    folium_html = folium.Html(station_html, script=True)
    return folium_html
