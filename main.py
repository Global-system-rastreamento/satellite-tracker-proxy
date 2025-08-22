from flask import Flask, request
from xml.etree import ElementTree
import datetime

app = Flask(__name__)

@app.route("/messages", methods=["POST"])
def receive_messages():
    xml_data = request.data

    try:
        pass

    except ElementTree.ParseError as e:
        print(f"Erro ao analisar o XML: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>Invalid XML format.</stateMessage></stuResponseMsg>"""
        return response_xml, 400, {'Content-Type': 'text/xml'}
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>An internal error occurred.</stateMessage></stuResponseMsg>"""
        return response_xml, 500, {'Content-Type': 'text/xml'}