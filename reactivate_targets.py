import json
from config import Config
from snyk_api import SnykApi
from logger import Logger


class ReactivateTargets:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger

        self.targets_reactivated = []

        self._targets_to_reactivate = []
        
    
    def execute(self):
        self._load_targets()
        self.logger.info(f"targets to reactivate: {len(self._targets_to_reactivate)}")

        for target in self._targets_to_reactivate:
            project_id = target.get("project_id")
            target_name = target.get("target_name")

            try:
                self.snyk_api.deactivate_project(
                    self.config.org_id,
                    project_id
                )
                
                self.snyk_api.activate_project(
                    self.config.org_id, project_id
                )

                self.targets_reactivated.append(target)
                self.logger.success(f"reactivate target {target_name} | project_id: {project_id}")
            except Exception as e:
                self.logger.error(f"reactivating target {target_name} | project_id: {project_id} | error: {str(e)}")
        

    def _load_targets(self):
        with open(self.config.targets_file_path, "r") as f:
            data = f.read()
            json_data = json.loads(data)
            self._targets_to_reactivate = json_data.get("projects", [])

    