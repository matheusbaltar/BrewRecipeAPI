#!/bin/sh
# O comando acima avisa o sistema que isso é um script shell (sh).
# Usamos sh e não bash porque a imagem python:3.12-slim garante o sh,
# mas não necessariamente o bash. O Dockerfile também chama com "sh entrypoint.sh".

set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Iniciando o servidor Python..."
exec "$@"
