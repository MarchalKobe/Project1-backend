from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
from time import sleep

from Temperatuursensor import Temperatuursensor


# THREAD
temperatuursensor = Temperatuursensor("28-00000bac625e")


def temperatuur():
    while True:
        temperatuur = temperatuursensor.get_temperature()
        print(temperatuur)
        sleep(1)



temperatuur_proces = threading.Thread(target=temperatuur)
temperatuur_proces.start()

# Start app
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Custom endpoint
endpoint = '/api/v1'


# ROUTES
@app.route("/")
def index():
    return "PLEASE VISIT API ROUTE"


@app.route(endpoint + "/sensoren/<sensor_id>/<date>", methods=["GET"])
def get_sensoren_data(sensor_id, date):
    if request.method == "GET":
        return jsonify(sensor_waarden=DataRepository.read_value_sensor(sensor_id, date)), 200


if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0')