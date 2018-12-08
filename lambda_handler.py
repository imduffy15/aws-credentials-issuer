import boto3
import datetime
import json
import os
import urllib
import requests
from arnparse import arnparse
from jose import jwt

CLIENT_ID = os.getenv('CLIENT_ID')

json.JSONEncoder.default = lambda self, obj: (
    obj.isoformat() if isinstance(obj, datetime.datetime) else None)


def jwt_verify(token):
    jwksPath = os.environ['LAMBDA_TASK_ROOT'] + "/jwks.json"
    jwks = json.loads(open(jwksPath).read())

    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = key
            break

    return jwt.decode(
        token,
        rsa_key,
        algorithms=unverified_header["alg"],
        audience=CLIENT_ID
    )


def console_login(event, context):
    credentials_resp = generate_credentials(event, context)
    credentials = json.loads(credentials_resp['body'])

    if not all(k in credentials for k in ("AccessKeyId", "SecretAccessKey", "SessionToken")):
        return credentials_resp

    json_string_with_temp_credentials = json.dumps({
        "sessionId": credentials['AccessKeyId'],
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

    return create_aws_lambda_response(200, {'url': request_url})


def generate_credentials(event, context):
    if 'headers' not in event or 'Authorization' not in event['headers']:
        return create_aws_lambda_response(
            400, {'error_message': 'No authorization header found.'})

    whole_auth_token = event['headers']['Authorization']
    token_parts = whole_auth_token.split(' ')
    auth_token = token_parts[1]
    token_method = token_parts[0]

    if not (token_method.lower() == 'bearer' and auth_token):
        return create_aws_lambda_response(
            400, {'error message': 'Invalid authorization token'})

    print(json.dumps(event))

    if 'queryStringParameters' not in event or event[
            'queryStringParameters'] is None or 'role' not in event['queryStringParameters']:
        return create_aws_lambda_response(400, {
            'error_message': 'You must provide a role arn via the query parameter \'role\''})

    requested_role_raw_arn = event['queryStringParameters']['role']

    try:
        arnparse(requested_role_raw_arn)
    except BaseException:
        return create_aws_lambda_response(
            400, {'error_message': 'invalid role arn'})

    try:
        claims = jwt_verify(auth_token)

        if 'roles' not in claims or requested_role_raw_arn not in claims['roles']:
            return create_aws_lambda_response(
                403, {'error_message': 'role not allowed'})

        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            RoleArn=requested_role_raw_arn,
            RoleSessionName=claims['preferred_username']
        )
        credentials = assumed_role_object['Credentials']
        return create_aws_lambda_response(200, credentials)
    except Exception as e:
        return create_aws_lambda_response(500, {'error_message': str(e)})


def create_aws_lambda_response(
    status_code,
    message,
    headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True}):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(message, indent=4, sort_keys=True)
    }
