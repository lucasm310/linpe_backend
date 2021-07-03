import json
import time
import urllib.request
from os import environ

from jose import jwk, jwt
from jose.utils import base64url_decode
from dotenv import load_dotenv

load_dotenv()

region = environ.get("AWS_REGION")
userpool_id = environ.get("USERPOOL_ID")
app_client_id = environ.get("CLIENT_ID")
keys_url = f'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'

with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def decodeJWT(token):
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        return False
    public_key = jwk.construct(keys[key_index])
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        return False
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims['exp']:
        return False
    if claims['client_id'] != app_client_id:
        return False
    return claims

