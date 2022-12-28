#!/usr/bin/python3

import logging
# set up the logger
logging.basicConfig(filename="/tmp/thermodisplay.log", format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)
import os
import time
import socket
from requests import get
# logging facility: https://realpython.com/python-logging/
from dataaccess import apis
from waveshare_epd import einkdisplay

timebetweenupdates = 10

def main():
    # log start up message
    logging.info("***************************************************************")
    logging.info("eink Display process has started")
    logging.info("Running %s", __file__)
    logging.info("Working directory is %s", os.getcwd())

    localipaddress = "IP: Unknown"
    try:
        hostname = socket.gethostname()
        externalip = get('https://api.ipify.org').text
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        localipaddress = s.getsockname()[0]
        logging.info("Hostname is %s", hostname)
        logging.info("Local IP is %s and external IP is %s", localipaddress, externalip)

    except Exception as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get network information")

    # initialize eink display, if present
    einkDisplay = einkdisplay.eink()
    einkDisplay.initDisplay()
    logging.info("Found eink display")

    # check how many sensors there are
    dataInfo= apis.getdataInfo()
    numSensors = dataInfo['numSensors']
    logging.info("Number of sensors detected: %s", numSensors)
    timeBetweenUpdates = dataInfo['timeBetweenUpdates']
    logging.info("Time between data updates: %s", timeBetweenUpdates)

    # list to store historical data to draw a chart
    data = []
    for s in range(numSensors):
        data.append([])

    while True:
        values = []
        changes = []
        for sensorId in range(1, numSensors + 1):
            t = apis.getTemperatureData(sensorId)
            c = apis.getTemperatureChange(sensorId)
            values.append(t)
            changes.append(c)
            data[sensorId - 1].append(t)

        # keep length of items to show in chart to less than 120
        while (len(data[sensorId - 1]) > 120):
            data[sensorId - 1].pop(0)

        # logging.info("Iteration: %d Temperature data: %s", iteration, tempsString)
        if einkDisplay != None:
            einkDisplay.displayTemps(values, changes, data, timebetweenupdates)

        time.sleep(timebetweenupdates)


# main program
if __name__ == '__main__':

    try:
        main()

    except Exception as e:
        logging.exception("Exception occurred in main")

    logging.info("ThermoDisplay has terminated")