# General-purpose library for communicating with a Domoticz Server (Raspberry Pi Pico version)
#
# Last changed: 05/01/2025 10:16
# Last change: Added date & time of last change

import urequests as requests

IP_AddressB = '192.168.1.31'
IP_AddressA = '192.168.1.32'
port = '8085'

# Function to log data to Domoticz server...
def LogToDomoticz(idx, SensorVal):
    urlA = 'http://' + IP_AddressA + ':' + port + '/json.htm?type=command&param=udevice&nvalue=0&idx='+idx+'&svalue='+str(SensorVal)
    urlB = 'http://' + IP_AddressB + ':' + port + '/json.htm?type=command&param=udevice&nvalue=0&idx='+idx+'&svalue='+str(SensorVal)

    try:
        request = requests.get(urlA)
        request.close()
        response = "OK"
    except:
        try:
            request = requests.get(urlB)
            request.close()
            response = "OK"
        except:
            response = "Error: (Unable to process request)"

    return response

def LogToDomoticz2(idx, SensorVal1, SensorVal2):
    url = 'http://' + IP_AddressA + ':' + port + '/json.htm?type=command&param=udevice&nvalue=0&idx='+idx+'&svalue='+str(SensorVal1)+';'+str(SensorVal2)

    try:
        request = requests.get(url)
        request.close()

        response = "Request sent!"
    except:
        response = "Error: Unable to process request)"

    return response
