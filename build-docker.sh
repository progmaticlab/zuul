#!/bin/sh
set -e

ZUUL_DOCKERREPO=${ZUUL_DOCKERREPO:-"local"}
ZUUL_VERSION=${ZUUL_VERSION:-"2.5.3"}

if [[ "$ZUUL_CLEAN" == "1" ]]; then
    docker image rm ${ZUUL_DOCKERREPO}/zuul:${ZUUL_VERSION}
    docker image rm ${ZUUL_DOCKERREPO}/zuul-executor:${ZUUL_VERSION}
    docker image rm ${ZUUL_DOCKERREPO}/zuul-fingergw:${ZUUL_VERSION}
    docker image rm ${ZUUL_DOCKERREPO}/zuul-merger:${ZUUL_VERSION}
    docker image rm ${ZUUL_DOCKERREPO}/zuul-scheduler:${ZUUL_VERSION}
    docker image rm ${ZUUL_DOCKERREPO}/zuul-web:${ZUUL_VERSION}
fi

docker build --target zuul -t ${ZUUL_DOCKERREPO}/zuul:${ZUUL_VERSION} .
docker build --target zuul-executor -t ${ZUUL_DOCKERREPO}/zuul-executor:${ZUUL_VERSION} .
docker build --target zuul-fingergw -t ${ZUUL_DOCKERREPO}/zuul-fingergw:${ZUUL_VERSION} .
docker build --target zuul-merger -t ${ZUUL_DOCKERREPO}/zuul-merger:${ZUUL_VERSION} .
docker build --target zuul-scheduler -t ${ZUUL_DOCKERREPO}/zuul-scheduler:${ZUUL_VERSION} .
docker build --target zuul-web -t ${ZUUL_DOCKERREPO}/zuul-web:${ZUUL_VERSION} .

if [[ "$ZUUL_PUSH" == "1" ]]; then
    docker push ${ZUUL_DOCKERREPO}/zuul:${ZUUL_VERSION}
    docker push ${ZUUL_DOCKERREPO}/zuul-executor:${ZUUL_VERSION}
    docker push ${ZUUL_DOCKERREPO}/zuul-fingergw:${ZUUL_VERSION}
    docker push ${ZUUL_DOCKERREPO}/zuul-merger:${ZUUL_VERSION}
    docker push ${ZUUL_DOCKERREPO}/zuul-scheduler:${ZUUL_VERSION}
    docker push ${ZUUL_DOCKERREPO}/zuul-web:${ZUUL_VERSION}
fi