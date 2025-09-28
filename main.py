import argparse
import os
from config import Config
from snyk_api import SnykApi
from logger import Logger
from load_projects import LoadProjects
from reactivate_projects import ReactivateProjects
from models import EnabledModules



def print_banner(config: Config):
    with open("banner.txt", "r") as f:
        banner = f.read()
        print(banner)

    print(f"Organization ID: {config.org_id}")
    print(f"Targets limit: {config.limit if config.limit > 0 else 'All Targets'}")
    print(f"Origins filter: {', '.join(config.origins) if config.origins else 'All Origins'}")
    print(f"Load Only: {config.load_only}")
    print(f"Reactivate Only: {config.reactivate_only}")
    print(f"Include CLI Origin: {config.include_cli_origin}")
    print(f"Retry Failed: {config.retry_failed}")
    print(f"Snyk API Version: {config.api_version}")
    print(f"Threads: {config.threads}")
    print()


def get_enabled_modules(config: Config) -> EnabledModules:
    modules = EnabledModules()

    if config.load_only:
        modules.load = True
        modules.reactivate = False
    
    if config.reactivate_only:
        modules.load = False
        modules.reactivate = True
    
    if config.retry_failed:
        modules.load = False
        modules.reactivate = True

    return modules


def initialize(args, config: Config):
    config.org_id = args.org
    config.limit = args.limit
    config.origins = args.origins
    config.load_only = args.load_only
    config.reactivate_only = args.reactivate_only
    config.include_cli_origin = args.include_cli_origin
    config.retry_failed = args.retry_failed
    config.api_version = args.api_version
    config.threads = args.threads
    config.validate()

    os.makedirs(config.output_folder_path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Recreate SCM Webhooks.')
    parser.add_argument("--org", type=str, required=True, help="Organization ID")
    parser.add_argument("--limit", type=int, help="(optional) Limit number of targets to process (default all projects)", default=0)
    parser.add_argument("--origins", nargs='*', type=str, help="(optional) Reactivate projects only for selected origins, e.g. --origins github bitbucket gitlab", default=[])
    parser.add_argument("--load-only", action="store_true", help="(optional) Only load projects, do not reactivate", default=False)
    parser.add_argument("--reactivate-only", action="store_true", help="(optional) Only reactivate projects, do not load", default=False)
    parser.add_argument("--include-cli-origin", action="store_true", help="(optional) By default, all cli upload/monitor are ignore. Add this option to include them.", default=False)
    parser.add_argument("--retry-failed", action="store_true", help="(optional) Only retry failed reactivation projects only", default=False)
    parser.add_argument("--api-version", type=str, help="(optional) API version to use (default 2024-10-15)", default="2024-10-15")
    parser.add_argument("--threads", type=int, help="(optional) Number of threads to use (default 5)", default=5)
    args = parser.parse_args()

    config = Config()
    initialize(args, config)

    print_banner(config)

    Logger.init(config)
    logger = Logger.get_instance()

    snyk_api = SnykApi(config)

    logger.info("Started")

    modules = get_enabled_modules(config)

    if modules.load:
        load_projects = LoadProjects(config, snyk_api, logger)
        load_projects.execute()
    
    if modules.reactivate:
        reactivate_projects = ReactivateProjects(config, snyk_api, logger)
        reactivate_projects.execute()

    logger.info("---")
    logger.info("Finished")



if __name__ == "__main__":
    main()