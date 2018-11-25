import boto3
import datetime
import json
import jwt
import os
import urllib
import requests
import struct
from arnparse import arnparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from jwt.exceptions import InvalidKeyError
from jwt.utils import base64url_decode

CLIENT_ID = os.getenv('CLIENT_ID')
CERTS_URL = os.getenv('CERTS_URL')

json.JSONEncoder.default = lambda self, obj: (
    obj.isoformat() if isinstance(obj, datetime.datetime) else None)


def jwt_verify(auth_token):
    header_segment = auth_token.split('.')[0]
    header = json.loads(base64url_decode(header_segment).decode('utf-8'))
    kid = header['kid']
    key = load_keystore(CERTS_URL)[kid]
    payload = jwt.decode(auth_token, key=key, verify=True, audience=CLIENT_ID)
    return payload


def load_keystore(jwks_uri):
    resp = requests.get(url=jwks_uri)
    keystore = resp.json()["keys"]
    ret = {}
    for key in keystore:
        kid = key['kid']
        ret[kid] = from_jwk(key)
    return ret


def from_jwk(obj):
    if obj.get('kty') != 'RSA':
        raise InvalidKeyError('Not an RSA key')

    # Public key
    numbers = RSAPublicNumbers(
        from_base64url_uint(obj['e']), from_base64url_uint(obj['n'])
    )

    return numbers.public_key(default_backend())


def from_base64url_uint(val):
    if isinstance(val, str):
        val = val.encode('ascii')

    data = base64url_decode(val)

    buf = struct.unpack('%sB' % len(data), data)
    return int(''.join(["%02x" % byte for byte in buf]), 16)


def console_login(event, context):
    credentials = json.loads(generate_credentials(event, context)['body'])
    json_string_with_temp_credentials = json.dumps({
        "sessionId":  credentials['AccessKeyId'],
        "sessionKey": credentials['SecretAccessKey'],
        "sessionToken": credentials['SessionToken']
    })
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&Session=" + \
        urllib.parse.quote_plus(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    r = requests.get(request_url)
    signin_token = json.loads(r.text)

    request_parameters = "?Action=login"
    request_parameters += "&Issuer=" + CLIENT_ID
    request_parameters += "&Destination=" + \
        urllib.parse.quote_plus("https://console.aws.amazon.com")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    return {
        'statusCode': 301,
        'headers': {
            'location': request_url
        }
    }


def generate_credentials(event, context):
    if 'headers' not in event or 'Authorization' not in event['headers']:
        return create_aws_lambda_response(400, {'error_message': 'No authorization header found.'})

    whole_auth_token = event['headers']['Authorization']
    token_parts = whole_auth_token.split(' ')
    auth_token = token_parts[1]
    token_method = token_parts[0]

    if not (token_method.lower() == 'bearer' and auth_token):
        return create_aws_lambda_response(400, {'error message': 'Invalid authorization token'})

    if 'queryStringParameters' not in event or 'role' not in event['queryStringParameters']:
        return create_aws_lambda_response(400, {
            'error_message': 'You must provide a role arn via the query parameter \'role\''})

    requested_role_raw_arn = event['queryStringParameters']['role']

    try:
        arnparse(requested_role_raw_arn)
    except:
        return create_aws_lambda_response(400, {'error_message': 'invalid role arn'})

    try:
        claims = jwt_verify(auth_token)

        if 'roles' not in claims or requested_role_raw_arn not in claims['roles']:
            return create_aws_lambda_response(403, {'error_message': 'role not allowed'})

        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            RoleArn=requested_role_raw_arn,
            RoleSessionName=claims['preferred_username']
        )
        credentials = assumed_role_object['Credentials']
        return create_aws_lambda_response(200, credentials)
    except Exception as e:
        return create_aws_lambda_response(500, {'error_message': str(e)})


def create_aws_lambda_response(status_code, message,
                               headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': True}):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(message, indent=4, sort_keys=True)
    }
