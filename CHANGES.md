# Changes applied to this container
- Add `runit/remote-api-server/run` as a testing drone
- Modify `bin/grunt` as follows:
    - Add new case entry
        ```
        user:create)
          node create-user "$@"
          ;;
        ```
      to create regular users via command-line
      
