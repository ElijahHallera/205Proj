from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import json
import requests
from prettyprinter import pprint
import random
import os
from dotenv import load_dotenv
from PIL import Image

# These 3 lines take steps to protect private api key
load_dotenv()
key = os.getenv('MY_ENV_VAR')
endpoint = os.getenv('ENDPOINT')

app = Flask(__name__)
Bootstrap(app)

class parser():
    def __init__(self, data):
        self.picDate = data["date"]
        self.copyright = data['copyright'] if len(data) > 7 else "No Copyright"
        self.explanation = data["explanation"]
        self.hdurl = data["hdurl"]
        self.mediaType = data["media_type"]
        self.title = data["title"]


# TODO imageProcessing function
# def imageProcessing(rawImageData):
# Sudo:
# PIL.image = rawImageData
# list = list()
# PIL.ImageProcesss(rawImageData)
# list.append(processedImage1)
# list.append(proccessedImageN)
# return list


'''
    This function makes sure our date is valid for the api request.
    Technically we don't need this because an exception is thrown if the request is bad,
    which in turn does a recursive call generating a new date and checking again, recursing if error
'''
def dateCheck(year, month, day):
    leap = False

    # Set lower bound
    if year == 1995 and month == 6 and day < 16:
        # If we hit lower bound then we default to the lowest possible limit
        return dateCheck(year, month, 16)

    # Set upper bound
    elif year == 2020 and month == 12 and day > 1:
        # If we hit upper bound then we default to highest possible limit
        return dateCheck(year, month, 1)

    # Since our range is so small we can account for all leap years available in this limit
    # Check for leap year
    if year % 4 == 0:
        leap = True

    # Check February
    if month == 2:
        # If its not a leap year and over limit 28 days, reassign day
        if day > 28 and not leap:
            return dateCheck(year, month, random.randrange(1, 29))
        # If leap year and over limit 29 days, reassign day
        elif day > 29 and leap:
            return dateCheck(year, month, random.randrange(1, 30))

    # Check April day limit
    if month == 4 and day > 30:
        return dateCheck(year, month, random.randrange(1, 31))

    # Check June day limit
    if month == 6 and day > 30:
        return dateCheck(year, month, random.randrange(1, 31))

    # Check September day limit
    if month == 9 and day > 30:
        return dateCheck(year, month, random.randrange(1, 31))

    # Check November day limit
    if month == 11 and day > 30:
        return dateCheck(year, month, random.randrange(1, 31))

    return f"{year}-{month}-{day}"


'''
        In this function we generate a random date between our NASA's limits (Jun 16, 1995 to Dec 01, 2020)
        We then pass those parameters into a recursive function which checks and accounts for:
            1. upper/lower bounds
            2. leap years
            3. Correct days of months
        The result of the function is a valid date within our limits.
        We then use that result to get a json object with our api requests
'''

def picRequest():

    # random.randrange(start, up-to-but-not-including)
    year = random.randrange(1995, 2021)
    month = random.randrange(1, 13)
    day = random.randrange(1, 32)
    date = dateCheck(year, month, day)

    payload = {
        'api_key': key,
        'date': date,
        'hd': 'True'
        # We use start_date and end_date if we want multiple pictures
        # 'start_date': date,
        # 'end_date': date
    }

    try:
        r = requests.get(endpoint, params=payload)
        data = r.json()

        pprint(data)
        if data["media_type"] != 'image':
            raise Exception("Result not an Image")

        # TODO:
        #  use PIL image to get the raw image data and assign to variable
        #  use the variable for image processing
        # imgList = imageProcessing(data["hdurl"])

        ''' Parse the data for easier usability '''
        obj = parser(data)
        print(obj.copyright)

        return obj

    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print("Trying again...")
        picRequest()

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/pic')
def pic():
    '''
     processed images are stored in imgList
     We need to iterate through the list and display the images
     We can do this with javascript or we can hardcode the pass imgList[0], imgList[1]...etc
    '''

    obj = picRequest()
    imgList = imageProcessing(obj.hdurl)

    # return render_template('pic.html', hdurl=obj.hdurl, img1=imgList[0], img2=imgList[1])
    return render_template('pic.html', hdurl=obj.hdurl, title=obj.title, disc=obj.explanation, date=obj.picDate)
    # return render_template('pic.html')


if __name__ == '__main__':
    app.run()
