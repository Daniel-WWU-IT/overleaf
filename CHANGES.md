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
