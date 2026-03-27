from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums import DatabaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, db_clinet):
        super().__init__(db_clinet)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_clinet):
        instance = cls(db_clinet)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for idx in indexes:
                await self.collection.create_index(
                    idx['key'],
                    name= idx['name'],
                    unique = idx['unique']
                )

    async def create_project(self, project: Project) -> Project:
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        record = await self.collection.find_one({
            'project_id': project_id
        })
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project
        
        return Project(**record)
    
    async def get_all_projects(self, page:int = 1,page_size:int = 10 ):
        total_documents = await self.collection.count_doucments({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
        cursor = self.collection.find().skip((total_pages -1)*page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )
        return projects, total_pages