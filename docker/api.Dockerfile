
FROM python:3.12.2-bullseye

SHELL ["/bin/bash", "-c"] 

RUN curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" bash

RUN echo 'source "$HOME/.rye/env"' >> ~/.profile
RUN echo 'source "$HOME/.rye/env"' >> ~/.bashrc

COPY notipy/ /opt/notipy/

WORKDIR /opt/notipy

RUN source "$HOME/.rye/env" && rye sync -f 

CMD ["bash", "start.sh"]
