# Local development deployment

- The provided `makefile` in the project root directory can be used to build local container images and boot up a local deployment; simply run `make` without any target
  - `docker-compose.local.yml` is used to build the local images
- For the Nextcloud application to work properly, you have to use the local IP address of your machine, not `localhost`, e.g. `http://1.2.3.4:8099`
  - Overleaf runs on port `8099` for local setups

