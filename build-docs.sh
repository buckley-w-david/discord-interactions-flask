#!/usr/bin/bash

GIT_SHA=$(git rev-parse --short HEAD)
DOCS=${1:-$PWD/docs/build/html}

podman build . -t "discord-interactions-flask:${GIT_SHA}"
podman run --rm --mount type=bind,source=$DOCS,target=/repo/docs/build/html "discord-interactions-flask:${GIT_SHA}"
