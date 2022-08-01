# Changes applied to this container
- Install pip and some Python modules in the container by adding the following to `Dockerfile`:
    ```
    RUN apt-get update \
    &&  apt-get install -y python3-pip \
    &&  python3 -m pip install Flask requests
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

| Action | Description                                                                                                        | Parameters                                                                                             |
| --- |--------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `create` | Creates a new user; if a user with the specified email already exists, nothing happens                             | `email` - The user's email address (= username)<br/> `password` - Optionally sets the account password |
| `login` | Logs the specified in; this will also redirect to the main Overleaf page                                           | `email` - The user's email address <br/> `password` - The user's password                              |
| `create-and-login` | Combines the actions `create` and `login`: The user is created if it doesn't exist yet and is logged in afterwards | `email` - The user's email address <br/> `password` - The user's password                                                                                              |

An example `GET` request to this service could look like this:
```
https://mydomain.com/regsvc?action=create&email=my@mail.com&password=mypass
```

Note that leaving out the `action` parameter will default to `create-and-login`.
