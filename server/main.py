import os
import requests
import geopy
from flask import Flask, request, render_template
from server.data_utils.data_abstract import DataAbstract
from server.logger_utils import Logger
import json

app = Flask(__name__)
# app.config.from_object(__name__)
print("I am gere 2")

#Initiating logger object
logger_object = Logger('server/logs/server.log')
logger = logger_object.get_logger()

##Inititalizing dataabstract object
data_abstract = DataAbstract(logger)


# app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = os.environ.get("MAPBOX_KEY", None)

@app.route('/home')
def home():
    logger.error("I am in Home")
    return render_template(
        'presentation.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

@app.route('/route', methods=['GET'])
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

