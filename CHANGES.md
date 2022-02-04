# Changes applied to this container
- Install pip and Flask in the container by adding the following to `Dockerfile`:
    ```
    RUN apt-get update \
    &&  apt-get install -y python3-pip \
    &&  python3 -m pip install Flask
    ```
- Add `runit/remote-api-server/run` as a testing drone
- Modify `bin/grunt` as follows:
    - Add new case entry
        ```
        user:create)
          node create-user "$@"
          ;;
        ```
      to create regular users via command-line
