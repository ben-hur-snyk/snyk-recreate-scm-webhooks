import json
import concurrent.futures
from config import Config
from snyk_api import SnykApi
from logger import Logger
from terminal import TerminalUI
from models import ProjectModel, ResultModel


class ReactivateProjects:
    def __init__(self, config: Config, snyk_api: SnykApi, logger: Logger, terminal_ui: TerminalUI):
        self.config = config
        self.snyk_api = snyk_api
        self.logger = logger
        self.terminal_ui = terminal_ui

        self._org_id = self.config.org_id
        self._projects_to_reactivate: list[ProjectModel] = []
        self._projects_reactivated: list[ProjectModel] = []
        self._failed_reactivation_projects: list[ProjectModel] = []
        
    
    def execute(self):
        self.logger.info(f"Loading projects to reactivate")
        self.terminal_ui.print(f"[bold]Loading projects to reactivate[/bold]")
        self._load_projects()

        num_projects_to_reactivate = len(self._projects_to_reactivate)

        self.logger.info(f"Projects to reactivate: {num_projects_to_reactivate}")
        self.terminal_ui.print(f"[bold]Projects to reactivate: [yellow]{num_projects_to_reactivate}[/yellow][/bold]\n")

        self.terminal_ui.progress.create(columns=["description", "bar", "completed", "time"])
        self.terminal_ui.progress.add_task("[green]Reactivated", num_projects_to_reactivate)
        self.terminal_ui.progress.add_task("[red]Failed", num_projects_to_reactivate)
        self.terminal_ui.progress.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(self._reactivate_project, project) for project in self._projects_to_reactivate]
            
            for future in concurrent.futures.as_completed(futures):
                future.result()

        self.terminal_ui.progress.stop()
        self._save_results()


    def num_of_projects_to_reactivate(self):
        return len(self._projects_to_reactivate)
    
    def num_of_projects_reactivated(self):
        return len(self._projects_reactivated)
    
    def num_of_failed_reactivation_projects(self):
        return len(self._failed_reactivation_projects)

        
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
            self.terminal_ui.progress.update("[green]Reactivated", 1)
            self.logger.success(f"reactivate target {project.target_name} | project_id: {project.project_id} | origin: {project.origin}")
        except Exception as e:
            self._failed_reactivation_projects.append(project)
            self.terminal_ui.progress.update("[red]Failed", 1)
            self.logger.error(f"reactivating target {project.target_name} | project_id: {project.project_id} | origin: {project.origin} | error: {str(e)}")


    def _load_projects(self):
        file_to_load = self.config.projects_to_reactivate_file_path

        if self.config.retry_failed:
            file_to_load = self.config.failed_projects_reactivation_file_path

        self.logger.info(f"Load projects from {file_to_load}")
        self.terminal_ui.print(f"Load projects from [yellow]{file_to_load}[/yellow]")

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

        self.logger.info(f"Reactivated projects saved to {self.config.reactivated_projects_file_path}")
        self.terminal_ui.print(f"\n[green]Reactivated[/green] projects saved to [yellow]{self.config.reactivated_projects_file_path}[/yellow]")

        failed = ResultModel(
            org_id=self._org_id,
            projects=self._failed_reactivation_projects
        )

        with open(self.config.failed_projects_reactivation_file_path, "w") as f:
            json.dump(failed.to_json(), f, indent=2)

        self.logger.info(f"Failed projects saved to {self.config.failed_projects_reactivation_file_path}")
        self.terminal_ui.print(f"[red]Failed[/red] projects saved to [yellow]{self.config.failed_projects_reactivation_file_path}[/yellow]")
        

        

        


    