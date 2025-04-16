from counterfit_connection import CounterFitConnection
import time
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
from counterfit_shims_grove.grove_light_sensor_v1_2 import GroveLightSensor
from counterfit_shims_grove.grove_led import GroveLed
import paho.mqtt.client as mqtt
import json
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, X509

CounterFitConnection.init('127.0.0.1', 5000)

adc = ADC() # water sensor, pin 0
relay = GroveRelay(5) # relay, pin 5
led = GroveLed(6) # led, pin 6

host_name = "hung-hub.azure-devices.net"
device_id = "soil-moisture-sensor-x509"
x509 = X509("./soil-moisture-sensor-x509-cert.pem", "./soil-moisture-sensor-x509-key.pem")

# create a device interface for Azure to communitcate with
device_client = IoTHubDeviceClient.create_from_x509_certificate(x509, host_name, device_id)

print('Connecting')
device_client.connect()
print('Connected')

sensor_running = True # for controlling the water sensor
actuator_running = False # for controlling the sprinkler

def handle_method_request(request):
		global sensor_running
		global actuator_running
		print("Direct method received - ", request.name)
		
		# We can define any method invocations we want to handle here
		if request.name == "start_watering":
				actuator_running = True
				print('Watering device turned ON')
		if request.name == "stop_watering":
				actuator_running = False
				print('Watering device turned OFF')
		if request.name == "say_hi":
				print("Farm Watering System says:")
				print(" .----------------.  .----------------.  .----------------.  .----------------.  .----------------. ")
				print("| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |")
				print("| |  ____  ____  | || |      __      | || |   _____      | || |   _____      | || |     ____     | |")
				print("| | |_   ||   _| | || |     /  \     | || |  |_   _|     | || |  |_   _|     | || |   .'    `.   | |")
				print("| |   | |__| |   | || |    / /\ \    | || |    | |       | || |    | |       | || |  /  .--.  \  | |")
				print("| |   |  __  |   | || |   / ____ \   | || |    | |   _   | || |    | |   _   | || |  | |    | |  | |")
				print("| |  _| |  | |_  | || | _/ /    \ \_ | || |   _| |__/ |  | || |   _| |__/ |  | || |  \  `--'  /  | |")
				print("| | |____||____| | || ||____|  |____|| || |  |________|  | || |  |________|  | || |   `.____.'   | |")
				print("| |              | || |              | || |              | || |              | || |              | |")
				print("| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |")
				print(" '----------------'  '----------------'  '----------------'  '----------------'  '----------------' ")
		if request.name == "stop_sensor":
				sensor_running = False
		if request.name == "start_sensor":
				sensor_running = True

		method_response = MethodResponse.create_from_method_request(request, 200)
		device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request

while True:
		if sensor_running:
				soil_moisture = adc.read(0)
				print("\tSoil moisture:", soil_moisture)

				message = Message(json.dumps({ 'soil_moisture': soil_moisture }))
				device_client.send_message(message)

		if actuator_running:
				# turn on relay and blink led
				relay.on()
				led.on()
				time.sleep(0.5)
				led.off()
				time.sleep(0.5)
				led.on()
				time.sleep(0.5)
				led.off()
		else:
				# turn off relay and led
				relay.off()
				led.off()
				time.sleep(1.5)
										
		time.sleep(0.5)
