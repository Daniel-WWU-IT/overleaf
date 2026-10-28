FROM ubuntu:plucky

RUN \
  groupmod -g 1001 www-data; \
  usermod -u 1001 www-data; \
  groupmod -g 33 ubuntu; \
  usermod -u 33 ubuntu

RUN apt-get update \
&&  apt-get install -y \
  texlive-full \
  python3-pygments \
  libsynctex2 \
  latexmk \
  inkscape
