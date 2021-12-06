import os
import requests
import geopy
from flask import Flask, request, render_template
from server.data_utils.data_abstract import DataAbstract
from server.logger_utils import Logger
import json

app = Flask(__name__,static_url_path = '', static_folder = "../client/static", template_folder = "../client/")
# app.config.from_object(__name__)
print("I am gere 2")

#Initiating logger object
logger_object = Logger('server/logs/server.log')
logger = logger_object.get_logger()

##Inititalizing dataabstract object
data_abstract = DataAbstract(logger)


# app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = "pk.eyJ1IjoiYmhhbnViaGFuZGFyaSIsImEiOiJja3dxdDU0Z20wYjJ1MnBudzYwaW96dzRxIn0.6dxya_VrZh-qazlsFUTzwg"

@app.route('/home')
def home():
    logger.error("I am in Home")
    return render_template(
        'index.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json(force=True)
    print(data)
    logger.debug(data)
    route_data = data_abstract.get_data((data['start_location']['lat'], data['start_location']['lng']),
                          (data['end_location']['lat'], data['end_location']['lng']), data['x'], data['min_max'])
    return json.dumps(route_data)

if __name__=='__main__':
    print("I am here")
    app.run(host='127.0.0.1', port=3000)

