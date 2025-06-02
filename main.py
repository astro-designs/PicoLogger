# Multi-function data logger
# Written for the Raspberry Pi PICO
# Supports DSxx 1-wire temperature sensors
#          DHTxx 1-wire temperature / humidity sensors
#          PIR sensors
#
# Last changed: 26/05/2025 10:16
# Last change: Added date & time of last change
#              Updating to match other modules

# To do...
# Add support for
#          Simple I/O based event counter (non-resetting)
#          Simple I/O based daily event counter (resets daily)
#          Enable averaging function
#          External LED status
#          Voltage monitor
#          Current monitor

import rp2
import network
import ubinascii
import machine
import onewire
import dht
import ds18x20
import urequests as requests
import time
from secrets import secrets
import socket
import domoticz
import sensors
import logging

# ***************************************
# Notes...
# ***************************************
# 
# * * * * * * * * * * * * * * * * * * * *


# ***************************************
# Pin configuration
# ***************************************
#sensor_temp = machine.ADC(4)                    # Internal temperature sensor I/O ref
#sensor_USB5V = machine.ADC(27)                  # Internal 5V ADC I/O ref
#sensor_voltage = machine.ADC(28)                # External voltage sense I/O ref

# ***************************************
# Device configuration
# ***************************************


# ***************************************
# Miscellaneous configuration
# ***************************************
# Raspberry Pi PICO ADC calibration (3.3V)
conversion_factor = 3.3 / (65535)

# External voltage calibration
#voltage_a = 0                                  # Square factor if non-linear
#voltage_b = (1 / 1000) * (1000 + 4700) * 0.995 # Gain factor from potential divider network
#voltage_c = 0.00                               # Offset

# Function to log and / or print data & debug information
DebugLevel = 1                                  # (0 = disable all logging to console)
LogLevel = 0                                    # (0 = disable all logging to file)
def DebugLog(logString, PrintThreshold = 1, LogThreshold = 999):
    if DebugLevel >= PrintThreshold: print('Debug:' + logString)
    if LogLevel >= LogThreshold: logging.info(logString)


# Setup Log to file function
filename = 'log.csv'
logging.basicConfig(filename=filename, level=logging.INFO, format='%(levelname)s,%(message)s')

# Initialise analogue interface if used by any sensors
if 'Analogue' in sensors.SensorType:
    DebugLog("Initialising Analogue sensors")
    sensor_alg = list(())
    num_Alg_sensors = 0
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'Analogue':
            sensor_alg.append(machine.ADC(sensors.SensorLoc[SensorID]))

# Initialise one-wire interface if used by any sensors
if 'T1w' in sensors.SensorType:
    DebugLog("Initialising T1w sensors")
    T1w_roms = list(())
    T1w_id = 0
    num_T1w_sensors = 0
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'T1w':
            if T1w_id == 0:
                T1w_sensors = ds18x20.DS18X20(onewire.OneWire(machine.Pin(sensors.SensorLoc[SensorID])))
                T1w_roms = T1w_sensors.scan()
            T1w_id = T1w_id + 1
    
    num_T1w_sensors = len(T1w_roms)
    DebugLog('Found ' + str(num_T1w_sensors) + ' DSxx 1-wire device(s):')
    for T1w_id in range(num_T1w_sensors):
        #T1w_roms.append(roms[T1w_id])
        DebugLog(str(T1w_roms[T1w_id]))


# Initialise DHTxx one-wire interface if used by any sensors
DHTxx_sensors = list(())
if 'DHT11_T' in sensors.SensorType:
    DebugLog("Initialising DHT11_T sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT11_T':
            DHTxx_sensors.append(dht.DHT11(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHTxx_sensors)) + ' DHT11 1-wire device(s)')
    
if 'DHT11_H' in sensors.SensorType:
    DebugLog("Initialising DHT11_H sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT11_H':
            DHTxx_sensors.append(dht.DHT11(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHTxx_sensors)) + ' DHT11 1-wire device(s)')

if 'DHT11_TH' in sensors.SensorType:
    DebugLog("Initialising DHT11_T/H sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT11_TH':
            DHTxx_sensors.append(dht.DHT11(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHTxx_sensors)) + ' DHT11 1-wire device(s)')

if 'DHT22_T' in sensors.SensorType:
    DebugLog("Initialising DHT22_T sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT22_T':
            DHTxx_sensors.append(dht.DHT22(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHT22_sensors)) + ' DHT22 1-wire device(s)')
    
if 'DHT22_H' in sensors.SensorType:
    DebugLog("Initialising DHT22_H sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT22_H':
            DHTxx_sensors.append(dht.DHT22(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHTxx_sensors)) + ' DHT22 1-wire device(s)')

if 'DHT22_TH' in sensors.SensorType:
    DebugLog("Initialising DHT22_T/H sensors")
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'DHT22_TH':
            DHTxx_sensors.append(dht.DHT22(machine.Pin(sensors.SensorLoc[SensorID])))

    DebugLog('Found ' + str(len(DHTxx_sensors)) + ' DHT22 1-wire device(s)')

# Initialise IOR sensor(s)
if 'IOR' in sensors.SensorType:    
    DebugLog("Initialising Rising Edge IO sensors")
    IOR_pins = list(())
    IOR_sts = list(())
    IOR_id = 0
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'IOR':
            IOR_pins.append(machine.Pin(sensors.SensorLoc[SensorID], machine.Pin.IN))
            IOR_sts.append(0)
            IOR_pins[IOR_id].irq(trigger=machine.Pin.IRQ_RISING, handler=IOR_callback)
            IOR_id = IOR_id + 1

    DebugLog('Found ' + str(IOR_id) + ' IOR sensors')

IOR_interrupt=0
def IOR_callback(pin):
    global IOR_interrupt
    IOR_interrupt = 1


# Initialise PIR sensor(s)
if 'PIR' in sensors.SensorType:    
    DebugLog("Initialising PIR sensors")
    PIR_pins = list(())
    PIR_sts = list(())
    PIR_id = 0
    for SensorID in range(sensors.ActiveSensors):
        if sensors.SensorType[SensorID] == 'PIR':
            PIR_pins.append(machine.Pin(sensors.SensorLoc[SensorID], machine.Pin.IN))
            PIR_sts.append(0)
            PIR_pins[PIR_id].irq(trigger=machine.Pin.IRQ_RISING, handler=PIR_callback)
            PIR_id = PIR_id + 1

    DebugLog('Found ' + str(PIR_id) + ' PIR sensors')

PIR_interrupt=0
def PIR_callback(pin):
    global PIR_interrupt
    PIR_interrupt = 1


# Initialise sensor data...
SensorVal = list(())
for SensorID in range(sensors.ActiveSensors):
    SensorVal.append(0)

# Initialise Reading counter
Reading = 1

# Initialise domoticz_sts
domoticz_sts = 'OK'


# Function to measure data...
def MeasureData(NextMeasurementTime):
    global SensorVal, DHT11_sensors, IOR_interrupt, PIR_interrupt
    Alg_id = 0
    T1w_id = 0
    DHTxx_id = 0
    IOR_id = 0
    PIR_id = 0

    TimeNow = time.time()
    if TimeNow > NextMeasurementTime:
        NextMeasurementTime = NextMeasurementTime + sensors.MeasurementInterval
        
        # Measure...
        DebugLog('Measuring...')

        # Blink LED when taking a measurement
        blink_onboard_led(1)

        for SensorID in range(sensors.ActiveSensors):
            if sensors.SensorType[SensorID] == 'Analogue':
                try:
                    adc_val = sensor_alg[Alg_id].read_u16()
                    adc_voltage = conversion_factor * adc_val
                    SensorVal[SensorID] = sensors.Sensor_A[SensorID] * (adc_voltage**2) + sensors.Sensor_B[SensorID] * adc_voltage + sensors.Sensor_C[SensorID]
                    DebugLog('Alg[' + str(Alg_id) + ']: ' + str(SensorVal[SensorID]),1,0)
                except:
                    DebugLog('Alg_sensor[' + str(Alg_id) + '] did not respond',1,0)
                Alg_id = Alg_id + 1
                
            if sensors.SensorType[SensorID] == 'T1w':
                try:
                    if T1w_id == 0:
                       T1w_sensors.convert_temp()
                    SensorVal[SensorID] = round(T1w_sensors.read_temp(T1w_roms[T1w_id]),1)
                    DebugLog('T1w[' + str(T1w_id) + ']: ' + str(SensorVal[SensorID]))                    
                except:
                    DebugLog('T1w_sensor[' + str(T1w_id) + '] did not respond',1,0)
                T1w_id = T1w_id + 1
                                
            if sensors.SensorType[SensorID] == 'DHT11_T':
                try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = DHTxx_sensors[DHTxx_id].temperature()
                    print(SensorVal[SensorID])
                    DebugLog('DHT11[' + str(DHTxx_id) + ']_T: ' + str(SensorVal[SensorID]))                    
                except:
                    DebugLog('DHT11[' + str(DHTxx_id) + '] did not respond',1,0)
                DHTxx_id = DHTxx_id + 1
            
            if sensors.SensorType[SensorID] == 'DHT11_H':
                try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = DHTxx_sensors[DHTxx_id].humidity()
                    print(SensorVal[SensorID])
                    DebugLog('DHT11[' + str(DHTxx_id) + ']_H: ' + str(SensorVal[SensorID]))                    
                except:
                    DebugLog('DHT11[' + str(DHTxx_id) + '] did not respond',1,0)
                DHTxx_id = DHTxx_id + 1

            if sensors.SensorType[SensorID] == 'DHT11_TH':
                    #try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = str(DHTxx_sensors[DHTxx_id].temperature()) + ';'
                    SensorVal[SensorID] = SensorVal[SensorID] + str(DHTxx_sensors[DHTxx_id].humidity())
                    print(SensorVal[SensorID])
                    DebugLog('DHT11[' + str(DHTxx_id) + ']_TH: ' + str(SensorVal[SensorID]))                    
                    #except:
                    #DebugLog('DHT11[' + str(DHT11_id) + '] did not respond',1,0)
                    DHTxx_id = DHTxx_id + 1

            if sensors.SensorType[SensorID] == 'DHT22_T':
                try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = DHTxx_sensors[DHTxx_id].temperature()
                    print(SensorVal[SensorID])
                    DebugLog('DHT22[' + str(DHTxx_id) + ']_T: ' + str(SensorVal[SensorID]))                    
                except:
                    DebugLog('DHT22[' + str(DHTxx_id) + '] did not respond',1,0)
                DHTxx_id = DHTxx_id + 1
            
            if sensors.SensorType[SensorID] == 'DHT22_H':
                try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = DHTxx_sensors[DHTxx_id].humidity()
                    print(SensorVal[SensorID])
                    DebugLog('DHT22[' + str(DHTxx_id) + ']_H: ' + str(SensorVal[SensorID]))                    
                except:
                    DebugLog('DHT22[' + str(DHTxx_id) + '] did not respond',1,0)
                DHTxx_id = DHTxx_id + 1

            if sensors.SensorType[SensorID] == 'DHT22_TH':
                    #try:
                    DHTxx_sensors[DHTxx_id].measure()
                    SensorVal[SensorID] = str(DHTxx_sensors[DHTxx_id].temperature()) + ';'
                    SensorVal[SensorID] = SensorVal[SensorID] + str(DHTxx_sensors[DHTxx_id].humidity())
                    print(SensorVal[SensorID])
                    DebugLog('DHT22[' + str(DHTxx_id) + ']_TH: ' + str(SensorVal[SensorID]))                    
                    #except:
                    #DebugLog('DHT11[' + str(DHT11_id) + '] did not respond',1,0)
                    DHTxx_id = DHTxx_id + 1

            if sensors.SensorType[SensorID] == 'IOR':
                if IOR_interrupt == 1:
                    SensorVal[SensorID] = SensorVal[SensorID] + 1
                    IOR_interrupt = 0
                DebugLog('IOR[' + str(IOR_id) + ']: ' + str(SensorVal[SensorID]))
                IOR_id = IOR_id + 1

            if sensors.SensorType[SensorID] == 'PIR':
                if PIR_interrupt == 1:
                    SensorVal[SensorID] = SensorVal[SensorID] + 1
                    PIR_interrupt = 0
                DebugLog('PIR[' + str(PIR_id) + ']: ' + str(SensorVal[SensorID]))
                PIR_id = PIR_id + 1
                
    return NextMeasurementTime

# Function to log data...
def LogData(NextLogTime):
    global Reading, domoticz_sts
    
    TimeNow = time.time()
    if TimeNow > NextLogTime:
        NextLogTime = NextLogTime + sensors.LogInterval
        
        DebugLog('Logging...')

        # Log to Domiticz server...
        DebugLog ("Logging to Domoticz...")
        domoticz_sts = 'OK'
        for SensorID in range(sensors.ActiveSensors):
            if sensors.DomoticzIDX[SensorID] != 'x' and domoticz_sts == 'OK':
                domoticz_sts = domoticz.LogToDomoticz(sensors.DomoticzIDX[SensorID], SensorVal[SensorID])
                if domoticz_sts == "OK":
                    DebugLog('Domoticz Response: ' + domoticz_sts,0,1)
                    SensorVal[SensorID] = 0 # Reset any interrupt based data
                else:
                    DebugLog('Domoticz Response: ' + domoticz_sts,0,0)

        # Log to file...
        # Log TitleString if this is the first log entry...
        if Reading == 1:
            logTitleString = "Date / Time,"
            for SensorID in range(sensors.ActiveSensors):
                logTitleString = logTitleString + sensors.SensorName[SensorID] + ","
            DebugLog (logTitleString, 1, 1)

        logTime = str(time.gmtime(TimeNow)[0]) + '-' + str(time.gmtime(TimeNow)[1]) + '-' + str(time.gmtime(TimeNow)[2]) + ' '
        logTime = logTime + str(time.gmtime(TimeNow)[3]) + ':' + str(time.gmtime(TimeNow)[4]) + ':' + str(time.gmtime(TimeNow)[5])
        #logTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(TimeNow))
        logString = logTime + "," + str(Reading) + ","
        for SensorID in range(sensors.ActiveSensors):
            logString = logString + str(SensorVal[SensorID]) + ","
        DebugLog (logString, 1, 1)
        
        # Reset some measurements after logging...
        for SensorID in range(sensors.ActiveSensors):
            if sensors.SensorType[SensorID] == 'PIR':
                SensorVal[SensorID] = 0

        # Next reading...
        Reading = Reading + 1
    
    return NextLogTime


# Connect to WLAN...
def connect():
    # Check the MAC address (for info only)
    MAC = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    DebugLog('MAC Address = ' + MAC, 0,1)

    # Set country to avoid possible errors
    rp2.country("GB")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    ssid_try = 0
    ssid = secrets['ssid0']
    pw = secrets['pw0']

    timeout = 10 #10 second timeout before trying next ssid or giving up...
    while ssid_try < 3 and wlan.isconnected() == False and timeout > 0:
        # Read login secrets...
        if ssid_try == 0:
            ssid = secrets['ssid0']
            pw = secrets['pw0']
        elif ssid_try == 1:
            ssid = secrets['ssid1']
            pw = secrets['pw1']
        else:    
            ssid = secrets['ssid2']
            pw = secrets['pw2']

        wlan.connect(ssid, pw)
    
        while wlan.isconnected() == False and timeout > 0:
            DebugLog('Waiting for connection...', 0,1)
            timeout -= 1
            time.sleep(1)
        
        if timeout == 0 and wlan.isconnected() == False: # Timeout occured, try a different SSID next time...
            timeout = 10 #10 second timeout before trying next ssid or giving up...
            ssid_try += 1
            
    if wlan.isconnected() == True:
        status = wlan.ifconfig()
        DebugLog('Connected to ' + ssid + ', IP Address = ' + status[0], 0,1)
            
    return wlan
    

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks=1):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)


wlan = connect()

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

TimeNow = time.time()
NextMeasurementTime = TimeNow
NextLogTime = TimeNow

while (wlan_status == 3):
    status = wlan.ifconfig()
    DebugLog('Connected, IP Address = ' + status[0] + ')', 0,1)

    while Reading < sensors.NumReadings or sensors.NumReadings < 1:
        #DebugLog('Reading: ' + str(Reading) + '/' + str(sensors.NumReadings))
        
        # Run measurement routine...
        NextMeasurementTime = MeasureData(NextMeasurementTime)
    
        # Run logging routine...
        NextLogTime = LogData(NextLogTime)
            
    # Check log response in case there was a network error...
    if sensors.Domoticz_En and domoticz_sts != 'OK':
        wlan_status = 99 # Set wlan_status to 99 (or anything other than 3) to flag error
    else:
        # Re-check WIFI status before repeating the loop...
        wlan_status = wlan.status()
        
# Blink LED 8 time to indicate loss of WIFI
blink_onboard_led(8)

# Reset Pico - hopefully a reset will fix the WIFI...
print('Resetting Pico')
machine.reset()
