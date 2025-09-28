import json
import concurrent.futures
from config import Config
from snyk_api import SnykApi
from logger import Logger
from models import ProjectModel, ResultModel


class ReactivateProjects:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger

        self._org_id = self.config.org_id
        self._projects_to_reactivate: list[ProjectModel] = []
        self._projects_reactivated: list[ProjectModel] = []
        self._failed_reactivation_projects: list[ProjectModel] = []
        
    
    def execute(self):
        self._load_projects()
        self.logger.info(f"projects to reactivate: {len(self._projects_to_reactivate)}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(self._reactivate_project, project) for project in self._projects_to_reactivate]
            
            for future in concurrent.futures.as_completed(futures):
                future.result()

        self._save_results()
            
        
    def _reactivate_project(self, project: ProjectModel):
        try:
            self.snyk_api.deactivate_project(
                self._org_id,
                project.project_id
            )
            
            self.snyk_api.activate_project(
                self._org_id, project.project_id
            )

            self._projects_reactivated.append(project)
            self.logger.success(f"reactivate target {project.target_name} | project_id: {project.project_id}")
        except Exception as e:
            self._failed_reactivation_projects.append(project)
            self.logger.error(f"reactivating target {project.target_name} | project_id: {project.project_id} | error: {str(e)}")


    def _load_projects(self):
        file_to_load = self.config.projects_to_reactivate_file_path

        if self.config.retry_failed:
            file_to_load = self.config.failed_projects_reactivation_file_path

        with open(file_to_load, "r") as f:
            data = f.read()
            json_data = json.loads(data)

            result = ResultModel.from_json(json_data)

            self._org_id = result.org_id
            self._projects_to_reactivate = result.projects


    def _save_results(self):
        reactivated = ResultModel(
            org_id=self._org_id,
            projects=self._projects_reactivated
        )

        with open(self.config.reactivated_projects_file_path, "w") as f:
            json.dump(reactivated.to_json(), f, indent=2)

        failed = ResultModel(
            org_id=self._org_id,
            projects=self._failed_reactivation_projects
        )

        with open(self.config.failed_projects_reactivation_file_path, "w") as f:
            json.dump(failed.to_json(), f, indent=2)

        


    