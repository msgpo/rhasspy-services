FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y \
        pulseaudio \
        gstreamer1.0-pulseaudio \
        gstreamer1.0-tools \
        gstreamer1.0-plugins-good

# Create new user
ENV UNAME=rhasspy
RUN export UNAME=$UNAME UID=1000 GID=1000 && \
    mkdir -p "/home/${UNAME}" && \
    echo "${UNAME}:x:${UID}:${GID}:${UNAME} User,,,:/home/${UNAME}:/bin/bash" >> /etc/passwd && \
    echo "${UNAME}:x:${UID}:" >> /etc/group && \
    mkdir -p /etc/sudoers.d && \
    echo "${UNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${UNAME} && \
    chmod 0440 /etc/sudoers.d/${UNAME} && \
    gpasswd -a ${UNAME} audio

COPY docker/pulseaudio.client.conf /etc/pulse/client.conf

# Copy script to run
COPY docker/run.sh /home/${UNAME}/run.sh

# Create cookie dir
RUN mkdir -p /home/${UNAME}/.config/pulse

# Own everything
RUN export UNAME=$UNAME UID=1000 GID=1000 && \
    chown ${UID}:${GID} -R /home/${UNAME}

# Switch to new user
USER $UNAME
ENV HOME /home/${UNAME}

WORKDIR /home/${UNAME}
ENTRYPOINT ["bash", "run.sh"]