

class ProjectModel:
    def __init__(self, target_name: str, project_id: str, integration: str):
        self.target_name = target_name
        self.project_id = project_id
        self.integration = integration

    
    def to_json(self):
        return {
            "target_name": self.target_name,
            "project_id": self.project_id,
            "integration": self.integration
        }
    
    @staticmethod
    def from_json(json_data):
        result = ProjectModel(
            target_name=json_data.get("target_name"),
            project_id=json_data.get("project_id"),
            integration=json_data.get("integration")
        )
        return result




class ResultModel:
    def __init__(self, org_id: str, projects: list[ProjectModel]):
        self.org_id = org_id
        self.projects = projects

    def to_json(self):
        return {
            "org_id": self.org_id,
            "projects": [proj.to_json() for proj in self.projects]
        }
    
    @staticmethod
    def from_json(json_data):
        result = ResultModel(
            org_id=json_data.get("org_id"),
            projects=[]
        )
        projects = json_data.get("projects", [])
        
        for project in projects:
            result.projects.append(
                ProjectModel.from_json(project)
            )

        return result



