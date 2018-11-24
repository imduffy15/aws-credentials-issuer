# AWS Credentials Issuer

This project is currently a work in progress

## Goals

When using AWS with federated authentication with SAML it is tricky to generate access and secret keys. The idea behind this project is to have your identity provider control AWS access via JWT claims. That is, should a users JWT contain a claim of roles which is an array of Amazon role ARNs the lambda function will execute an AssumeRole and return the credentials.

Additionally, the service will generate federated sign on URLs for console access.
