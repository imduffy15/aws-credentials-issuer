import json
import os

import jwt

def auth(event, context):
    whole_auth_token = event['headers']['Authorization']
    if not whole_auth_token:
        print(f'Token not found: {event}')
        raise Exception('Unauthorized')

    token_parts = whole_auth_token.split(' ')
    auth_token = token_parts[1]
    token_method = token_parts[0]

    if not (token_method.lower() == 'bearer' and auth_token):
        print("Failing due to invalid token_method or missing auth_token")
        raise Exception('Unauthorized')

    try:
        claims = jwt_verify(auth_token, '')
        policy = generate_policy(claims['sub'], 'Allow', event['methodArn'])
        return policy
    except Exception as e:
        print(f'Exception encountered: {e}')
        raise Exception('Unauthorized')

def jwt_verify(auth_token, public_key):
    payload = jwt.decode(auth_token, verify=False)
    return payload

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource

                }
            ]
        }
    }

def generate_credentials(event, context):
    return create_200_response('Hi ⊂◉‿◉つ from Private API. Only logged in users can see this')

def create_200_response(message):
    headers = {
        # Required for CORS support to work
        'Access-Control-Allow-Origin': '*',
        # Required for cookies, authorization headers with HTTPS
        'Access-Control-Allow-Credentials': True,
    }
    return create_aws_lambda_response(200, {'message': message}, headers)

def create_aws_lambda_response(status_code, message, headers):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(message)
    }
