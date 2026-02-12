# Overleaf Nextcloud Integration - v2.0.0

## Changes applied to Overleaf
- Build custom base image to use the full Texlive distribution by applying the following changes to `server-ce/Dockerfile-base`:
    - Set `selected_scheme` to `scheme-full` (located within the TexLive installation block)
    - Update TexLive by adding this directly after the TexLive installation block:
      ```
      RUN tlmgr update --self \
      &&  tlmgr update --all
      ```
- Modifications to the main Docker file `server-ce/Dockerfile`:
    - Use the custom base image by modifying ARG `OVERLEAF_BASE_TAG` accordingly
    - Install additional Python modules by adding this directly above the `WORKDIR` directive:
        ```
        RUN apt-get update \
        &&  apt-get install -y python3-flask python3-requests python3-cryptography python3-bs4 python3-lxml python3-gunicorn
        ```
    - **MIGHT REMOVE/CHANGE** Add some web files by adding the following below the `Copy grunt thin wrapper` block:
        ```
        COPY server-ce/runit/reverse-proxy/*.js /overleaf/services/web/public/js/
        COPY server-ce/runit/reverse-proxy/*.css /overleaf/services/web/public/stylesheets/
        ```
    - To add additional Tex packages, you can use the following command:
        ```
        RUN tlmgr install <package>
        ```
- Add `server-ce/runit/remote-api-server` and `server-ce/runit/reverse-proxy`
    - Make sure that the `run` files have the executable flag set
- Modify `server-ce/bin/grunt` as follows:
    - Add new case entry
        ```
        user:create)
          exec /sbin/setuser www-data node modules/server-ce-scripts/scripts/create-user.mjs "$@"
          ;;
        ```
      to create regular users via command-line
- Update `server-ce/nginx/overleaf.conf` as follows:
  - Add `proxy_hide_header X-Frame-Options;` for locations `/` and `/socket.io` to allow iframe embedding
  - Redirect requests to the registration service by adding the following location to `server-ce/nginx/sharelatex.conf`:
    ```
    location /regsvc {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_hide_header X-Frame-Options;
        proxy_read_timeout 10m;
        proxy_send_timeout 10m;
    }
    ```
  - Replace all instances of `127.0.0.1` by `localhost`

## How to use
### Registration/User management service
A new service called `regsvc` will be launched within the container; it can be reached at the `/regsvc` endpoint.

The service provides various actions, specified through the `action` parameter:

| Action   | Description                                                                                                                          | Parameters                                      |
|----------|--------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `create` | Creates a new user and sets a random password; if a user with the specified email already exists, only the password will be renewed. | `email` - The user's email address (= username) |
| `delete` | Deletes the specified user.                                                                                                          | `email` - The user's email address              |


For all actions, an API key needs to be passed via the `apikey` parameter. This needs to match the `REMOTE_API_KEY` environment variable specified during deployment.

An example `GET` request to this service could look like this:
```
https://mydomain.com/regsvc?action=create&email=my@mail.com
```

#### Configuration
The `regsvc` service can be configured by setting various environment variables:

| Variable | Description                                                                                                 | Default |
| --- |-------------------------------------------------------------------------------------------------------------| --- |
| `REMOTE_API_KEY` | This key is used to protect the various endpoints (except for `open-projects`); it is mandatory to specify. | `""` |
| `REMOTE_API_ALLOWED_CLIENTS` | If set, only the specified clients are allowed to issue requests; wildcards are supported.                  | `""` |

### Local deployment
The directory `local` contains files to run a local deployment alongside a Nextcloud. The `makefile` located in the project root directory can be used to build and run this deployment. Before using this, though, read the instructions in[`LOCAL_DEPLOYMENT.md`](local/LOCAL_DEPLOYMENT.md) carefully, as it will _not_ work out-of-the-box!
