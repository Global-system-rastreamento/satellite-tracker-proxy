from flask import Flask, request
from xml.etree import ElementTree
import datetime

from app.core.logger import get_logger
from app.connection.main_server_conection import main_server_connection

app = Flask(__name__)
logger = get_logger(__name__)

LEAP_SECONDS = -18
def decode_time(gps_value, unix_time):
    utc_time = datetime.datetime.fromtimestamp(unix_time, tz=datetime.timezone.utc)
    gw_time_seconds = utc_time.hour * 3600 + utc_time.minute * 60 + utc_time.second
    
    gps_time_of_day = (gps_value * 6) + (gw_time_seconds // 720) * 720
    
    utc_corrected_time_seconds = gps_time_of_day + LEAP_SECONDS
    
    if utc_corrected_time_seconds < gw_time_seconds:
        utc_corrected_time_seconds += 720
    
    final_time = utc_time.timestamp() + utc_corrected_time_seconds
    
    return datetime.datetime.fromtimestamp(final_time, tz=datetime.timezone.utc)
def decode_payload(payload_hex):
    try:
        payload_bytes = bytes.fromhex(payload_hex[2:])
        if len(payload_bytes) != 9:
            raise ValueError("Payload length is not 9 bytes.")

        byte0 = payload_bytes[0]
        message_type = byte0 & 0b11
        battery_status = (byte0 >> 2) & 0b1
        gps_valid = (byte0 >> 3) & 0b1

        lat_bytes = payload_bytes[1:4]
        lat_int = int.from_bytes(lat_bytes, 'big', signed=True)
        latitude = lat_int * (90.0 / (2**23))

        lon_bytes = payload_bytes[4:7]
        lon_int = int.from_bytes(lon_bytes, 'big', signed=True)
        longitude = lon_int * (180.0 / (2**23))

        speed_kmh = payload_bytes[7]
        
        byte8 = payload_bytes[8]
        battery_byte8 = (byte8 >> 7) & 0b1
        time_modulo = byte8 & 0b1111111

        return {
            'message_type': message_type,
            'battery_status': 'OK' if battery_status == 0 else 'Replace',
            'gps_valid': 'Valid' if gps_valid == 0 else 'Failed',
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'speed_kmh': speed_kmh,
            'battery_status_byte8': 'OK' if battery_byte8 == 0 else 'Replace',
            'time_modulo': time_modulo
        }
    except (ValueError, IndexError) as e:
        logger.info(f"Erro na decodificação do payload: {e}")
        return None
@app.route("/messages", methods=["POST"])
def receive_messages():
    xml_data = request.data

    try:
        root = ElementTree.fromstring(xml_data)

        if root.tag == "stuMessages":
            message_id = root.attrib.get("messageID")
            logger.info(f"Pacote de dados (stuMessages) recebido. MessageID: {message_id}")

            for stu_message in root.findall("stuMessage"):
                esn = stu_message.find("esn").text
                unix_time = stu_message.find("unixTime").text
                payload = stu_message.find("payload").text

                logger.info("-" * 20)
                logger.info(f"  ESN: {esn}")
                logger.info(f"  Unix Time: {unix_time}")
                logger.info(f"  Payload: {payload}")

                decoded_data = decode_payload(payload)
                if decoded_data:
                    event_time_utc = decode_time(decoded_data['time_modulo'], int(unix_time))
                    decoded_data["event_time_utc"] = event_time_utc.isoformat()
                    
                    logger.info(f"  Horário do evento (UTC): {event_time_utc.isoformat()}")
                    logger.info(f"  Latitude: {decoded_data['latitude']}°")
                    logger.info(f"  Longitude: {decoded_data['longitude']}°")
                    logger.info(f"  Velocidade: {decoded_data['speed_kmh']} km/h")
                    logger.info(f"  Tipo de Mensagem: {decoded_data['message_type']}")
                    logger.info(f"  Status da Bateria (Byte 0): {decoded_data['battery_status']}")
                    logger.info(f"  Status da Bateria (Byte 8): {decoded_data['battery_status_byte8']}")
                    logger.info(f"  GPS Válido: {decoded_data['gps_valid']}")

                    main_server_connection.send_data(esn, decoded_data)
                else:
                    logger.info("  Erro: Falha ao decodificar a carga de dados.")
                    
                
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://cody.glpconnect.com/XSD/StuResponse_Rev1_0.xsd" deliveryTimeStamp="{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S GMT')}" correlationID="{message_id}"><state>pass</state><stateMessage>Messages received and processed successfully.</stateMessage></stuResponseMsg>"""
            return response_xml, 200, {'Content-Type': 'text/xml'}

        elif root.tag == "prvmsgs":
            prv_message_id = root.attrib.get("prvMessageID")
            logger.info(f"Pacote de provisionamento (prvmsgs) recebido. prvMessageID: {prv_message_id}")
            
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?><prvResponseMsg xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://cody.glpconnect.com/XSD/ProvisionResponse_Rev1_0.xsd" deliveryTimeStamp="{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S GMT')}" correlationID="{prv_message_id}"><state>PASS</state></prvResponseMsg>"""
            return response_xml, 200, {'Content-Type': 'text/xml'}

        else:
            logger.info(f"Formato XML desconhecido: {root.tag}")
            response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>Unknown message type.</stateMessage></stuResponseMsg>"""
            return response_xml, 400, {'Content-Type': 'text/xml'}

    except ElementTree.ParseError as e:
        logger.info(f"Erro ao analisar o XML: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>Invalid XML format.</stateMessage></stuResponseMsg>"""
        return response_xml, 400, {'Content-Type': 'text/xml'}
    
    except Exception as e:
        logger.info(f"Ocorreu um erro: {e}")
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><stuResponseMsg><state>fail</state><stateMessage>An internal error occurred.</stateMessage></stuResponseMsg>"""
        return response_xml, 500, {'Content-Type': 'text/xml'}