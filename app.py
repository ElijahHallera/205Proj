from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import json
import requests
from prettyprinter import pprint
from urllib.request import urlopen
import ssl

key='ddoOH0QwXpcTGp5Hsyv8kxYDbdheTri8sDBp36qX'

# ssl._create_default_https_context = ssl._create_unverified_context
# my_site='https://api.nasa.gov/planetary/apod?api_key=' + key
# site_html=urlopen(my_site)
# print(site_html.read())

payload = {
    'api_key': key,
    'start_date': '2020-05-01',
    'end_date': '2020-05-01'
}

endpoint = 'https://api.nasa.gov/planetary/apod'
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