import os
import requests
import geopy
from flask import Flask, request, render_template
import json

app = Flask(__name__, static_url_path='', static_folder="../presentation/static",
            template_folder="../presentation/templates")
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = os.environ.get("MAPBOX_KEY", None)

@app.route('/presentation')
def presentation():
    return render_template(
        'presentation.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )


@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json(force=True)
    print(data)
    route_data = get_data((data['start_location']['lat'], data['start_location']['lng']),
                          (data['end_location']['lat'], data['end_location']['lng']), data['x'], data['min_max'])
    return json.dumps(route_data)
