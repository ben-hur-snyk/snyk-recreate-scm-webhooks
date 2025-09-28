import os


class Config:
    def __init__(self):
        self.org_id = None
        self.project_ids = []
        self.origins = []
        self.load_only = False
        self.reactivate_only = False
        self.include_cli_origin = False
        self.retry_failed = False
        self.api_version = "2024-10-15"
        self.threads = 5
        
        self.snyk_token = os.environ.get("SNYK_TOKEN")
        self.snyk_base_api_url = "https://api.snyk.io"
        self.output_folder_path = ".output"
        self.log_file_path = os.path.join(self.output_folder_path, "app.log")
        self.projects_to_reactivate_file_path = os.path.join(self.output_folder_path, "projects_to_reactivate.json")
        self.reactivated_projects_file_path = os.path.join(self.output_folder_path, "reactivated_projects.json")
        self.failed_projects_reactivation_file_path = os.path.join(self.output_folder_path, "failed_projects_reactivation.json")
        

    def validate(self):
        if not self.org_id:
            raise ValueError("🚫 Organization ID is required (set via --org or ORG_ID env variable)")
        
        if not self.snyk_token:
            raise ValueError("🚫 SNYK_TOKEN environment variable is required")