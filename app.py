from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import threading
from time import sleep
from datetime import datetime, timedelta

from Temperatuursensor import Temperatuursensor
from Luchtkwaliteitsensor import Luchtkwaliteitsensor

#THREAD Temperatuur
temperatuursensor = Temperatuursensor("28-01145b8d5bf2")


def temperature():
    while True:
        minute = datetime.now().minute
        if(minute % 15 == 0 or minute == 0):
            temperature = temperatuursensor.get_temperature()
            DataRepository.add_value_sensor(3, temperature)
            print(f"Added temperature: {temperature} to database.")
            sleep(60)



temperatuur_proces = threading.Timer(10, temperature)
temperatuur_proces.start()

#THREAD Luchtkwaliteit
luchtkwaliteitsensor = Luchtkwaliteitsensor()


def airquality():
    while True:
        minute = datetime.now().minute
        if(minute % 15 == 0 or minute == 0):
            airquality = luchtkwaliteitsensor.result()
            DataRepository.add_value_sensor(2, airquality)
            print(f"Added airquality: {airquality} to database.")
            sleep(60)


luchtkwaliteit_proces = threading.Timer(10, airquality)
luchtkwaliteit_proces.start()

# Start app
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# JWT
app.config["JWT_SECRET_KEY"] = "Secret!"
jwt = JWTManager(app)

# Custom endpoint
endpoint = '/api/v1'


# ROUTES
@app.route("/")
def index():
    return "PLEASE VISIT API ROUTE"


@app.route(endpoint + "/sensoren/<sensor_id>/<date>", methods=["GET"])
@jwt_required
def get_sensoren_data(sensor_id, date):
    if request.method == "GET":
        return jsonify(sensor_waarden=DataRepository.read_value_sensor(sensor_id, date)), 200


@app.route(endpoint + "/aanmelden", methods=["POST"])
def aanmelden():
    gegevens = DataRepository.json_or_formdata(request)

    username = gegevens["username"]
    password = gegevens["password"]

    passwordDB = DataRepository.get_password_by_user(username)

    if password == passwordDB["Wachtwoord"]:
        expires = timedelta(hours=12)
        access_token = create_access_token(identity=username, expires_delta=expires)
        return(jsonify(message="aangemeld",access_token=access_token)), 200
    else:
        return(jsonify(message="error")), 401


if __name__ == "__main__":
    socketio.run(app, debug=False, host='0.0.0.0')