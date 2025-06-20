#!/usr/bin/env python

# Sensor configuration...
# Note - Each array below must be equal in length to len(SensorName)

ModuleName = '[Enter a name...]'
ModuleLoc = '[Enter a location...]'
SensorName = ["Sensor1", "Sensor2", "Sensor3", "...", "Sensor255"]
SensorType = ['Type1', 'Type2', 'Type3', '...', 'Type255']
# 'T1w' = One-Wire Temperature Sensor 
# 'Analogue, = ADC reading
# 'PIR' = Passive Infrared sensor / motion sensor

# The following are planned but not yet supported...
# 'Counter_R' = Rising-Edge IO pulse counter
# 'Counter_F' = Falling-Edge IO pulse counter
# 'Int_Temp' = local / internal temperature
# 'Throttle_Status' = CPU Throttle status (Current throttle status)
# 'Throttle_Level' = CPU Throttle level (% time throttled)
# 'Ping' = network ping success (%)
# 'Electric_Whrs_import_today' = Electricity usage meter (daily)
# 'Electric_kW' = Electricity usage meter (Watts now)
# 'SolarPV_Whrs_gen_today' = Solar PV generation meter (daily)
# 'SolarPV_W' = Solar PV generation meter (Watts now)
# 'DHTxx_T' = DHT22 or DHT11 Temperature
# 'DHTxx_H' = DHT22 or DHT11 Humidity
# 'DHTxx_TH' = DHT22 or DHT11 Temperature
# 'Rain' = Rain sensor

SensorLoc = [1, 2, 3, 4, 255]

# Sensor output calculation (gain & offset)
# Output = Ax^2 + Bx + C
Sensor_A = [0.0, 0.0, 0.0, 0.0, 0.0]
Sensor_B = [1.0, 1.0, 1.0, 1.0, 1.0]
Sensor_C = [0.0, 0.0, 0.0, 0.0, 0.0]

# Sensor Error & Warning thresholds
# Set Warning and Reset thresholds to 0 to disable
HighWarning = [0,0,0,0,0]
HighReset   = [0,0,0,0,0]
LowWarning  = [0,0,0,0,0]
LowReset    = [0,0,0,0,0]

# Domoticz config
Domoticz_En = True
DomoticzIDX = ['x', 'x', 'x', 'x', 'x'] # Use 'x' to disable logging to Domoticz for each sensor

# Other options

# Number of active sensors
ActiveSensors = len(SensorName)

# Measurement interval in seconds
MeasurementInterval = 5

# Log interval in seconds
LogInterval = 60

# Number of Readings to capture
# Set to 0 to run continuously
NumReadings = 0
