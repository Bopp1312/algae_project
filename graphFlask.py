from flask import Flask, Markup, render_template
import sqlite3
import time 
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime

app = Flask(__name__)

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def get_data():
    global co2
    global hours
    global minutes
    global humidity
    global temp
    global ph

    # get an array of timestamps from database
    connection = sqlite3.connect("sensorDatabase/sensorDatabase.db")
    cursor = connection.cursor()
    hours = 24.0
    window = hours*3600.0
    current_time = time.time()
    seconds_back = current_time - window
    cursor.execute("SELECT * FROM ENV_data WHERE seconds >" + str(seconds_back) + "  ORDER BY seconds DESC")
    results = cursor.fetchall()
    connection.close()
    timestamps = [x[0] for x in results]
    seconds    = [x[4] for x in results]
    co2        = [x[1] for x in results]
    temp       = [x[2] for x in results]
    humidity   = [x[3] for x in results]
    ph         = [x[5] for x in results]
    
    most_recent = np.max(seconds)
    minutes = np.around((most_recent - seconds)/60.0,2)
    hours = minutes/60.0
    
@app.route('/line')
def line():
    global temp
    global humidity
    global co2
    global hours
    global ph
    get_data()
    now = datetime.now()

    gs = GridSpec(nrows=2, ncols=2)
    temp_f = [9.0*t/5.0+32.0 for t in temp]
    x_ticks = np.linspace(24, 0, 25)

    fig_co2 = plt.figure()
    fig_env = plt.figure()
    fig_ph = plt.figure()
    ax1 = fig_co2.add_subplot(111)
    ax2 = fig_env.add_subplot(211)
    ax3 = fig_env.add_subplot(212)
    ax4 = fig_ph.add_subplot(111)
    
    ax1.grid()
    ax1.set_ylim(400, 2000)
    ax1.set_xticks(x_ticks)
    ax1.plot(hours, co2, 'blue')
    ax1.set_xlabel("Time (Hours)")
    ax1.set_ylabel("CO2 (PPM)")
    ax1.invert_xaxis()
    
    ax2.grid()
    ax2.set_xticks(x_ticks)
    ax2.plot(hours, temp_f, 'red')
    ax2.set_ylabel("Temperature (F)")
    ax2.invert_xaxis()
    
    ax3.grid()
    ax3.set_xticks(x_ticks)
    ax3.plot(hours, humidity, 'green')
    ax3.set_xlabel("Time (Hours)")
    ax3.set_ylabel("Humidity (%)")
    ax3.invert_xaxis()

    ax4.grid()
    ax4.set_xticks(x_ticks)
    #ax4.set_ylim(8,9)
    ax4.plot(hours, ph, 'purple')
    ax4.set_xlabel("Time (Hours)")
    ax4.set_ylabel("Acidity (pH)")
    ax4.invert_xaxis()

    fig_co2.savefig('static/matplot_co2.png')
    fig_env.savefig('static/matplot_env.png')
    fig_ph.savefig('static/matplot_ph.png')
    plt.close()

    date = now.strftime("%m-%d-%Y, %H:%M:%S")
    return render_template('matplot.html', title="Enviornmental Data from The Apartment", date=date )

@app.route('/pie')
def pie():
    pie_labels = labels
    pie_values = values
    return render_template('pie_chart.html', title='Bitcoin Monthly Price in USD', max=17000, set=zip(values, labels, colors))

if __name__ == '__main__':
    app.run(debug = False, host='0.0.0.0', port=8080)
