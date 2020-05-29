#FROM jupyter/datascience-notebook:82b978b3ceeb
FROM python:3.6-buster

SHELL ["/bin/bash", "-c"]

USER root

RUN sed -i "s#deb http://deb.debian.org/debian buster main#deb http://deb.debian.org/debian buster main contrib non-free#g" /etc/apt/sources.list
RUN apt-get update -y && apt-get install -y \
    sudo \
    cmake \
    liblapack-dev \
    libblas-dev \
    libopenmpi-dev \
    autoconf \
    libtool \
    pgplot5 \
    libfftw3-bin \
    libfftw3-dev \
    libfftw3-double3 \
    libfftw3-long3 \
    libfftw3-quad3 \
    libfftw3-single3 \
    libcfitsio-dev \ 
    libglib2.0-dev \
    libx11-dev \ 
    swig \
    pkg-config \ 
    openssh-client \
    openssh-server \ 
    libhealpix-cxx-dev \
    libchealpix-dev \ 
    libreadline-dev \ 
    imagemagick \
    latex2html \ 
    gv \
    tcsh \
    libsuitesparse-dev \
    rsync \ 
    dvipng \
    libgsl-dev \
    libmagickwand-dev \
    man \
    bash-completion \
    nano \ 
    vim \ 
    less \
    gnuplot \
    htop \
    tmux 

#    libfftw3-dbg \
#    libhealpix-cxx0v5 \
#    libeigen2-dev \ 

# set up user
RUN useradd -mr -G sudo dev 
RUN passwd -d dev
RUN echo "dev  ALL=(ALL)       NOPASSWD: ALL"  >> /etc/sudoers
RUN chown -R dev /home/dev

WORKDIR /home/dev

RUN mkdir /opt/pulsar
RUN chown -R dev /opt/pulsar
ENV PATH=$PATH:/home/dev/.local/bin

USER dev

# Environment setup
ENV PGPLOT_DIR=/usr/lib/pgplot5 
ENV PGPLOT_FONT=/usr/lib/pgplot5/grfont.dat 
ENV PGPLOT_INCLUDES=/usr/include 
ENV PGPLOT_BACKGROUND=white 
ENV PGPLOT_FOREGROUND=black 
ENV PGPLOT_DEV=/xs
ENV PSRHOME=/opt/pulsar

### install tempo 
ENV TEMPO=$PSRHOME/tempo 
ENV PATH=$PATH:$PSRHOME/tempo/bin

RUN git clone git://git.code.sf.net/p/tempo/tempo
RUN mv tempo $PSRHOME

WORKDIR ${TEMPO}
RUN ./prepare && \
    ./configure --prefix=$PSRHOME/tempo && \
    make && \
    make install && \
    cd util/print_resid && \
    make

COPY requirements.txt /var/tmp/requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install numpy
RUN pip install -r /var/tmp/requirements.txt

### install PRESTO
ENV PRESTO=$PSRHOME/presto 
ENV PATH=$PATH:$PRESTO/bin 
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PRESTO/lib 

RUN git clone https://github.com/scottransom/presto.git
RUN mv presto $PRESTO

# pull maskdata PRESTO modifications
WORKDIR /home/dev
RUN git clone https://github.com/federatedcloud/modulation_index.git && \
    cd modulation_index && \
    cp changes/*.h $PRESTO/include && \
    cp changes/*.c $PRESTO/src && \
    cp changes/Makefile $PRESTO/src

WORKDIR $PRESTO/src
RUN make prep && \
    make
WORKDIR $PRESTO
RUN pip install --upgrade pip && \
    pip install .
#TESTING
RUN python tests/test_presto_python.py
###

# install PALFA pipeline
WORKDIR $PSRHOME
RUN mkdir PALFA && \
    mkdir PALFA/bin
ENV PALFA=$PSRHOME/PALFA

WORKDIR $PALFA
RUN git clone https://github.com/federatedcloud/transients_pipeline2.git

# install modulation index
RUN cd /home/dev/modulation_index/mi_src && \
    gcc -Wall palfa_calc_mi.c -o palfa_mi -lm && \
    cp palfa_mi $PALFA/bin

# install blimpy
RUN pip install https://github.com/UCBerkeleySETI/blimpy/archive/1.4.1.tar.gz

# user setup
COPY bashrc /home/dev/.bashrc
COPY vimrc /home/dev/.vimrc
COPY profile /home/dev/.profile

USER root
RUN git clone https://github.com/scottransom/psrfits_utils.git && \
    cd psrfits_utils && \
    ./prepare && \
    ./configure && \
    make && make install

RUN apt-get clean
RUN systemctl enable ssh
RUN mkdir /var/run/sshd
RUN sed 's/X11Forwarding yes/X11Forwarding yes\nX11UseLocalhost no/' -i /etc/ssh/sshd_config
RUN git clone https://github.com/demorest/tempo_utils.git && \
    cd tempo_utils && \
    python setup.py install

ENV PATH=/opt/pulsar/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/pulsar/lib:$LD_LIBRARY_PATH

RUN chown -R dev /home/dev
#ENV GRANT_SUDO=1

#RUN groupadd -g 999 docker
#RUN usermod -aG docker dev

USER dev
WORKDIR /home/dev

