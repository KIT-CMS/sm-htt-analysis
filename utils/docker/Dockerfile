FROM cern/slc6-base:20170301

USER root
ENV USER root
ENV HOME /root
ENV VO_CMS_SW_DIR       /cvmfs/cms.cern.ch
ENV CMS_LOCAL_ROOT_BASE /cvmfs/cms.cern.ch

RUN yum install -y yum-plugin-ovl && yum clean all
RUN yum update -y && yum clean all
RUN yum -y install \
    which \
    time \
    tar \ 
    perl \
    gcc \
    freetype \
    glibc-headers \
    glibc-devel \
    subversion \
    make \ 
    gcc \
    gcc-c++ \
    binutils \
    patch \ 
    wget \
    python \
    libxml2-devel \
    libX11-devel \
    libXpm-devel \
    libXft-devel \
    libXext-devel \
    bzip2-devel \
    openssl-devel \
    ncurses-dev-el \
    readline-devel \
    mesa-libGL-devel \
    libgfortran.x86_64 \
    glew-devel \
    git \
    krb5-workstation \
    gsl \
    libtool-ltdl \
    lcg-util.x86_64 \
    bc \
    tcsh \
    atlas \
    libpng-devel \
    libjpeg-turbo \
    ; \
    yum clean all

RUN git config --global user.email "alias@example.com"
RUN git config --global user.name "alias"

# set timezone to cet
RUN ln -sf /usr/share/zoneinfo/CET /etc/localtime

WORKDIR /root

## make the whole container seamlessly executable
CMD bash
