import requests
from config import Config

class SnykApi:
    def __init__(self, config: Config):
        self.config = config
        self._ORG_API_LIMIT = 100

    
    def get_org_projects(self, org_id, origins = []):
        url = f"{self.config.snyk_base_api_url}/rest/orgs/{org_id}/projects?version={self.config.api_version}&limit={self._ORG_API_LIMIT}"

        if len(origins) > 0:
            url += f"&origins={','.join(origins)}"

        response = requests.get(
            url=url,
            headers={"Authorization":self.config.snyk_token,"Accept":"*/*"},
        )

        data = response.json()

        return data
    
    def get_org_projects_next_page(self, next_page_url):
        response = requests.get(
            f"{self.config.snyk_base_api_url}{next_page_url}",
            headers={"Authorization":self.config.snyk_token,"Accept":"*/*"},
        )

        data = response.json()

        return data


    def get_project_by_id(self, org_id, project_id):
        response = requests.get(
            f"{self.config.snyk_base_api_url}/rest/orgs/{org_id}/projects/{project_id}?version={self.config.api_version}",
            headers={"Authorization":self.config.snyk_token,"Accept":"*/*"},
        )

        data = response.json()
        return data


    def deactivate_project(self, org_id, project_id):
        response = requests.post(
            f"{self.config.snyk_base_api_url}/v1/org/{org_id}/project/{project_id}/deactivate?version={self.config.api_version}",
            headers={"Authorization":self.config.snyk_token,"Accept":"*/*"},
        )

        return response.ok
        

    def activate_project(self, org_id, project_id):
        response = requests.post(
            f"{self.config.snyk_base_api_url}/v1/org/{org_id}/project/{project_id}/activate",
            headers={"Authorization":self.config.snyk_token,"Accept":"*/*"},
        )

        return response.ok
    

