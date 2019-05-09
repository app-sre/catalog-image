FROM centos:7

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

RUN yum install -y epel-release && \
    yum install -y python2-pip PyYAML git && \
    pip install --upgrade pip setuptools && \
    yum clean all

COPY setup.py /catalog-image/setup.py
COPY catalog_image/ /catalog-image/catalog_image/

WORKDIR /catalog-image

RUN python setup.py install
