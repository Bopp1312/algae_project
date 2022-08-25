import sqlite3
import sys
import time
import board 
import adafruit_scd4x
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime
import numpy as np

# pairs [voltage, PH]
calibration_points = np.array([(1.530,7.0),(2.04,4.0),(10.0,1.016)])
x = calibration_points[:,0]
y = calibration_points[:,1]
z = np.polyfit(x,y,2)
print(z)

def getPHvalue(voltage):
    global z
    return(z[0]*voltage**2+z[1]*voltage+z[2])

#conn=sqlite3.connect('sensorDatabase/sensorDatabase.db')
#curs=conn.cursor()

i2c = board.I2C()
scd4x = adafruit_scd4x.SCD4X(i2c)
ads = ADS.ADS1015(i2c)

scd4x.start_periodic_measurement()
print("Waiting for measurement ...")


def add_data(seconds, co2, temp, hum, ph):
    conn=sqlite3.connect('sensorDatabase/sensorDatabase.db')
    curs=conn.cursor()
    curs.execute("INSERT INTO ENV_data values(datetime('now'), (?), (?), (?), (?), (?))", (co2, temp, hum, seconds, ph))
    conn.commit()
    conn.close()

while True:
    try:
        if scd4x.data_ready:

            seconds = time.time()
            chan = AnalogIn(ads,ADS.P0)
            ph = getPHvalue(chan.voltage)
            add_data(seconds, scd4x.CO2, scd4x.temperature, scd4x.relative_humidity, ph)
            today = datetime.today()
            timestamp = today.strftime("%b-%d-%Y_%H-%M-%S")
            print("Logged data: " + timestamp + " ==> " + str(seconds))
    except Exception as e:
            print(str(e))
            

