# Vague Roadmap
Basic setup
1. ~~Set up repo with devcontainer, pre-commit, etc~~
2. ~~Add uv project, some deps, create first scaffolding with dummy endpoints~~
3. ~~Create some dummy data to send, and some methods to send (use mise), also start service~~
4. ~~Add some logic, db storage (sqlite), methods to wipe the db, mock LLM response~~
    - https://docs.pydantic.dev/latest/examples/orms/
    - https://docs.sqlalchemy.org/en/20/orm/quickstart.html
    - https://sqlmodel.tiangolo.com/
5. ~~Add LLM to the mix~~
6. ~~Add docker file, CI build, docker-compose.yml~~


## Some possible additions
- Look at logging, with proper levels, use env variable to set (i.e. debug/info/warn)
- Add tests (out of time for today)
- User specific review prompts (in separate table, with separate endpoint for setting them)
    - Add endpoint that lets users send custom prompts, request body should include username, language, and the prompt itself.
    - When a query hits the snippets endpoint, retrieve the custom user prompt, if there is one the user/ language combination.
- Prompt versioning using a tool like MLFLow
    - The formatting/ system prompts are currently hardcoded, better would be to store them in a prompt manager and retrieve the correct version at runtime (based on config/ env variables)
- Run a linter first (i.e. ruff, jslint, ...), for example using a sys call, to reduce LLM/ token usage
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

## Secrets
For development, this projects requires an OpenAI api key stored in an `.env` file at the top of the repo, that looks like
```
OPENAI_API_KEY=sk-....
```
A better approach could be to add [fnox](https://fnox.jdx.dev/), store the secret either using local encryption or better in a cloud secret manager, and use `mise` to add it to the relevant commands (i.e. `fnox exec -- uv run fastapi dev server/src/main.py`).
This would also allow using basically identically commands locally and in the cloud (where secret manager access would be injected for example via IAM.)

## Docker compose
This repo also builds the service image on CI, and provides a `docker-compose.yml` that consumes that image.
If you prefer using it, and also would like to avoid using `mise`, you can start the service with
```
docker compose up
```
in the repo root. If you are using podman, you may need to install [podman-compose](https://github.com/containers/podman-compose) as well.

You can then test the service for example with
```
curl -X 'POST' \
  'http://127.0.0.1:8000/snippets' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "@data/sample1.json" | jq
```
(Note that the response gets piped into `jq`, which should be installed on most systems.)
