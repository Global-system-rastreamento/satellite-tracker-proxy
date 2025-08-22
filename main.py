from flask import Flask, request
from xml.etree import ElementTree
import datetime

app = Flask(__name__)

@app.route("/messages", methods=["POST"])
def receive_messages():
    xml_data = request.data

    try:
        root = ElementTree.fromstring(xml_data)

        if root.tag == "stuMessages":
            pass

        elif root.tag == "prvmsgs":
            prv_message_id = root.attrib.get("prvMessageID")
            print(f"Pacote de provisionamento (prvmsgs) recebido. prvMessageID: {prv_message_id}")
            
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?><prvResponseMsg xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://cody.glpconnect.com/XSD/ProvisionResponse_Rev1_0.xsd" deliveryTimeStamp="{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S GMT')}" correlationID="{prv_message_id}"><state>PASS</state></prvResponseMsg>"""
            return response_xml, 200, {'Content-Type': 'text/xml'}

        else:
            print(f"Formato XML desconhecido: {root.tag}")
            response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>Unknown message type.</stateMessage></stuResponseMsg>"""
            return response_xml, 400, {'Content-Type': 'text/xml'}

    except ElementTree.ParseError as e:
        print(f"Erro ao analisar o XML: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>Invalid XML format.</stateMessage></stuResponseMsg>"""
        return response_xml, 400, {'Content-Type': 'text/xml'}
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>An internal error occurred.</stateMessage></stuResponseMsg>"""
        return response_xml, 500, {'Content-Type': 'text/xml'}