# Vague Roadmap
1. Set up repo with devcontainer, pre-commit, etc
2. Add uv project, some deps, create first scaffolding with dummy endpoints
3. Create some dummy data to send, and some methods to send (use mise), also start service
4. Add some logic, db storage (sqlite), methods to wipe the db, mock LLM response
5. Ask LLM to create more test data, store, add utility to run as demo


## Some possible additions
- Look at logging, with proper levels, use env variable to set (i.e. debug/info/warn)
- Build container on CI
- Custom review prompts (in separate table, with separate endpoint for setting them)
- Linters?
