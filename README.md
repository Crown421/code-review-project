# Vague Roadmap
1. ~~Set up repo with devcontainer, pre-commit, etc~~
2. ~~Add uv project, some deps, create first scaffolding with dummy endpoints~~
3. ~~Create some dummy data to send, and some methods to send (use mise), also start service~~
4. ~~Add some logic, db storage (sqlite), methods to wipe the db, mock LLM response~~
    - https://docs.pydantic.dev/latest/examples/orms/
    - https://docs.sqlalchemy.org/en/20/orm/quickstart.html
    - https://sqlmodel.tiangolo.com/
5. Ask LLM to create more test data, store, add utility to run as demo


## Some possible additions
- Look at logging, with proper levels, use env variable to set (i.e. debug/info/warn)
- Build container on CI
- Custom review prompts (in separate table, with separate endpoint for setting them)
- Linters?
- Embedding snippets, check if similar snippet was reviewed before and add to context if yes


# Getting started
## Setting up the environment
This project uses a dev container, so the easiest way to work in the same context as me is to
- Use VSCode
- Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Set up a container runtime
    - On Linux, either install `podman` and follow [these instructions](https://code.visualstudio.com/remote/advancedcontainers/docker-options#_podman), or install docker and start the daemon.
    - On Mac, either Docker Desktop or Podman Desktop (again needs [a settings change](https://code.visualstudio.com/remote/advancedcontainers/docker-options#_podman) should work.
- Open this project folder
- Hit Ctrl+P (or the Mac equivalent) and run `Dev Containers: Open Workspace in Container`

## Running the service and commands
This project uses [mise](https://mise.jdx.dev/) to make running various useful commands easy.
Run
```
mise tasks
```
to get a list of available tasks.
