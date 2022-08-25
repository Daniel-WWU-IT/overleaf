# Changes applied to this container
- Install pip and some Python modules in the container by adding the following to `Dockerfile`:
    ```
    RUN apt-get update \
    &&  apt-get install -y python3-pip \
    &&  python3 -m pip install Flask requests
    ```
- Update TeXLive and install additional packages by adding the following to `Dockerfile`:
    ```
    RUN tlmgr option repository ftp://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/2021/tlnet-final \
    &&  tlmgr update --self \
    &&  tlmgr update --all \
    &&  tlmgr install xcolor
    ```
- Add `runit/remote-api-server/*` as a testing drone
    - Make sure that the `run` file has the executable flag set
- Modify `bin/grunt` as follows:
    - Add new case entry
        ```
        user:create)
          node create-user "$@"
          ;;
        ```
      to create regular users via command-line
- Add `proxy_hide_header X-Frame-Options;` to `nginx/sharelatex.conf` for locations `/` and `/socket.io` to allow iframe embedding

# How to use
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

## Configuration
The `regsvc` service can be configured by setting various environment variables:

| Variable | Description                                                                                                | Default |
| --- |------------------------------------------------------------------------------------------------------------| --- |
| `REMOTE_API_KEY` | This key is used to protect the various endpoints (except for `open-projects`); it is mandatory to specify | `""` |
| `REMOTE_API_ALLOWED_CLIENTS` | If set, only the specified clients are allowed to issue requests; wildcards are supported                  | `""` |
| `REMOTE_API_DATA_KEY` | This key is used to encrypt login data; the key _must_ have a length of 32 characters and is mandatory     | `""` |
