#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageFont, ImageTk
import datetime
from gpiozero import Button


class eink:

    # constructor; it initializes all data members per passed parameters
    def __init__ (self):
        self.buttons = [Button(5), Button(6), Button(13), Button(19)]
        self.epd = None
        self.root = None
        self.canvas = None
        self.displayepd = True
        self.iteration = 0
        self.displayPage = 2
        self.font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        self.font10 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 10)
        self.font22 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 22)
        self.font28 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 28)
        self.font64 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 64)
        self.font128 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 128)

    def handleButtonPress(self, button):
        logging.info("User pressed button %i", button.pin.number)

        if button.pin.number == 5:
            self.displayPage = 1
        elif button.pin.number == 6:
            self.displayPage = 2
        elif button.pin.number == 13:
            self.displayPage = 3
        elif button.pin.number == 19:
            self.epd.Clear(255)
            self.epd.sleep()
            logging.info("User pressed button 19 - exit")
            epd2in7.epdconfig.module_exit()
            exit()

    def initDisplay(self):

        # set up button handlers
        for button in self.buttons:
            button.when_pressed = self.handleButtonPress

        self.epd = epd2in7.EPD()
        self.width = self.epd.height
        self.height = self.epd.width

        # set up window for display

        try:
            self.root = tk.Tk()
            self.root.geometry('%dx%d' % (self.width, self.height))
            self.canvas = Canvas(self.root, width = self.width, height = self.height)
            self.canvas.pack()

        except Exception as e:
            logging.error("Unable to get window")

        try:
            logging.info("Initalize E-Ink display")

            if self.displayepd:
                self.epd.init()
                self.epd.Clear(255)

        except IOError as e:
            logging.info(e)

    def displayTempsAndChart(self, temps, changes, datasets, timebetweenupdates):
        try:

            blackimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(blackimage)

            # display current date / time
            text = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
            draw.text((10, 0), text, font=self.font22, fill=0)

            # format the temperature string
            text = ''
            position = 1
            for temp in temps:
                text = text + "  {0:3.1f} ".format(temp)
                position = position + 1

            # get the minimum and maximum values
            minTemp = 1000
            maxTemp = -1000

            for dataset in datasets:
                for dataitem in dataset:
                    if minTemp > dataitem:
                        minTemp = dataitem

                    if maxTemp < dataitem:
                        maxTemp = dataitem

            draw.text((10, 28), text, font=self.font28, fill=0)
            draw.line((0, 60, self.width, 60), width = 2, fill = 0)

            # draw charts
            draw.line((5, 72 + 98, self.width - 5, 72 + 98), width = 0, fill = 0)
            draw.line((5, 72, 5, 72 + 95), fill = 0)

            datasetIndex = 0
            for data in datasets:

                datasetIndex += 1

                x = 0
                y = 0
                v = 0

                if (len(data) > 1):
                    lastdatapoint = -1
                    xdist = (self.width - 10) / (len(data) - 1)
                    xpos = 5

                    for rawdatapoint in data:
                        datapoint = rawdatapoint / ((maxTemp) / 80)
                        v = rawdatapoint
                        x = xpos + xdist
                        y = self.height - 5 - datapoint
                        if lastdatapoint > 0:
                            draw.line((xpos, self.height - 5 - lastdatapoint,
                                       x, y), width = 1, fill = 0)

                            xpos = xpos + xdist

                        lastdatapoint = datapoint

                    text = "{0:3.1f} ".format(rawdatapoint)
                    draw.text((x - (24 * 1), y - 1), text, font = self.font10, fill = 0)

            # every so often clear the display
            self.iteration += 1
            if self.displayepd and self.iteration > 15:
                self.epd.Clear(255)
                self.iteration = 0

            if (self.canvas != None):
                photo = ImageTk.PhotoImage(blackimage)
                self.canvas.create_image(0, 0, image=photo, anchor="nw")
                self.canvas.pack()
                self.canvas.update_idletasks()

            if self.displayepd:
                self.epd.display(self.epd.getbuffer(blackimage))

        except IOError as e:
            logging.info(e)

    def displayTempsBig(self, temps, changes, datasets, timebetweenupdates):
        try:
            blackimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(blackimage)

            # display current date / time
            text = datetime.datetime.now().strftime("%m/%d/%Y   %H:%M:%S")
            draw.text((10, 0), text, font=self.font22, fill=0)
            draw.line((0, 30, self.width, 30), width=2, fill=0)

            # format the temperature string
            text = ''
            position = 0
            rowCount = 0
            for temp in temps:
                # we want to display up to 2 rows
                rowCount = rowCount + 1
                if rowCount > 2:
                    break

                text = ""
                if temp != None:
                    text = "{:.1f} ".format(temp)
                else:
                    text = "N/A"

                draw.text((10, 28 + position * 64), text, font=self.font64, fill=0)
                draw.line((0, 94 + position * 64, self.width, 94 + position * 64), width=2, fill=0)
                position = position + 1

            position = 0
            rowCount = 0
            for rate in changes:
                # we want to display up to 2 rows
                rowCount = rowCount + 1
                if rowCount > 2:
                    break

                text = ""
                if rate != None:
                    text = "{:.1f} ".format(rate)
                else:
                    text = "N/A"

                draw.text((172, 32 + position * 64), text, font=self.font24, fill=0)
                draw.text((210, 60 + position * 64), "min", font=self.font24, fill=0)
                draw.line((200, 74 + position * 64, 220, 74 - 20 + position * 64), width=2, fill=0)
                position = position + 1

            # every so often clear the display
            self.iteration += 1
            if self.displayepd and self.iteration > 15:
                self.epd.Clear(255)
                self.iteration = 0

            if (self.canvas != None):
                photo = ImageTk.PhotoImage(blackimage)
                self.canvas.create_image(0, 0, image=photo, anchor="nw")
                self.canvas.pack()
                self.canvas.update_idletasks()

            if self.displayepd:
                self.epd.display(self.epd.getbuffer(blackimage))

        except IOError as e:
            logging.info(e)


    def displayTable(self, temps, changes, datasets, timebetweenupdates):
        try:
            blackimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(blackimage)

            # display current date / time
            text = datetime.datetime.now().strftime("%m/%d/%Y   %H:%M:%S")
            draw.text((10, 0), text, font=self.font22, fill=0)
            draw.line((0, 30, self.width, 30), width=2, fill=0)

            # format the temperature string
            text = ''
            position = 0

            for temp in temps:
                text = ""
                if temp != None:
                    text = "{:.2f} ".format(temp)
                else:
                    text = "N/A"

                draw.text((10, 28 + position * 28), text, font=self.font24, fill=0)
                draw.line((0, 58 + position * 28, self.width, 58 + position * 28), width=1, fill=0)
                position = position + 1

            position = 0
            for rate in changes:
                text = ""
                if rate != None:
                    text = "{:.2f} ".format(rate)
                else:
                    text = "N/A"

                draw.text((172, 32 + position * 28), text, font=self.font24, fill=0)
                position = position + 1

            # every so often clear the display
            self.iteration += 1
            if self.displayepd and self.iteration > 15:
                self.epd.Clear(255)
                self.iteration = 0

            if (self.canvas != None):
                photo = ImageTk.PhotoImage(blackimage)
                self.canvas.create_image(0, 0, image=photo, anchor="nw")
                self.canvas.pack()
                self.canvas.update_idletasks()

            if self.displayepd:
                self.epd.display(self.epd.getbuffer(blackimage))

        except IOError as e:
            logging.info(e)

    def displayTemps(self, temps, changes, datasets, timebetweenupdates):

        if self.displayPage == 1:
            self.displayTempsAndChart(temps, changes, datasets, timebetweenupdates)
        elif self.displayPage == 2:
            self.displayTempsBig(temps, changes, datasets, timebetweenupdates)
        elif self.displayPage == 3:
            self.displayTable(temps, changes, datasets, timebetweenupdates)

    def turnOff(self):

        try:
            logging.info("Clear...")
            if self.displayepd:
                self.epd.Clear(255)
                epd2in7.epdconfig.module_exit()

            logging.info("Goto Sleep...")
            self.epd.sleep()

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd2in7.epdconfig.module_exit()
            exit()
