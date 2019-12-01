#!/usr/bin/env python
"""
/* ######################################################################### */
/*
 * This file was created by www.DavesMotleyProjects.com
 *                                                                  */
/* ######################################################################### */
"""

import io
import os
import time
import datetime
import serial

from time import sleep      # to create delays

# from locale import format   # to format numbers PY2
import locale # PY3

from shutil import rmtree   # to remove directories


PathValid = False
FileName = ""
FilePath = ""
dataIndex = 0

FAIL_PATH = "/media/pi/USBDRIVE1/"
DRIVE_PATH = "/media/pi/USBDRIVE/"
AUTH_PATH = DRIVE_PATH + "validate.txt"

MAX_ROWS_IN_FILE = 65535


"""############################################################################

    Function:       chk_usb_on_start
    Description:    This function is called at the start of the program
    execution and provides a helpful message to the user on the approprate
    actions to take to start datalogging, if a valid usb drive was not found.

############################################################################"""


def chk_usb_on_start():

    global PathValid, DRIVE_PATH, AUTH_PATH


    # if the "validate.txt" file is not found on startup, prompt the user to
    # install the appropriate usb drive
    if not (os.path.exists(AUTH_PATH)):
        print("\n")
        print("To start datalogging, insert a usb drive that is formatted as FAT, with the ")
        print("label 'USBDRIVE', that has a text file named 'validate.txt' at the top level ")
        print("of the usb drive.\n")

        while not (os.path.exists(AUTH_PATH)):
            sleep(1)
            if (os.path.isdir(DRIVE_PATH)):
                if (os.path.isdir(FAIL_PATH)):
                    PathValid=True
                    validate_usb_write()
                    PathValid=False
                    print("To finish path correction, remove and replace USBDRIVE.")

    print("'USBDRIVE' with 'validate.txt' file found.")


def set_path_invalid():

    global PathValid, dataIndex

    # if the path is already defined as invalid, do nothing, else, set the
    # path as invalid, inform the user, and reset the dataIndex.

    if not PathValid == False:
        PathValid = False
        print("USB path is not valid, corrupted, missing, or ejected")
        dataIndex = 0

def validate_usb_write():

    global PathValid, DRIVE_PATH, AUTH_PATH

    # if we already know the path isn't valid, this check isn't needed.
    if PathValid == False:
        return

    # if the "validate.txt" file is not found, then we may have created a
    # 'fake' USB drive path accidentally...
    if not (os.path.exists(AUTH_PATH)):
        print("path corruption suspected")
        sleep(1)

        # if the "validate.txt" file is not found a second time...
        if not (os.path.exists(AUTH_PATH)):
            print("path corruption confirmed")
            print("validate.txt file was not found")
            set_path_invalid()

            # remove the drive path. the location that is being written to is
            # not the USB drive. This happens rarely, when attempting a write
            # to a USB that doesn't exist. Linux will create a temporary
            # location, and will appear to be logging to the USB, but isn't.
            rmtree(DRIVE_PATH, ignore_errors = True)

            # if the path no longer exists then rmtree worked, and the
            # incorrect path was deleted.
            if not (os.path.isdir(DRIVE_PATH)):
                print("path corruption corrected")

def start_new_file():

    global PathValid, FileName, FilePath, dataIndex

    # Assemble the filename based on the current date and time. Then assign
    # the FilePath to start using the new file.
    FileName = str("_".join(str(datetime.datetime.now()).split(" ")))
    FileName = str("_".join(FileName.split(":")))
    FileName = str("_".join(FileName.split(".")))
    FileName = str("_".join(FileName.split("-")))
    FileName = FileName + ".csv"
    FilePath = DRIVE_PATH + FileName

    # if the drive path exists...
    if (os.path.isdir(DRIVE_PATH)):

        # create a new blank file. If this file existed, which it shouldn't,
        # open with 'w' would overwrite it.
        mFile = open(FilePath, "w")

        # display to the user that a new file has been started
        print()
        print("#############################################################")
        print("New File: " + FileName)
        print("#############################################################")

        mFile.write("Index, Date, Time, Data \r\n")
        mFile.close()
        PathValid = True
        dataIndex = 1

    # if the drive path didn't exist...
    else:

        set_path_invalid();

def read_data():

    global PathValid, FileName, FilePath, dataIndex, ser

    if (PathValid == False):
        start_new_file()
        if (PathValid == False):
            return

    valueString = ""                # reset the string that will collect chars
    
    #mchar = ser.read()             # PY2 read the next char from the serial port
    mchar = ser.read().decode()     # PY3
    
    while (mchar != '\n'):
        if (mchar != '\r'):
            valueString += mchar
        #mchar = ser.read()          # PY2
        mchar = ser.read().decode() # PY3

    millis = int(round(time.time() * 1000))
    rightNow = str(datetime.datetime.now()).split()
    mDate = rightNow[0]
    mTime = rightNow[1]

    # format the full string: index, timestamp, and data
    # locale.format_string('%05d', dataIndex) ## PY3
     
    #fileString = str(format('%05d', dataIndex)) + ", " + \
        #str(mDate) + ", " + str(mTime) + ", " + valueString
        
    fileString = locale.format_string('%05d', dataIndex) + ", " + \
        str(mDate) + ", " + str(mTime) + ", " + valueString

    try:
        if (os.path.exists(FilePath)):
            print(fileString)
            fileString += "\r\n"
            mFile = open(FilePath, "a", 1)
            mFile.write(fileString)
            mFile.close()
            dataIndex += 1
            validate_usb_write()
        elif (os.path.isdir(DRIVE_PATH)):
            start_new_file()
        else:
            set_path_invalid()
    except:
        print("write failed")
    if (dataIndex >= MAX_ROWS_IN_FILE):
        start_new_file()

def main():

    global ser

    ser = serial.Serial()
    ser.baudrate = 57600
    ser.timeout = None
    ser.port = '/dev/ttyACM0'

    print(ser)
    print(ser.name)
    ser.open()
    print("Serial port is open: ", ser.isOpen())

    chk_usb_on_start()

    start_new_file()

    try:
        while (True):
            read_data()
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print("Serial port is open: ", ser.isOpen())

    return 0

if __name__ == '__main__':
    main()
