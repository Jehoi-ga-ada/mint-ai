#!/bin/sh
set -e

DOMAIN=mintai.eastasia.cloudapp.azure.com
EMAIL=${1:-}

if [ -n "$EMAIL" ]; then
  REG="-m $EMAIL --no-eff-email"
else
  REG="--register-unsafely-without-email"
fi

docker compose run --rm -p 80:80 --entrypoint "" certbot \
  certbot certonly --standalone -d "$DOMAIN" --agree-tos $REG

docker compose up -d
