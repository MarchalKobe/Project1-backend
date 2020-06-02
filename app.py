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


@app.route(endpoint + "/sensoren/<sensor_id>/<date>", methods=["GET"])
@jwt_required
def get_sensoren_data(sensor_id, date):
    if request.method == "GET":
        return jsonify(sensor_waarden=DataRepository.read_value_sensor(sensor_id, date)), 200


@app.route(endpoint + "/activiteiten/<date>/days", methods=["GET"])
@jwt_required
def get_activiteiten_days(date):
    if request.method == "GET":
        return jsonify(days=DataRepository.read_activiteiten_days(date)), 200


@app.route(endpoint + "/activiteiten/<idOrDate>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def edit_activiteiten(idOrDate):
    if request.method == "GET":
        return jsonify(activiteiten=DataRepository.read_activiteiten(idOrDate)), 200
    elif request.method == "PUT":
        link = DataRepository.get_activiteiten_link(idOrDate)

        if(link["LinkID"] > 0):
            info = DataRepository.json_or_formdata(request)
            event = info["event"]
            date = info["date"].replace("T", " ")
            data = DataRepository.update_activiteit(idOrDate, event, date)
            
            if data is not None:
                if data == -1:
                    return jsonify(message="Fout: Deze activiteit bestaat niet of is gelinkt aan een externe kalender"), 404
                elif data == 0:
                    return jsonify(message="Geen gegevens aangepast"), 200
                else:
                    return jsonify(message="Succesvol aangepast", date=date.split(" ")[0]), 200
            else:
                return jsonify(message="error"), 404
        else:
            return jsonify(message="Fout: Deze activiteit is gelinkt aan een externe kalender"), 406
    elif request.method == "DELETE":
        data = DataRepository.delete_activiteit(idOrDate)
        if data > 0:
            return jsonify(message="Succesvol verwijderd"), 201
        else:
            return jsonify(message="Niks verwijderd"), 201


if __name__ == "__main__":
    socketio.run(app, debug=False, host='0.0.0.0')