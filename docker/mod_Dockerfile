# Acts as a modification to run Laura Spitler's version of single-pulse searching
# Also installs other useful software
FROM cornellcac/ipta-docker-updated

SHELL ["/bin/bash", "-c"]

USER jovyan

ENV PSRHOME=/opt/pulsar
ENV PRESTO=$PSRHOME/presto 
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PRESTO/lib 
ENV PATH=$PATH:$PRESTO/bin

WORKDIR $PSRHOME
RUN mkdir PALFA && \
    mkdir PALFA/bin
ENV PALFA=$PSRHOME/PALFA

WORKDIR $PALFA
RUN git clone https://github.com/federatedcloud/transients_pipeline2.git

WORKDIR $PRESTO/src
RUN make clean

# pull maskdata PRESTO modifications
WORKDIR /home/jovyan
RUN git clone https://github.com/federatedcloud/modulation_index.git && \
    cd modulation_index && \
    cp changes/*.h $PRESTO/include && \
    cp changes/*.c $PRESTO/src && \
    cp changes/Makefile $PRESTO/src

# rebuild PRESTO
WORKDIR $PRESTO/src
RUN make prep && \
    make

WORKDIR $PRESTO
RUN pip install .

# install modulation index
RUN cd /home/jovyan/modulation_index/mi_src && \
    gcc -Wall palfa_calc_mi.c -o palfa_mi -lm && \
    cp palfa_mi $PALFA/bin

# install blimpy
RUN pip install https://github.com/UCBerkeleySETI/blimpy/archive/1.4.1.tar.gz

# user setup
COPY bashrc /home/jovyan/.bashrc
COPY vimrc /home/jovyan/.vimrc
COPY profile /home/jovyan/.profile

USER root

RUN groupadd -g 999 docker
RUN usermod -aG docker jovyan

