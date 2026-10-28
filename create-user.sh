#!/bin/bash
set -eu
cd "$(dirname "$0")"

set -a
. ./.env
set +a

mkdir -p auth
htpasswd -Bbn "$REGISTRY_USER" "$REGISTRY_PASSWORD" > auth/htpasswd
chmod 600 auth/htpasswd
echo "Пользователь $REGISTRY_USER записан в auth/htpasswd"