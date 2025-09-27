import argparse
import os
from config import Config
from snyk_api import SnykApi
from logger import Logger
from load_targets import LoadTargets
from reactivate_targets import ReactivateTargets


config = None
snyk_api = None
logger = None

processed_targets = set()


def print_banner(config: Config):
    with open("banner.txt", "r") as f:
        banner = f.read()
        print(banner)

    print(f"Organization ID: {config.org_id}")
    print(f"Targets limit: {config.limit if config.limit > 0 else 'All Targets'}")
    print(f"Load Only: {config.load_only}")
    print(f"Reactivate Only: {config.reactivate_only}")
    print(f"Snyk API Version: {config.api_version}")
    print()


def initialize(args):
    global config, snyk_api, logger

    config = Config()
    config.org_id = args.org
    config.limit = args.limit
    config.load_only = args.load_only
    config.reactivate_only = args.reactivate_only
    config.api_version = args.api_version
    config.validate()

    os.makedirs(config.output_folder_path, exist_ok=True)

    Logger.init(config)
    logger = Logger.get_instance()

    snyk_api = SnykApi(config)


def main():
    parser = argparse.ArgumentParser(description='Reactivate projects.')
    parser.add_argument("--org", type=str, required=True, help="Organization ID")
    parser.add_argument("--limit", type=int, help="(optional) Limit number of targets to process (0 for no limit, default 3)", default=3)
    parser.add_argument("--load-only", action="store_true", help="(optional) Only load targets, do not reactivate")
    parser.add_argument("--reactivate-only", action="store_true", help="(optional) Only reactivate targets, do not load")
    parser.add_argument("--api-version", type=str, help="(optional) API version to use (default 2024-10-15)", default="2024-10-15")
    args = parser.parse_args()
    
    initialize(args)

    print_banner(config)

    logger.info("Started")

    should_load = not config.reactivate_only

    if should_load:
        load_targets = LoadTargets(config, snyk_api, logger)
        load_targets.execute()
    
    
    should_reactivate = not config.load_only

    if should_reactivate:
        reactivate_targets = ReactivateTargets(config, snyk_api, logger)
        reactivate_targets.execute()

    logger.info("---")
    logger.info(f"targets reactivated: {len(reactivate_targets.targets_reactivated)}")
    logger.info("Finished")



if __name__ == "__main__":
    main()