from flask import Flask, request, render_template, send_file
import subprocess
from marc import Sonifier
import os

app = Flask(__name__, template_folder='templates', static_folder='statics')

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/prikaci', methods=['POST'])
def upload():
	file = request.files['file']
	file.save('uploads/' + file.filename)
	p = Sonifier('uploads/' + file.filename)
	return send_file("download/izlez.mid", as_attachment = True)

if __name__ == "__main__":
	app.run(debug = True)
