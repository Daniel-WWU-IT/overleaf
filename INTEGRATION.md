# Overleaf Nextcloud Integration - v2.0.0

## Changes applied to Overleaf
_Coming soon!_

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
