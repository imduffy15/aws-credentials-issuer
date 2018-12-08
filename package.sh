#!/usr/bin/env bash

echo "Downloading jwks"
wget -q -nv -O jwks.json http://localhost:8080/auth/realms/example-realm/protocol/openid-connect/certs >/dev/null 2>/dev/null
