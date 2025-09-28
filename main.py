from dotenv import load_dotenv
load_dotenv()

import argparse
import os
from config import Config
from snyk_api import SnykApi
from logger import Logger
from load_projects import LoadProjects
from reactivate_projects import ReactivateProjects
from models import EnabledModules
from terminal import TerminalUI



def print_banner(terminal: TerminalUI, config: Config):
    with open("banner.txt", "r") as f:
        banner = f.read()
        terminal.print(banner)

    terminal.table.create("Configuration")
    terminal.table.add_column("Config")
    terminal.table.add_column("Value")

    config_str = lambda txt: f"[yellow]{txt}[/yellow]"

    terminal.table.add_row("Organization ID", config_str(config.org_id))
    terminal.table.add_row("Targets limit", config_str(f"{config.limit if config.limit > 0 else 'All Targets'}"))
    terminal.table.add_row("Origins filter", config_str(", ".join(config.origins) if config.origins else "All Origins"))
    terminal.table.add_row("Load Only", config_str(config.load_only))
    terminal.table.add_row("Reactivate Only", config_str(config.reactivate_only))
    terminal.table.add_row("Include CLI Origin", config_str(config.include_cli_origin))
    terminal.table.add_row("Retry Failed", config_str(config.retry_failed))
    terminal.table.add_row("Snyk API Version", config_str(config.api_version))
    terminal.table.add_row("Threads", config_str(config.threads))
    terminal.table.print()


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

    terminal_ui = TerminalUI(config)

    print_banner(terminal_ui, config)

    Logger.init(config)
    logger = Logger.get_instance()

    snyk_api = SnykApi(config)

    logger.info("\n========== Started ==========")

    modules = get_enabled_modules(config)

    num_projects_to_reactivate = 0
    num_project_reactivated = 0
    num_failed_reactivation_projects = 0

    if modules.load:
        load_projects = LoadProjects(config, snyk_api, logger, terminal_ui)
        load_projects.execute()

        num_projects_to_reactivate = load_projects.num_of_projects_to_reactivate()
    
    if modules.reactivate:
        reactivate_projects = ReactivateProjects(config, snyk_api, logger, terminal_ui)
        reactivate_projects.execute()

        num_projects_to_reactivate = reactivate_projects.num_of_projects_to_reactivate()
        num_project_reactivated = reactivate_projects.num_of_projects_reactivated()
        num_failed_reactivation_projects = reactivate_projects.num_of_failed_reactivation_projects()


    logger.info(f"Finished: to reactivate: {num_projects_to_reactivate}, reactivated: {num_project_reactivated}, failed: {num_failed_reactivation_projects}")
    terminal_ui.print(f"Logs saved to [yellow]{os.path.join(config.output_folder_path, 'app.log')}[/yellow]")

    terminal_ui.print("\n")
    terminal_ui.table.create("Summary")
    terminal_ui.table.add_column("Item")
    terminal_ui.table.add_column("Total")
    terminal_ui.table.add_row("To Reactivate", f"{num_projects_to_reactivate}")
    terminal_ui.table.add_row("[green]Reactivated[/green]", f"[green]{num_project_reactivated}[/green]")
    terminal_ui.table.add_row("[red]Failed[/red]", f"[red]{num_failed_reactivation_projects}[/red]")
    terminal_ui.table.print()

if __name__ == "__main__":
    main()