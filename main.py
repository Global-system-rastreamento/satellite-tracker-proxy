from flask import Flask, request
from xml.etree.ElementTree import ElementTree
import datetime

app = Flask(__name__)

@app.route("/messages", methods=["POST"])
def receive_messages():
    xml_data = request.data

    