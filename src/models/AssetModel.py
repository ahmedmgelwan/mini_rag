from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums import DatabaseEnum
from bson import ObjectId


class AssetModel(BaseDataModel):
    def __init__(self, db_clinet):
        super().__init__(db_clinet)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for idx in indexes:
                await self.collection.create_index(
                    idx['key'],
                    name = idx['name'],
                    unique = idx['unique']
                )

    async def create_asset(self, asset: Asset):
        record = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = record.inserted_id
        return record
    
    async def get_assets_by_project_id(self, project_id:ObjectId):
        result = await self.collection.find({
            'project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id
        })
        return result