#!/bin/bash -e

# $1 - name of component to build. all components will be built if not present

ZUUL_DOCKERREPO=${ZUUL_DOCKERREPO:-"local"}
ZUUL_VERSION=${ZUUL_VERSION:-"2.6.1"}

docker build --target zuul -t ${ZUUL_DOCKERREPO}/zuul:${ZUUL_VERSION} .
if [[ -n "$1" ]]; then
  docker build --target zuul-$1 -t ${ZUUL_DOCKERREPO}/zuul-$1:${ZUUL_VERSION} .
else
  docker build --target zuul-executor -t ${ZUUL_DOCKERREPO}/zuul-executor:${ZUUL_VERSION} .
  docker build --target zuul-fingergw -t ${ZUUL_DOCKERREPO}/zuul-fingergw:${ZUUL_VERSION} .
  docker build --target zuul-merger -t ${ZUUL_DOCKERREPO}/zuul-merger:${ZUUL_VERSION} .
  docker build --target zuul-scheduler -t ${ZUUL_DOCKERREPO}/zuul-scheduler:${ZUUL_VERSION} .
  docker build --target zuul-web -t ${ZUUL_DOCKERREPO}/zuul-web:${ZUUL_VERSION} .
fi