# Snyk - Reacreate SCM Webhooks

To recreated a missing webhook for a repo, we just need to deactivate and reactivate one project inside that repo.

What this tool does:

1. Get projects for the selected Org.
2. Select one project for each target (repo).
3. Save all targets with project to a file (`targets_to_reactivate.json`).
4. Load the file containing the targets to reactivate.
5. For each target/project, deactivate and reactivate.

This will recreate the webhook for the target.

## Setup

Requirements:
- Python 3.12
- UV
- SNYK_TOKEN env variable to authenticate with Snyk ORG.

Prepare Dev:
- Run `uv sync`
- Activate venv `source .venv/bin/activate`

## Running

```
usage: main.py [-h] --org ORG [--limit LIMIT] [--integrations [INTEGRATIONS ...]] [--load-only] [--reactivate-only] [--include-cli-origin] [--api-version API_VERSION]
               [--threads THREADS]

Recreate SCM Webhooks.

options:
  -h, --help            show this help message and exit
  --org ORG             Organization ID
  --limit LIMIT         (optional) Limit number of targets to process (default all projects)
  --integrations [INTEGRATIONS ...]
                        (optional) Reactivate targets only for selected integrations, e.g. --integrations github bitbucket gitlab
  --load-only           (optional) Only load targets, do not reactivate
  --reactivate-only     (optional) Only reactivate targets, do not load
  --include-cli-origin  (optional) By default, all cli upload/monitor are ignore. Add this option to include them.
  --api-version API_VERSION
                        (optional) API version to use (default 2024-10-15)
  --threads THREADS     (optional) Number of threads to use (default 5)
```


Example:

```sh
export SNYK_TOKEN="token f19c*********21da09"
python main.py --org 65523c0b-3a89-4f55-a819-11c497a7c0d3 --limit 0
```

## Run with Docker

This project contains a Dockerfile to not depend on python or uv install.

```sh
SNYK_TOKEN="token f19c********a09"
ORG_ID="65523c0b-3a89-4f55-a819-11c497a7c0d3"

docker build -t snyk-recreate-scm-webhooks .
docker run --rm -e SNYK_TOKEN="$SNYK_TOKEN" snyk-recreate-scm-webhooks --org $ORG_ID --limit 0
```