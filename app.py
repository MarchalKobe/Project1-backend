from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

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