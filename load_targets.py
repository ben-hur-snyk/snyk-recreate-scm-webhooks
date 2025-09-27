import json
from config import Config
from snyk_api import SnykApi
from logger import Logger

class LoadTargets:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger

        self.targets_to_reactivate = {}
        

    def execute(self):
        self.logger.info(f"loading targets for ORG {self.config.org_id}")
        response = self.snyk_api.get_org_projects(self.config.org_id)

        projects = response.get('data', [])
        self._bind_targets_to_reactivate(projects)

        next_url = response.get('links', {}).get('next')
        
        while next_url and not self._targets_limit_reached():
            response = self.snyk_api.get_org_projects_next_page(next_url)
            projects = response.get('data', [])
            self._bind_targets_to_reactivate(projects)
            next_url = response.get('links', {}).get('next')

        self._save_results()        


    def _save_results(self):
        json_data = {
            "org_id": self.config.org_id,
            "projects": []
        }

        for target_name, project_id in self.targets_to_reactivate.items():
            json_data["projects"].append({
                "project_id": project_id,
                "target_name": target_name
            })

        with open(self.config.targets_file_path, "w") as f:
            json.dump(json_data, f, indent=4)

    
    def _bind_targets_to_reactivate(self, projects):
        for project in projects:
            if self._targets_limit_reached():
                return
            
            target_name = project.get('attributes', {}).get('name', "").split(":")[0]
            project_id = project.get('id')

            if target_name in self.targets_to_reactivate:
                continue

            self.targets_to_reactivate[target_name] = project_id
    

    def _targets_limit_reached(self):
        return self.config.limit > 0 and len(self.targets_to_reactivate) >= self.config.limit