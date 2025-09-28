import json
from config import Config
from snyk_api import SnykApi
from logger import Logger
from models import ProjectModel, ResultModel


class LoadProjects:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger

        self._targets_to_reactivate = {}
        

    def execute(self):
        self.logger.info(f"loading projects for ORG {self.config.org_id}")
        response = self.snyk_api.get_org_projects(self.config.org_id, self.config.origins)

        self._parse_api_response_projects(response)

        next_url = response.get('links', {}).get('next')
        
        while next_url and not self._targets_limit_reached():
            response = self.snyk_api.get_org_projects_next_page(next_url)
            self._parse_api_response_projects(response)
            next_url = response.get('links', {}).get('next')

        self._save_results()        


    def _parse_api_response_projects(self, response):
        result = []

        projects = response.get('data', [])

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

        self._filter_projects_to_reactivate(result)


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

    
    def _filter_projects_to_reactivate(self, projects):
        for project in projects:
            if self._targets_limit_reached():
                return

            if self._should_ignore_project(project):
                continue

            self._targets_to_reactivate[project.target_name] = project
    

    def _should_ignore_project(self, project: ProjectModel):
        if project.target_name in self._targets_to_reactivate:
            return True

        if not self.config.include_cli_origin and project.origin == "cli":
            return True

        return False


    def _targets_limit_reached(self):
        return self.config.limit > 0 and len(self._targets_to_reactivate) >= self.config.limit