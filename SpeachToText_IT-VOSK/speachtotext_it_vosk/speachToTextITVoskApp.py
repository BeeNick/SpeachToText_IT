'''
Italian speach to text application usign Vosk model.
Please read REDME.md and LICENSE.md files.

The application is designed for local use, it makes use of https
as required by most browsers to allow access to audio data.

The logging details are defined in logger.yml, but the most 
iportant info is anyway logged in the terminal.
'''
from flask import Flask, render_template, request, jsonify
from vosk import Model, KaldiRecognizer
import json
import ssl
import os
from beans_logging.auto import logger

app = Flask(__name__)

BEANS_LOGGING_CONFIG_PATH="./configs/logger.yml"

SPEACH_TEXT_CONFIG_PATH="./configs/speachToText_it_config.yml"

# Initialize Vosk model
logger.info(f"Vosk model: {e} - loading")
try:
    model = Model("vosk-model-small-it-0.22")
    recognizer = KaldiRecognizer(model, 16000)
    logger.info(f"Vosk model: {e} - loaded")
except Exception as e:
    logger.error(f"Error loading Vosk model: {e}")
    print(f"Error loading Vosk model: {e}")
    print("Please download the model from https://alphacephei.com/vosk/models")
    exit(1)

@app.route('/')
def index():
    logger.info(f"Rendering index page")
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    logger.info(f"Transcribe function - check request for audio data")
    logger.trace(f"Request {request}")
    if 'audio' not in request.files:
        logger.error("No audio file provided")
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    # Convert the audio data to the format Vosk expects
    logger.info(f"Transcribe function - converting audio for Vosk model")
    #TODO check correct webm - codec opus reading
    #TODO write audio file using CONFIG path   
    audio_data = audio_file.read()
    logger.trace("Start audio file")
    logger.trace(f"{audio_data}")
    logger.trace("End audio file")
    
    # Process the audio with Vosk
    logger.info(f"Transcribe function - processing audio with Vosk model")
    if recognizer.AcceptWaveform(audio_data):
        logger.info(f"Transcribe function - audio processed - generating response")
        result = json.loads(recognizer.Result())
        #TODO write transcirbed text file using CONFIG path   
        logger.trace(f"Transcription result: {result}")
        return jsonify({'text': result.get('text', '')})
    
    return jsonify({'text': ''})

def generate_self_signed_cert():
    """Generate self-signed certificate for HTTPS"""
    from OpenSSL import crypto
    
    logger.info(f"HTTPS function - key generation")
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    logger.info(f"HTTPS function - certificate generation")
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Write certificate and private key to files
    logger.info(f"HTTPS function - certificate writing")
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

if __name__ == '__main__':
    # Check if certificate exists, if not generate it
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        try:
            generate_self_signed_cert()
            print("Generated self-signed certificate")
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            print(f"Error generating certificate: {e}")
            logger.info("Installing pyOpenSSL...")
            print("Installing pyOpenSSL...")
            os.system("poetry add pyOpenSSL")
            logger.info("Retrying certificate generation...")
            print("Retrying certificate generation...")
            generate_self_signed_cert()
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    # Run the app on all network interfaces with HTTPS
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)