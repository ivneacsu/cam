#!/usr/bin/env python
"""
/* ######################################################################### */

/* http://www.davesmotleyprojects.com/raspi/raspi-data-logger/raspi-data-logger.html

 * This file was created by www.DavesMotleyProjects.com
 *
 * This software is provided under the following conditions:
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * 'Software'), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *                                                                           */
/* ######################################################################### */
"""

import io
import os
import time
import datetime
import serial

from time import sleep      # to create delays
from locale import format   # to format numbers
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

## main()
def chk_usb_on_start():
## validate_usb_write()

    global PathValid, DRIVE_PATH, AUTH_PATH


    # if the "validate.txt" file is not found on startup, prompt the user to
    # install the appropriate usb drive
    if not (os.path.exists(AUTH_PATH)):
        print "\n"
        print "To start datalogging, insert a usb drive that is formatted as FAT, with the "
        print "label 'USBDRIVE', that has a text file named 'validate.txt' at the top level "
        print "of the usb drive.\n"

        while not (os.path.exists(AUTH_PATH)):
            sleep(1)
            if (os.path.isdir(DRIVE_PATH)):
                if (os.path.isdir(FAIL_PATH)):
                    PathValid=True
                    validate_usb_write()
                    PathValid=False
                    print "To finish path correction, remove and replace USBDRIVE."

    print "'USBDRIVE' with 'validate.txt' file found."



"""############################################################################

    Function:       set_path_invalid
    Description:    This function is called whenever a path verification check
    has failed in order to inform the user of the error, and to set the
    PathValid variable to false to prevent any further attempts to write to
    the usb drive until the error condition is corrected.

############################################################################"""

## validate_usb_write()
## start_new_file()
## read_data()
def set_path_invalid():

    global PathValid, dataIndex

    # if the path is already defined as invalid, do nothing, else, set the
    # path as invalid, inform the user, and reset the dataIndex.

    if not PathValid == False:
        PathValid = False
        print "USB path is not valid, corrupted, missing, or ejected"
        dataIndex = 0


"""############################################################################

    Function:       validate_usb_write
    Description:    This function checks for the creation of an erroneous USB
    drive path, which can occur rarely if the USB drive is removed, without
    ejecting it first, and the removal occurs between the code that checks
    for a valid path, and where the data is written to the USB drive. If the
    USB doesn't exist, and the write occurs, a 'fake" USBDRIVE owned by root
    will be created and data logging will continue to that location, and all
    future insertions of the USB will be assigned USBDRIVE1, and data will not
    be written to the USB drive again. When this condition is detected, the
    condition will be automatically corrected by erasing the fake path.

    IMPORTANT: to detect this condition a text file called "validate.txt"
    needs to be placed on the USB drive.

############################################################################"""

## chk_usb_on_start()
## read_data()
def validate_usb_write():
## set_path_invalid()

    global PathValid, DRIVE_PATH, AUTH_PATH

    # if we already know the path isn't valid, this check isn't needed.
    if PathValid == False:
        return

    # if the "validate.txt" file is not found, then we may have created a
    # 'fake' USB drive path accidentally...
    if not (os.path.exists(AUTH_PATH)):
        print "path corruption suspected"
        sleep(1)

        # The sleep above is to provide some manner of debouncing, in case
        # the detection error of "validate.txt" was a timing / race condition.
        # After all, the result could be erasing all of our data, so it pays
        # to double-check.

        # if the "validate.txt" file is not found a second time...
        if not (os.path.exists(AUTH_PATH)):
            print "path corruption confirmed"
            print "validate.txt file was not found"
            set_path_invalid()

            # remove the drive path. the location that is being written to is
            # not the USB drive. This happens rarely, when attempting a write
            # to a USB that doesn't exist. Linux will create a temporary
            # location, and will appear to be logging to the USB, but isn't.
            rmtree(DRIVE_PATH, ignore_errors = True)

            # if the path no longer exists then rmtree worked, and the
            # incorrect path was deleted.
            if not (os.path.isdir(DRIVE_PATH)):
                print "path corruption corrected"



"""############################################################################

    Function:       start_new_file
    Description:    This function is called when a new file is needed to save
    data logging results. A filename is assembled based on the current Date
    and Time, and if the creation of the file is successful, the file is
    initialized with a header row. If all was successful, PathValid will be
    set to True (This is the only location where this is set to True)

############################################################################"""

## read_data()
## main()
def start_new_file():
## set_path_invalid()

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
        print
        print "#############################################################"
        print "New File: " + FileName
        print "#############################################################"
        print

        # write to the new file a header row to indicate what each of the
        # values represent. In this example, the 'Data' values are unknown. It
        # is expected that 'Data' is a string of an unknown number of values,
        # to which the proper csv formatting has been applied. If you know your
        # data formatting, and want to make this program specific, add your
        # data headers here.

        mFile.write("Index, Date, Time, Data \r\n")
        mFile.close()
        PathValid = True
        dataIndex = 1

    # if the drive path didn't exist...
    else:

        set_path_invalid();


"""############################################################################

    Function:       read_data
    Description:    This function reads the serial input, assembling chars
    until the new line character is received. On reception of a new line,
    the function generates a timestamp, which is pre-pended to the received
    data, and the entire string is written to the display and logged to the
    usb drive (if a valid drive exists).

############################################################################"""

## main()
def read_data():
## start_new_file()
## set_path_invalid()

    global PathValid, FileName, FilePath, dataIndex, ser

    # if there is currently no file to write to, attempt to create a file. If
    # that fails, simply return. This means that there is no valid USB inserted
    # so there is no reason to attempt writing to a file.

    if (PathValid == False):
        start_new_file()
        if (PathValid == False):
            return

    valueString = ""        # reset the string that will collect chars
    mchar = ser.read()      # read the next char from the serial port

    # continue reading characters and appending them to the valueString
    # (ignoring carriage returns) until a 'new line' character is received.

    while (mchar != '\n'):
        if (mchar != '\r'):
            valueString += mchar
        mchar = ser.read()

    # after a full valueString has been assembled, create the timestamp

    millis = int(round(time.time() * 1000))
    rightNow = str(datetime.datetime.now()).split()
    mDate = rightNow[0]
    mTime = rightNow[1]

    # format the full string: index, timestamp, and data

    fileString = str(format('%05d', dataIndex)) + ", " + \
        str(mDate) + ", " + str(mTime) + ", " + valueString


    # if execution reaches this point, then it is assumed that a valid USB is
    # inserted, and a file exists to write the data. Open the data file with
    # 'a' to append the new data, write the data string, close the file, and
    # increment the index.

    try:

        # before writing, double-check that the data logging file exists

        if (os.path.exists(FilePath)):
            print(fileString)
            fileString += "\r\n"
            mFile = open(FilePath, "a", 1)
            mFile.write(fileString)
            mFile.close()
            dataIndex += 1
            validate_usb_write()

        # if the file doesn't exist, but the drive path still exsists, then it
        # is possible that the file was deleted while in use.

        elif (os.path.isdir(DRIVE_PATH)):
            start_new_file()

        else:
            set_path_invalid()

    except:

        print("write failed")

    # if the number of rows written to the data file exceeds MAX_ROWS_IN_FILE
    # start a new file. This was added to address an issue where Excel would
    # not import more than 65535 rows from a csv file, when the csv is opened
    # directly, even though Excel is supposed to have a maximum number of rows
    # closer to 1048576.

    if (dataIndex >= MAX_ROWS_IN_FILE):
        start_new_file()


"""############################################################################

    Function:       main

############################################################################"""


def main():

    global ser

    ser = serial.Serial()
    ser.baudrate = 57600
    ser.timeout = None
    ser.port = '/dev/serial0'

    print ser
    print ser.name
    ser.open()
    print "Serial port is open: ", ser.isOpen()

    chk_usb_on_start()

    start_new_file()

    try:
        while (True):
            read_data()

    finally:
        ser.close
        print "Serial port is open: ", ser.isOpen()

    return 0


"""############################################################################

    This next section checks to see whether the file is being executed
    directly. If it is, then __name__ == '__main__' will evaluate as True, and
    the main() function will execute. If the file is being imported by another
    module, then __name__ will be set to the modules name instead.

############################################################################"""


if __name__ == '__main__':
    main()


"""############################################################################
    End of File: datalogger.py
############################################################################"""
