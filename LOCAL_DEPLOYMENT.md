# Local development deployment
This is a guide on how to run a local deployment of Overleaf integrated into a Nextcloud instance.

## Prerequisites
Unfortunately, running a local instance of Overleaf+Nextcloud Integration is no easy feat, mainly due to browser security restrictions. There are a few steps that must be taken on the local system before being able to run the provided setup:

1. Add local domains
  Edit `/etc/hosts` and add the following two entries:
    ```
    127.0.0.1 nextcloud.dev.local
    127.0.0.1 overleaf.nextcloud.dev.local
    ```
2. Install **mkcert** and execute the following:
    ```
    mkcert -install
   
   mkcert \
    -cert-file local.crt \
    -key-file local.key \
    nextcloud.dev.local overleaf.nextcloud.dev.local
   ```
3. Copy the generated two files into `local/certs`.

These steps will allow you to use the two local domains to work over *https*, which is necessary for Overleaf to work properly.

Next, a few setup steps for Nextcloud need to be done:

1. Start the local deployment by simply running `make` in the main project directory. Ignore any errors.
2. Once the Nextcloud container has started, go to `https://nextcloud.dev.local` and follow the on-screen instructions (use `admin/admin` to log in).
3. Enter the running Nextcloud container:
    ```
   docker exec -it nextcloud bash
   ```
4. Change ownership of `custom_apps`:
   ```
   chown -R www-data:www-data custom_apps
   ```
5. Restart the deployment.

All these steps only need to be done once. **Note**: The Nextcloud setup needs to be redone if you delete the `nextcloud` Docker volume.

## Running a local deployment

The provided `makefile` in the project root directory can be used to build local container images and boot up a local deployment; simply run `make` without any target. This will also start a Nextcloud instance, which runs on `https://nextcloud.dev.local`. The default administrator login is `admin/admin`.
