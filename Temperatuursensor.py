class Temperatuursensor:
    def __init__(self, slave):
        self._sensor_file_name = f"/sys/bus/w1/devices/{slave}/w1_slave"
    

    def get_temperature(self):
        temperature = ""
        
        sensor_file = open(self._sensor_file_name, "r")
        for line in sensor_file:
            temperature += line
        sensor_file.close()

        temperature = int(temperature[temperature.find("t=") + 2:]) / 1000

        return temperature