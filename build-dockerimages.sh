#!/bin/sh

ZUUL_DOCKERREPO=${ZUUL_DOCKERREPO:-"local"}
ZUUL_VERSION=${ZUUL_VERSION:-"2.6.1"}

docker build --target zuul -t ${ZUUL_DOCKERREPO}/zuul:${ZUUL_VERSION} .
docker build --target zuul-executor -t ${ZUUL_DOCKERREPO}/zuul-executor:${ZUUL_VERSION} .
docker build --target zuul-fingergw -t ${ZUUL_DOCKERREPO}/zuul-fingergw:${ZUUL_VERSION} .
docker build --target zuul-merger -t ${ZUUL_DOCKERREPO}/zuul-merger:${ZUUL_VERSION} .
docker build --target zuul-scheduler -t ${ZUUL_DOCKERREPO}/zuul-scheduler:${ZUUL_VERSION} .
docker build --target zuul-web -t ${ZUUL_DOCKERREPO}/zuul-web:${ZUUL_VERSION} .