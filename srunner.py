import os
from flask import Flask, render_template
from flask_zurb_foundation import Foundation

app = Flask(__name__)
Foundation(app)

@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
