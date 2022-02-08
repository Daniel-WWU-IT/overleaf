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

# How to use
A new service called `regsvc` will be launched within the container; it can be reached at the `/regsvc` endpoint.

To create a new user, issue the following `GET` request:
```
https://mydomain.com/regsvc?email=my@mail.com
```
An activation link will be shown once the account has been created.

It is also possible to directly set a password, circumventing the activation step:
```
https://mydomain.com/regsvc?email=my@mail.com&password=mypassword
```
This will redirect to the Overleaf login page after the account has been created.
