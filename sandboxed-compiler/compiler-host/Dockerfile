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

# Copy over the actual server code
ADD "server.py" "/server.py"

CMD ["gunicorn", "-w", "4", "-b", "127.0.0.1:6666", "--access-logfile=-", "--error-logfile=-", "--timeout", "600",  "server:app"]
