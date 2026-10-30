# Container for running the compiler host which will process compile calls by launching a new container which in return will run the actual compiler.
FROM ubuntu:jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt -y update && apt -y upgrade
RUN apt -y install \
  wget \
  htop \
  vim \
  pv \
  curl \
  rsync \
  netcat \
  telnet \
  qperf \
  traceroute \
  python3-flask \
  gunicorn \
  podman

RUN date > /builddate

ADD "server.py" "/server.py"

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6666", "--access-logfile=-", "--error-logfile=-", "--timeout", "600",  "server:app"]
