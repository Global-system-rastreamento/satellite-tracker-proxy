# Satellite Tracker Proxy

Este projeto é uma aplicação Flask que atua como um proxy para receber e processar mensagens de rastreadores de satélite. Ele recebe dados XML, decodifica o payload e extrai informações relevantes, como latitude, longitude, velocidade e status da bateria.

## Funcionalidades

*   Recebe mensagens XML de rastreadores de satélite.
*   Analisa dados XML para extrair informações relevantes.
*   Decodifica o payload para recuperar latitude, longitude, velocidade e status da bateria.
*   Registra as mensagens recebidas e os dados decodificados.
*   Envia dados para um servidor principal usando comunicação de socket.
*   Suporta formatos XML `stuMessages` e `prvmsgs`.

## Dependências

O projeto usa as seguintes dependências:

*   Flask
*   gunicorn
*   loguru
*   pydantic\_settings

Essas dependências estão listadas no arquivo `requirements.txt`.

## Configuração

A configuração do aplicativo é definida no arquivo `app/config/settings.py`. Ele usa Pydantic para carregar variáveis de ambiente de um arquivo `.env`. As seguintes configurações estão disponíveis:

*   `LOG_LEVEL`: O nível de log para o aplicativo.
*   `MAIN_SERVER_ADDRESS`: O endereço do servidor principal.

## Uso

Para executar o aplicativo, use o seguinte comando:

```bash
gunicorn main:app --workers 3 --worker-class gthread --threads 2 --timeout 600
```

Este comando inicia o servidor Gunicorn com 3 workers, cada um com 2 threads.

O aplicativo escuta solicitações POST no endpoint `/messages`. As solicitações devem conter dados XML em um dos formatos suportados (`stuMessages` ou `prvmsgs`).

## Formato da Mensagem

### stuMessages

O formato `stuMessages` é usado para enviar mensagens de dados dos rastreadores de satélite. Os dados XML devem conter os seguintes elementos:

*   `messageID`: O ID da mensagem.
*   `stuMessage`: Um contêiner para mensagens individuais.
    *   `esn`: O ESN do rastreador de satélite.
    *   `unixTime`: O timestamp Unix da mensagem.
    *   `payload`: Os dados do payload em formato hexadecimal.

### prvmsgs

O formato `prvmsgs` é usado para mensagens de provisionamento. Os dados XML devem conter os seguintes atributos:

*   `prvMessageID`: O ID da mensagem de provisionamento.

## Decodificação do Payload

O payload é decodificado usando a função `decode_payload` em `main.py`. A função extrai as seguintes informações do payload:

*   `message_type`: O tipo da mensagem.
*   `battery_status`: O status da bateria.
*   `gps_valid`: Indica se os dados do GPS são válidos.
*   `latitude`: A latitude do rastreador.
*   `longitude`: A longitude do rastreador.
*   `speed_kmh`: A velocidade do rastreador em km/h.
*   `time_modulo`: Time modulo.

## Comunicação de Socket

O aplicativo envia dados para o servidor principal usando comunicação de socket. A função `send_dict_to_server` em `app/connection/main_server_conection.py` é usada para enviar os dados. A função se conecta ao servidor usando o endereço especificado na configuração `MAIN_SERVER_ADDRESS`. Os dados são enviados em formato JSON, encapsulados com bytes `\xff` e `\xfe`.

## Logging

O aplicativo usa a biblioteca `loguru` para logging. Os logs são gravados no console e em um arquivo. O nível de log pode ser configurado usando a configuração `LOG_LEVEL`.



