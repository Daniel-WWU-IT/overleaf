# ---------------------------------------------
# Overleaf Community Edition (overleaf/overleaf)
# ---------------------------------------------

# ARG SHARELATEX_BASE_TAG=sharelatex/sharelatex-base:2.7.0
# Use a custom base image which provides the "full" Texlive distribution
ARG SHARELATEX_BASE_TAG=omnivox/overleaf-base:latest
FROM $SHARELATEX_BASE_TAG

# Install pip and some Python modules
# -----------------------------------
RUN apt-get update \
&&  apt-get install -y python3-pip \
&&  python3 -m pip install Flask requests cryptography beautifulsoup4 lxml gunicorn

WORKDIR /var/www/sharelatex

# Add required source files
# -------------------------
ADD ${baseDir}/genScript.js /var/www/sharelatex/genScript.js
ADD ${baseDir}/services.js /var/www/sharelatex/services.js

# Checkout services
# -----------------
RUN node genScript checkout | bash \
  \
# Store the revision for each service
# ---------------------------------------------
&&  node genScript revisions | bash > /var/www/revisions.txt \
  \
# Cleanup the git history
# -------------------
&&  node genScript cleanup-git | bash

# Install npm dependencies
# ------------------------
RUN node genScript install | bash

# Compile
# --------------------
RUN node genScript compile | bash

# Links CLSI synctex to its default location
# ------------------------------------------
RUN ln -s /var/www/sharelatex/clsi/bin/synctex /opt/synctex


# Copy runit service startup scripts to its location
# --------------------------------------------------
ADD ${baseDir}/runit /etc/service


# Configure nginx
# ---------------
ADD ${baseDir}/nginx/nginx.conf.template /etc/nginx/templates/nginx.conf.template
ADD ${baseDir}/nginx/sharelatex.conf /etc/nginx/sites-enabled/sharelatex.conf


# Configure log rotation
# ----------------------
ADD ${baseDir}/logrotate/sharelatex /etc/logrotate.d/sharelatex
RUN chmod 644 /etc/logrotate.d/sharelatex


# Copy Phusion Image startup scripts to its location
# --------------------------------------------------
COPY ${baseDir}/init_scripts/ /etc/my_init.d/

# Copy app settings files
# -----------------------
COPY ${baseDir}/settings.js /etc/sharelatex/settings.js

# Copy grunt thin wrapper
# -----------------------
ADD ${baseDir}/bin/grunt /usr/local/bin/grunt
RUN chmod +x /usr/local/bin/grunt

# Add missing TeX packages
# ------------------------
# tlmgr install <package>

# Copy reverse proxy scripts and stylesheets
COPY ${baseDir}/runit/reverse-proxy/*.js /var/www/sharelatex/web/public/js
COPY ${baseDir}/runit/reverse-proxy/*.css /var/www/sharelatex/web/public/stylesheets

# Set Environment Variables
# --------------------------------
ENV SHARELATEX_CONFIG /etc/sharelatex/settings.js
ENV WEB_API_USER "sharelatex"
ENV SHARELATEX_APP_NAME "Overleaf Community Edition"
ENV OPTIMISE_PDF "true"

EXPOSE 80

WORKDIR /

ENTRYPOINT ["/sbin/my_init"]