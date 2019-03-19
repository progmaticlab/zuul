FROM ubuntu:xenial as zuul

RUN echo "deb http://ppa.launchpad.net/openstack-ci-core/bubblewrap/ubuntu xenial main" >> /etc/apt/sources.list \
  && apt-get update \
  && apt-get -y install curl python3.5 python3-setuptools ca-certificates git build-essential zookeeperd libssl-dev libffi-dev libxml2-dev libxslt-dev python3-dev python python-setuptools python-dev \
  && apt-get -y --allow-unauthenticated install bubblewrap \
  && easy_install pip \
  && easy_install3 pip \
  && pip3 install lxml

# py2-requirements.txt and py3-requirements.txt contains packages required by Tungsten Fabric CI
RUN cd /tmp \
  && git clone https://github.com/progmaticlab/zuul.git -b contrail/feature/zuulv3 \
  && cd zuul \
  && pip2 install -r py2-requirements.txt \
  && pip3 install . \
  && pip3 install -r py3-requirements.txt \
  && mkdir -p /var/log/zuul \
  && rm -rf /tmp/zuul \
  && adduser --disabled-password --gecos GECOS zuul

VOLUME /var/lib/zuul
CMD ["/usr/local/bin/zuul"]

FROM zuul as zuul-executor
CMD ["/usr/local/bin/zuul-executor"]

FROM zuul as zuul-fingergw
CMD ["/usr/local/bin/zuul-fingergw"]

FROM zuul as zuul-merger
CMD ["/usr/local/bin/zuul-merger"]

FROM zuul as zuul-scheduler
CMD ["/usr/local/bin/zuul-scheduler"]

FROM zuul as zuul-web
CMD ["/usr/local/bin/zuul-web"]

