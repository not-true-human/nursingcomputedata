from pyngrok import ngrok
import os
import time

# If you have an NGROK_AUTHTOKEN set in environment, this will use it.
token = os.getenv("NGROK_AUTHTOKEN")
if token:
    try:
        ngrok.set_auth_token(token)
    except Exception:
        pass

# Open a public tunnel to the running Streamlit server (port 8501)
tunnel = ngrok.connect(8501, bind_tls=True)
print("ngrok tunnel public URL:", tunnel.public_url)
print("Press Ctrl+C to stop the tunnel")
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    ngrok.disconnect(tunnel.public_url)
    ngrok.kill()
    print("ngrok tunnel closed")
