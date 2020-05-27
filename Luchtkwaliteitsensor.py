import smbus

class Luchtkwaliteitsensor:
	ADDRESS_RESULT = 0x00
	ADDRESS_CONFIG = 0x02


	def __init__(self, address=0x50):
		self._address = address
		self._bus = smbus.SMBus(1)
		self._bus.write_byte_data(self._address, self.ADDRESS_CONFIG, 0x20)


	def adc_read(self):
		data = self._bus.read_i2c_block_data(self._address, self.ADDRESS_RESULT, 2)
		value = (data[0] & 0x0f) << 8 | data[1]
		return value


	def result(self):
		sensor_value = self.adc_read()

		return sensor_value

		# if sensor_value > 700:
		# 	return f"{sensor_value} Hoge verontreiniging"
		# elif sensor_value > 300:
		# 	return f"{sensor_value} Lage verontreiniging"
		# else:
		# 	return f"{sensor_value} Lucht is zuiver"