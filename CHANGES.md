# Changes applied to this container
- Build custom base image to use the full Texlive distribution by applying the following changes to `server-ce/Dockerfile-base`: 
    - Set `selected_scheme` to `scheme-full`
    - Update Texlive:
      ```
      RUN tlmgr update --self \
      &&  tlmgr update --all
      ```
- Modifications to the main Docker file `server-ce/Dockerfile`:
    - Use the custom base image
    - Install pip and some Python modules:
        ```
        RUN apt-get update \
        &&  apt-get install -y python3-pip \
        &&  python3 -m pip install Flask requests cryptography beautifulsoup4 gunicorn
        ```
    - Add some web files:
        ```
        COPY server-ce/runit/reverse-proxy/*.js /overleaf/services/web/public/js/
        COPY server-ce/runit/reverse-proxy/*.css /overleaf/services/web/public/stylesheets/
        ``` 
- Add `server-ce/runit/remote-api-server` and `server-ce/runit/reverse-proxy`
    - Make sure that the `run` files have the executable flag set
- Modify `server-ce/bin/grunt` as follows:
    - Add new case entry
        ```
        user:create)
          node modules/server-ce-scripts/scripts/create-user "$@"
          ;;
        ```
      to create regular users via command-line
- Add `proxy_hide_header X-Frame-Options;` to `server-ce/nginx/sharelatex.conf` for locations `/` and `/socket.io` to allow iframe embedding
- Add the following setting to `server-ce/config/settings.js`:
    ```
    cookieSessionLength: false,
    ```
- Redirect `GET` requests to the reverse proxy service through `server-ce/nginx/sharelatex.conf` by adding the following to the `/` location:
    ```
    if ($request_method = GET) {
        proxy_pass http://localhost:9000;
    }
    if ($request_method != GET) {
        proxy_pass http://localhost:3000;
    }
    ```
- Replace all instances of `127.0.0.1` by `localhost` in `server-ce/nginx/sharelatex.conf` 
- The following changes need to be made in the `web` service:
  - `frontend/js/features/project-list/components/project-list-root.tsx`:
    - To remove the *Welcome to Overleaf* screen, change `totalProjectsCount == 0 ?` (around L61) to `totalProjectsCount >= 0 ?`

# How to use
## Registration/User management service
A new service called `regsvc` will be launched within the container; it can be reached at the `/regsvc` endpoint.

The service provides various actions, specified through the `action` parameter:

| Action | Description                                                                                                                                                                 | Parameters                                                                                             |
| --- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `create` | Creates a new user; if a user with the specified email already exists, nothing happens                                                                                      | `email` - The user's email address (= username)<br/> `password` - Optionally sets the account password |
| `login` | Logs the specified in; this will return a link that can be followed afterwards                                                                                              | `email` - The user's email address <br/> `password` - The user's password                              |
| `create-and-login` | Combines the actions `create` and `login`: The user is created if it doesn't exist yet and is logged in afterwards; the returned data can be used to open the projects page | `email` - The user's email address <br/> `password` - The user's password                              |
| `open-projects` | Redirects to the projects page after a user has been logged in                                                                                                              | `data` - The data returned by a previous login call                                                    |

For all actions except `open-projects`, an API key needs to be passed via the `apikey` parameter. This needs to match the `REMOTE_API_KEY` environment variable specified during deployment.

An example `GET` request to this service could look like this:
```
https://mydomain.com/regsvc?action=create&email=my@mail.com&password=mypass&apikey=123key
```

Note that leaving out the `action` parameter will default to `create-and-login`.

### Configuration
The `regsvc` service can be configured by setting various environment variables:

| Variable | Description                                                                                                | Default |
| --- |------------------------------------------------------------------------------------------------------------| --- |
| `REMOTE_API_KEY` | This key is used to protect the various endpoints (except for `open-projects`); it is mandatory to specify | `""` |
| `REMOTE_API_ALLOWED_CLIENTS` | If set, only the specified clients are allowed to issue requests; wildcards are supported                  | `""` |
| `REMOTE_API_DATA_KEY` | This key is used to encrypt login data; the key _must_ have a length of 32 characters and is mandatory     | `""` |
