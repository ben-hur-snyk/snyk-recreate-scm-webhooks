import json
from config import Config
from snyk_api import SnykApi
from logger import Logger
from terminal import TerminalUI
from models import ProjectModel, ResultModel


class LoadProjects:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger, terminal_ui: TerminalUI):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger
        self.terminal_ui = terminal_ui


        self._targets_to_reactivate = {}
        

    def execute(self):
        self.logger.info(f"Loading projects for ORG {self.config.org_id}")
        self.terminal_ui.print(f"[bold]Loading projects for ORG: [/bold][yellow]{self.config.org_id}[/yellow]")

        self.terminal_ui.status.create("Loading projects")

        response = self._fetch_projects_from_api()
        projects = self._parse_api_response_projects(response)
        self._filter_projects_to_reactivate(projects)

        self.terminal_ui.status.stop()
        self.terminal_ui.print(
            f"Found [bold yellow]{len(self._targets_to_reactivate)}[/bold yellow] targets to reactivate"
        )
        self.logger.info(f"Found {len(self._targets_to_reactivate)} targets to reactivate")

        self._save_results()        


    def num_of_projects_to_reactivate(self):
        return len(self._targets_to_reactivate)


    def _fetch_projects_from_api(self):
        projects = []
        response = self.snyk_api.get_org_projects(
            self.config.org_id,
            self.config.origins,
            self.config.project_ids
        )

        projects.extend(response.get('data', []))

        next_url = response.get('links', {}).get('next')
        
        while next_url:
            response = self.snyk_api.get_org_projects_next_page(next_url)
            projects.extend(response.get('data', []))
            next_url = response.get('links', {}).get('next')

        return projects

    def _parse_api_response_projects(self, projects):
        result = []

        for project in projects:
            target_name = project.get('attributes', {}).get('name', "").split(":")[0]
            origin = project.get('attributes', {}).get('origin', "")
            project_id = project.get('id')

            result.append(
                ProjectModel(
                    target_name=target_name,
                    project_id=project_id,
                    origin=origin
                )
            )

        return result


    def _save_results(self):
        results = ResultModel(
            org_id=self.config.org_id,
            projects=[]
        )

        for _, project in self._targets_to_reactivate.items():
            results.projects.append(project)

        json_data = results.to_json()

        with open(self.config.projects_to_reactivate_file_path, "w") as f:
            json.dump(json_data, f, indent=2)

        self.terminal_ui.print(
            f"Results saved to [yellow]{self.config.projects_to_reactivate_file_path}[/yellow]"
        )
        self.logger.info(f"Results saved to {self.config.projects_to_reactivate_file_path}")


    
    def _filter_projects_to_reactivate(self, projects):
        for project in projects:
            if self._should_ignore_project(project):
                continue

            self._targets_to_reactivate[project.target_name] = project
    

    def _should_ignore_project(self, project: ProjectModel):
        if project.target_name in self._targets_to_reactivate:
            return True

        if not self.config.include_cli_origin and project.origin == "cli":
            return True

        return False