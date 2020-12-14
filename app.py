from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import requests
from prettyprinter import pprint
import random
import os
import io
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

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

        # CALLING PICREQUEST HERE WHEN THERE IS AND IMAGE OR GIF
        # THIS FORCES THE RECURSION RATHER THAN EXCEPTION UNTIL WE GET AN IMAGE
        # THIS FIXED THE NONETYPE ERROR WE WERE GETTING
        # THUS LEADS TO FINALLY RETURNING AN OBJ AT END.
        if data["media_type"] != 'image' or data["url"][-3] == 'g' or data["hdurl"][-3] == 'g':
            raise Exception("Result not an Image")

        ''' Parse the data for easier usability '''
        obj = parser(data)

    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print("Trying again...")
        picRequest()

    if obj is None:
        picRequest()
    else:
        return obj


def sepia(pixel):
    if pixel[0] < 63:
        r, g, b = int(pixel[0] * 1.1), pixel[1], int(pixel[2] * .9)
    elif pixel[0] > 62 and pixel[0] < 192:
        r, g, b = int(pixel[0] * 1.15), pixel[1], int(pixel[2] * .85)
    else:
        r = int(pixel[0] * 1.08)
        if r > 255: r = 255
        g, b = pixel[1], pixel[2] // 2
    return r, g, b

def imageProcessing(imageURL):

    if(len(imageURL) == 0):
        print("empty")
    else:
        print("PROCESSING IMAGE URL AND SAVING TO LIST")

    storageList = []
    buffer = io.BytesIO()
    buffer2 = io.BytesIO()
    buffer3 = io.BytesIO()

    response = requests.get(imageURL)
    print(response)

    #     Filter the Image to Grayscale
    #     GRAYSCALE WILL NOT WORK IF THE IMAGE IS MEGA PIXELATED OR BLURRY OR HAS A BLACK BORDER AND TEXT
    #     OTHERWISE THIS VERSION OF GRAYSCALE WORKS FOR IMAGES GENERATED
    image = Image.open(BytesIO(response.content))
    resultingImage = Image.new('RGB', image.size)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r, g, b = image.getpixel((x, y))
            if(r == 0 and g == 0 and b == 0):
                resultingImage.putpixel((x, y), (0, 0, 0))
            else:
                gray = int(r * 0.2126 + g * 0.7152 + b * 0.0722)
                resultingImage.putpixel((x, y), (gray, gray, gray))
    resultingImage.save(buffer, format='JPEG')
    buffer.seek(0)

    data_uri = base64.b64encode(buffer.read()).decode('ascii')
    storageList.append(data_uri)

    #     Filter the Image to Sepia
    image2 = Image.open(BytesIO(response.content))
    sepia_list = map(sepia, image2.getdata())
    image2.putdata(list(sepia_list))
    image2.save(buffer2, format='JPEG')
    buffer2.seek(0)

    data_uri2 = base64.b64encode(buffer2.read()).decode('ascii')
    storageList.append(data_uri2)

    #     Filter the Image to Negative
    image3 = Image.open(BytesIO(response.content))
    negative_list = [(255 - p[0], 255 - p[1], 255 - p[2]) for p in image.getdata()]
    image3.putdata(negative_list)
    image3.save(buffer3, format='JPEG')
    buffer3.seek(0)

    data_uri3 = base64.b64encode(buffer3.read()).decode('ascii')
    storageList.append(data_uri3)

    if not storageList:
        print("STORAGE LIST IS EMPTY")
    else:
        print("STORAGE LIST HAS ELEMENTS")
        print("PROCESSING IS DONE")

    return storageList

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/aboutUS')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/pic')
def pic():

    '''
     processed images are stored in imgList
     We need to iterate through the list and display the images
     We can do this with javascript or we can hardcode the pass imgList[0], imgList[1]...etc
    '''

    obj = picRequest()

    imgList = imageProcessing(obj.hdurl)

    return render_template('pic.html', hdurl=obj.hdurl, title=obj.title, disc=obj.explanation, date=obj.picDate, img1=imgList[0], img2=imgList[1], img3=imgList[2])

if __name__ == '__main__':
    app.run()