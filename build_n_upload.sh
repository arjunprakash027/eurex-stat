#!/usr/bin/env bash

IMG=arjunrao123/eurex-stat
VER=$(tr -d '[:space:]' < VERSION.txt)

docker build -t ${IMG}:${VER} .
docker tag  ${IMG}:${VER} ${IMG}:latest
docker push ${IMG}:${VER}
docker push ${IMG}:latest
echo "Pushed ${IMG}:{${VER},latest}"
