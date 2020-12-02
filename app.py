from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/pic')
def pic():
    return render_template('pic.html')



if __name__ == '__main__':
    app.run()
