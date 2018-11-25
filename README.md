# AWS Credentials Issuer

## Goals

When using AWS with federated authentication with SAML it is tricky to generate access and secret keys. The idea behind this project is to have your identity provider control AWS access via JWT claims. That is, should a users JWT contain a claim of roles which is an array of Amazon role ARNs the lambda function will execute an AssumeRole and return the credentials.

Additionally, the service generates federated sign on URLs for console access.

## Example:

Get a sign in URL:

```
curl -i https://api-gateway/dev/api/login?role=arn:aws:iam::account-id:role/role-name -H "Authorization: bearer JWT-TOKEN"
HTTP/2 301
content-type: application/json
content-length: 0
location: https://signin.aws.amazon.com/federation?Action=login&Issuer=aws-credentials-issuer&Destination=https%3A%2F%2Fconsole.aws.amazon.com&SigninToken=SIGN_IN_TOKEN
date: Sun, 25 Nov 2018 22:55:37 GMT
x-amzn-requestid: 39157c93-f105-11e8-b9c8-e97c811258c0
x-amz-apigw-id: Q8NAZEkrFiAFsig=
x-amzn-trace-id: Root=1-5bfb2868-ebb115d00468a2303cff1f30;Sampled=0
x-cache: Miss from cloudfront
via: 1.1 6e3453a91a5fc5982955003a408b061d.cloudfront.net (CloudFront)
x-amz-cf-id: zpwf0oPhNhV1PbKXzQk88iEiJGR7LPaj9jGGwoWNtioYxXQu_RFGyg==
```

Get API Credentials:

```
curl https://api-gateway/dev/api/credentials?role=arn:aws:iam::account-id:role/role-name -H "Authorization: bearer JWT"
{
    "AccessKeyId": "",
    "Expiration": "2018-11-25T23:57:04+00:00",
    "SecretAccessKey": "",
    "SessionToken": ""
}
```
