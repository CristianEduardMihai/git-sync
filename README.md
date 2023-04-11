# git-sync
A python tool used to sync cloud servers with github repos, with pull and push capabilities

## Instalation
- Install PyGithub
  ```python3 -m pip install PyGithub```
  
  ## Usage
  - Rename `sync_config.json.example` to `sync_config.json`
  - Fill out `sync_config.json`
  ```json
    "github_email": "your github account's email",
    "github_username": "the username of the github account that made the repo you are trying to sync with",
    "github_token": "github token. get one here: https://github.com/settings/tokens",
    "repo_name": "the name of the repository you are trying to sync with",
    "run_cmd": "the command to run after the sync is complete. for example `python3 main.py`"
  ```
