#!/bin/bash -e

# $1 - name of component to build. all components will be built if not present

ZUUL_DOCKERREPO=${ZUUL_DOCKERREPO:-"local"}
ZUUL_VERSION=${ZUUL_VERSION:-"2.5.3"}

function build() {
  local name=$1
  if [[ "$ZUUL_CLEAN" == "1" ]]; then
    docker image rm ${ZUUL_DOCKERREPO}/zuul-$name:${ZUUL_VERSION} || /bin/true
  fi
  docker build --target zuul-$name -t ${ZUUL_DOCKERREPO}/zuul-$name:${ZUUL_VERSION} .
  if [[ "$ZUUL_PUSH" == "1" ]]; then
    docker push ${ZUUL_DOCKERREPO}/zuul-$name:${ZUUL_VERSION}
  fi    
}

if [[ -n "$1" ]]; then
  build $1
else
  build executor
  build fingergw
  build merger
  build scheduler
  build web
fi
