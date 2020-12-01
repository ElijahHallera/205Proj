from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import json
import requests
from prettyprinter import pprint
import random
import os
from dotenv import load_dotenv

# These 3 lines take steps to protect private api key
load_dotenv()
key = os.getenv('MY_ENV_VAR')
endpoint = os.getenv('ENDPOINT')

def dateCheck(year, month, day):
    leap = False
    # msg': 'Date must be between Jun 16, 1995 and Dec 01, 2020.'
    # Since our range is so small we can account for all leap years available in this limit

    # Set lower bound
    if year == 1995:
        if month == 6:
            if day < 16:
                # If we hit lower bound then we default to the lowest possible limit
                return dateCheck(year, month, 16)

    # Set upper bound
    elif year == 2020:
        if month == 12:
            if day > 1:
                # If we hit upper bound then we default to highest possible limit
                return dateCheck(year, month, 1)

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


year = random.randrange(1995, 2021)
month = random.randrange(1, 13)
day = random.randrange(1, 32)

date = dateCheck(year, month, day)

payload = {
    'api_key': key,
    'date': date,
    # HD images only
    'hd': 'True'

    # We use start_date and end_date if we want multiple pictures
    # 'start_date': date,
    # 'end_date': date
}

# TODO: some results return 'media_type': 'video', this is wrong and we will encounter problems so we must
#   try again and get a new result

try:
    r = requests.get(endpoint, params=payload)
    data = r.json()
    pprint(data)
except:
    print('please try again')

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def hello_world():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()