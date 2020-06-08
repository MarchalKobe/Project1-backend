from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import multiprocessing
import ctypes
from time import sleep
from datetime import datetime, timedelta, date
from ics import Calendar
import requests

from RPi import GPIO
from subprocess import check_output, run
import pathlib

from Temperatuursensor import Temperatuursensor
from Luchtkwaliteitsensor import Luchtkwaliteitsensor
from OLED import OLED


# PROCESS sensors
temperatuursensor = Temperatuursensor("28-01145b8d5bf2")
luchtkwaliteitsensor = Luchtkwaliteitsensor()


def sensors():
    while True:
        minute = datetime.now().minute
        if(minute % 15 == 0 or minute == 0):
            temperature = temperatuursensor.get_temperature()
            DataRepository.add_value_sensor(3, temperature)
            print(f"Added temperature: {temperature} to database.")

            airquality = luchtkwaliteitsensor.result()
            DataRepository.add_value_sensor(2, airquality)
            print(f"Added airquality: {airquality} to database.")
            sleep(60)


sensors_process = multiprocessing.Process(target=sensors)
sensors_process.start()

calendarStop = False


# PROCESS Calendar
def calendar():
    global calendarStop

    while True:
        links = DataRepository.get_links()
        
        if links:
            print("Import calendar begin")
            
            for linkInformation in links:
                if not calendarStop:
                    linkID = linkInformation["LinkID"]
                    link = linkInformation["Link"]
                    
                    try:
                        c = Calendar(requests.get(link).text)
                        e = list(c.timeline)

                        for event in e:
                            if not calendarStop:
                                time = event.begin
                                date = time.strftime("%Y-%m-%d %H:%M:%S")
                                event = event.name

                                DataRepository.add_activiteit_not_exists(event, date, linkID)
                            else:
                                DataRepository.delete_activiteiten(linkID)
                    except Exception as e:
                        print(e)
            
            print("Import calendar end")

        calendarStop = False
        sleep(15)


calendar_process = multiprocessing.Process(target=calendar)
calendar_process.start()


# PROCESS interface
oled = OLED()
pir = 23
audio = 21

oled.show_logo()
sleep(2)

GPIO.setup(pir, GPIO.IN)
GPIO.setup(audio, GPIO.OUT)
GPIO.output(audio, GPIO.LOW)

interface_button_up = 5
interface_button_down = 12
interface_button_right = 6
interface_toggle = 13

GPIO.setup(interface_button_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(interface_button_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(interface_button_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(interface_toggle, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if GPIO.input(interface_toggle) == GPIO.LOW:
    print("ON")
    interfaceEnabled = True
else:
    print("OFF")
    interfaceEnabled = False

upButtonPressed = False
downButtonPressed = False
rightButtonPressed = False
interfaceNumber = 1
agendaCalendar = True
sleepMode = False

eventName = ""
eventDate = ""

agendaDate = date.today()
agendaDate = agendaDate.strftime("%Y-%m-%d")

showMessage = multiprocessing.Value(ctypes.c_bool, False)
manager = multiprocessing.Manager()
messageList = manager.list()


def interface_agenda():
    global agendaDate, agendaCalendar, eventName, eventDate

    if agendaCalendar:
        oled.show_calendar_date(agendaDate)
    else:
        if eventName is not None:
            oled.show_calendar_event(eventDate, eventName)


def interface_klok():
    oled.show_clock()


def interface_ip():
    ips = check_output(["hostname", "--all-ip-addresses"])
    ips = ips.decode("utf-8").split()
    oled.show_text(f"IP: {ips[0]}")


def button_up(channel):
    global upButtonPressed
    if showMessage.value == False:
        upButtonPressed = True


def button_down(channel):
    global downButtonPressed
    if showMessage.value == False:
        downButtonPressed = True


def button_right(channel):
    global rightButtonPressed
    if showMessage.value == False:
        rightButtonPressed = True


def toggle_button(channel):
    global interfaceEnabled
    if GPIO.input(interface_toggle) == GPIO.LOW:
        print("ON")
        interfaceEnabled = True
    else:
        print("OFF")
        interfaceEnabled = False


def interface():
    global upButtonPressed, downButtonPressed, rightButtonPressed, interfaceNumber, agendaDate, agendaCalendar, eventName, eventDate, sleepMode, interfaceEnabled, showMessage, screenNickname, screenMessage

    GPIO.add_event_detect(interface_button_up, GPIO.FALLING, callback=button_up, bouncetime=500)
    GPIO.add_event_detect(interface_button_down, GPIO.FALLING, callback=button_down, bouncetime=500)
    GPIO.add_event_detect(interface_button_right, GPIO.FALLING, callback=button_right, bouncetime=200)
    GPIO.add_event_detect(interface_toggle, GPIO.BOTH, callback=toggle_button, bouncetime=200)

    interface_agenda()

    while True:
        if interfaceEnabled and showMessage.value == False:
            if sleepMode == False:
                if rightButtonPressed:
                    longPress = True
                    longPressTime = 0

                    while longPress and longPressTime <= 1:
                        if GPIO.input(interface_button_right) == GPIO.LOW:
                            sleep(0.1)
                            longPressTime += 0.1
                        else:
                            longPress = False

                    if longPressTime >= 1:
                        if interfaceNumber == 1:
                            interfaceNumber = 2
                        elif interfaceNumber == 2:
                            interfaceNumber = 3
                        elif interfaceNumber == 3:
                            interfaceNumber = 1
                        
                        print(interfaceNumber)
                        print("LONG PRESS")
                        sleep(0.5)
                    else:
                        print("NOT LONG PRESS")
                        if interfaceNumber == 1:
                            if agendaCalendar:
                                eventInformation = DataRepository.get_first_event_on_date(agendaDate)
                                if eventInformation is not None:
                                    eventName = eventInformation["Activiteit"]
                                    eventDate = eventInformation["Datum"].strftime("%H:%M:%S")
                                    agendaCalendar = False
                            else:
                                agendaCalendar = True
                        if interfaceNumber == 2:
                            sleepMode = True
                    
                    rightButtonPressed = False
                
                if upButtonPressed:
                    if interfaceNumber == 1:
                        if agendaCalendar:
                            newDate = DataRepository.get_closest_date_up(agendaDate)
                            print(newDate)
                            if newDate:
                                agendaDate = newDate["Datum"].strftime("%Y-%m-%d")
                                oled.show_calendar_date(agendaDate)
                        else:
                            newEvent = DataRepository.get_closest_event_up(agendaDate, eventDate)
                            print(newEvent)
                            if newEvent:
                                eventName = newEvent["Activiteit"]
                                eventDate = newEvent["Datum"].strftime("%H:%M:%S")
                                oled.show_calendar_event(eventDate, eventName)
                    
                    upButtonPressed = False
                
                if downButtonPressed:
                    if interfaceNumber == 1:
                        if agendaCalendar:
                            newDate = DataRepository.get_closest_date_down(agendaDate)
                            print(newDate)
                            if newDate:
                                agendaDate = newDate["Datum"].strftime("%Y-%m-%d")
                                oled.show_calendar_date(agendaDate)
                        else:
                            newEvent = DataRepository.get_closest_event_down(agendaDate, eventDate)
                            print(newEvent)
                            if newEvent:
                                eventName = newEvent["Activiteit"]
                                eventDate = newEvent["Datum"].strftime("%H:%M:%S")
                                oled.show_calendar_event(eventDate, eventName)
                    
                    downButtonPressed = False

                if interfaceNumber == 1:
                    interface_agenda()
                elif interfaceNumber == 2:
                    interface_klok()
                elif interfaceNumber == 3:
                    interface_ip()
            else:
                if rightButtonPressed:
                    sleepMode = False
                    rightButtonPressed = False
                
                if GPIO.input(pir) == GPIO.HIGH:
                    showClockTime = 0

                    while showClockTime <= 4:
                        oled.show_clock()
                        sleep(0.1)
                        showClockTime += 0.1
                
                oled.clear_screen()
        else:
            if showMessage.value:
                oled.show_message(f"{messageList[0]}: {messageList[1]}")
                print(messageList[0], messageList[1])

                path = pathlib.Path(__file__).parent.absolute()
                GPIO.output(audio, GPIO.HIGH)
                run(["sudo", "omxplayer", f"{path}/sounds/notification.mp3"])
                GPIO.output(audio, GPIO.LOW)

                answer = False
                
                while answer == False:
                    if GPIO.input(interface_button_up) == GPIO.LOW:
                        DataRepository.update_message_answer(messageList[2], "Ja")
                        answer = True

                    if GPIO.input(interface_button_down) == GPIO.LOW:
                        DataRepository.update_message_answer(messageList[2], "Nee")
                        answer = True
                
                showMessage.value = False
            else:
                oled.clear_screen()
        

interface_process = multiprocessing.Process(target=interface)
interface_process.start()

# Start app
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# JWT
app.config["JWT_SECRET_KEY"] = "ZSwqNY%J%7?]\B3}"
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

        if link["LinkID"] is None:
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


@app.route(endpoint + "/activiteiten", methods=["PUT"])
@jwt_required
def add_activiteit():
    if request.method == "PUT":
        eventData = DataRepository.json_or_formdata(request)
        event = eventData["event"]
        date = eventData["date"].replace("T", " ")

        if not event or not date:
            return jsonify(message="error"), 422
        else:
            data = DataRepository.add_activiteit(event, date)
            return jsonify(message="ok"), 200


@app.route(endpoint + "/links", methods=["GET", "PUT"])
@jwt_required
def get_links():
    if request.method == "GET":
        return jsonify(links=DataRepository.get_links()), 200
    elif request.method == "PUT":
        link = DataRepository.json_or_formdata(request)
        link = link["url"]

        if not link:
            return jsonify(message="error"), 422
        else:
            try:
                urlRead = requests.get(link).text

                if "BEGIN" in urlRead:
                    data = DataRepository.add_link(link)
                    return jsonify(message="ok"), 200
                else:
                    return jsonify(message="error"), 422
            except Exception:
                return jsonify(message="error"), 422


@app.route(endpoint + "/links/<id>", methods=["DELETE"])
@jwt_required
def delete_link(id):
    global calendarStop

    if request.method == "DELETE":
        DataRepository.delete_activiteiten(id)
        data = DataRepository.delete_link(id)
        if data > 0:
            calendarStop = True
            return jsonify(message="Succesvol verwijderd"), 201
        else:
            return jsonify(message="Niks verwijderd"), 201


@app.route(endpoint + "/nickname", methods=["GET"])
@jwt_required
def get_nickname():
    if request.method == "GET":
        user = get_jwt_identity()
        nickname = DataRepository.get_nickname(user)
        return jsonify(nickname=nickname), 200


@app.route(endpoint + "/sendmessage", methods=["POST"])
@jwt_required
def send_message():
    if request.method == "POST":
        user = get_jwt_identity()
        nickname = DataRepository.get_nickname(user)["Bijnaam"]
        message = DataRepository.json_or_formdata(request)["message"]
        userid = DataRepository.get_user_id(user)["GebruikerID"]

        messageid = DataRepository.add_message(message, userid)

        showMessage.value = True
        messageList[:] = []
        messageList.append(nickname)
        messageList.append(message)
        messageList.append(messageid)

        return jsonify(id=messageid), 200


@app.route(endpoint + "/message/answer/<id>", methods=["GET"])
@jwt_required
def get_message_answer(id):
    if request.method == "GET":
        data = DataRepository.get_message_answer(id)
        return jsonify(answer=data), 200


if __name__ == "__main__":
    socketio.run(app, debug=False, host='0.0.0.0')