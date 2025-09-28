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
usage: main.py [-h] --org ORG [--limit LIMIT] [--origins [ORIGINS ...]] [--load-only] [--reactivate-only] [--include-cli-origin] [--retry-failed]
               [--api-version API_VERSION] [--threads THREADS]

Recreate SCM Webhooks.

options:
  -h, --help            show this help message and exit
  --org ORG             Organization ID
  --limit LIMIT         (optional) Limit number of targets to process (default all projects)
  --origins [ORIGINS ...]
                        (optional) Reactivate projects only for selected origins, e.g. --origins github bitbucket gitlab
  --load-only           (optional) Only load projects, do not reactivate
  --reactivate-only     (optional) Only reactivate projects, do not load
  --include-cli-origin  (optional) By default, all cli upload/monitor are ignore. Add this option to include them.
  --retry-failed        (optional) Only retry failed reactivation projects only
  --api-version API_VERSION
                        (optional) API version to use (default 2024-10-15)
  --threads THREADS     (optional) Number of threads to use (default 5)
```

### Options

#### `--org`
The Organization ID. e.g. `--org 65523c0b-3a89-4f55-a819-11c497a7c0d3`


#### `--limit`
By default, the tool select one project for each target, all targets. To limit number of targets selected, use this option. e.g. `--limit 10`


#### `--origins [ORIGINS ...]`
By default, the tool reactivate one project for each target, all targets in all origins (except created from CLI).

To restrict the origins the tool should fetch projects, use this option. e.g. `--origins github bitbucket`


#### `--load-only`
By default, the tool will fetch projects first, then save the projects that need to be reactivated in `projects_to_reactivate.json` file.
After this, it will read this file and reactivate each project.

To only fetch the projects and not reactivate them, use this option. e.g. `--load-only`


#### `--reactivate-only`
By default, the tool will fetch projects first, then save the projects that need to be reactivated in `projects_to_reactivate.json` file.
After this, it will read this file and reactivate each project.

To not fetch the projects and only reactivate the projects, use this option. e.g. `--reactivate-only`


### `--include-cli-origin`
By default, the tool not include projects created from `CLI`. To include them, use this option. e.g. `--include-cli-origin`


#### `--retry-failed`
After reactivate the projects, two files will be created:

- `reactivated_projects.json`: has all the successfuly reactivated projects
- `failed_projects_reactivation.json`: has all the failed reactivation projects

If you want to retry the failed projects, use this option. e.g. `--retry-failed`


#### `--api-version`
Use this option to configure which api version to use. e.g. `--api-version 2024-10-15`


#### `--threads`
You can configure the number of threads for reactivation process. e.g. `--threads 5`



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