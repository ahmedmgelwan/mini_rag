from fastapi import FastAPI, APIRouter,UploadFile, status, Depends, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from models.enums import ResponseSignal, AssetTypeEnum
import aiofiles
from helpers.config import get_settings, Settings
import logging
from .schemes import ProcessRequest
from models import ProjectModel,DataChunkModel, AssetModel
from models.db_schemes import DataChunk, Asset
import os



logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix='/api/v1',
    tags=['v1','data'],
)

@data_router.post('/upload/{project_id}')
async def upload(request:Request,project_id:str ,file:UploadFile, app_settings:Settings =Depends(get_settings)):
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    data_controller = DataController()
    is_valid, signal = data_controller.validate_uploaded_file(file)

    if  not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal':signal,
                'uploaded_file_type': file.content_type,
            }
        )
    file_path, file_id = data_controller.generate_unique_file_path(project_id,file.filename)
    try:
        async with aiofiles.open(file_path,'wb') as f:
            while chunk := await file.read(app_settings.GENERATION_DAFAULT_CHUNK_SIZE):
                await f.write(chunk)
        
        asset_model = await AssetModel.create_instance(request.app.db_client)
        _ = await asset_model.create_asset(asset=Asset(
            asset_project_id = project.project_id,
            asset_name = file_id,
            asset_type = AssetTypeEnum.FILE.value,
            asset_size = file.size,
        ))
        return {
            'signal': ResponseSignal.FILE_UPLODED_SUCESS.value,
            'file_id': file_id,
            'project_id': str(project.project_id)
        }
    except Exception as e:
        logger.error(f'Error while uploading {file.filename}: {e}')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.FILE_UPLOADED_FAIL.value
            }
        )


@data_router.post('/process/{project_id}')
async def process(request:Request, project_id:str, process_request: ProcessRequest):
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    asset_model = AssetModel(request.app.db_client)
    project_file_ids = {}
    if process_request.file_id:
            asset_record = await asset_model.get_asset_record(project.project_id,process_request.file_id)
            if asset_record is None:
                return JSONResponse(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    content={
                        'signal': ResponseSignal.FILE_ID_ERROR.value
                    }
                )
            project_file_ids = {asset_record.asset_id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_assets_by_project_id(
            project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE.value
        )
        project_file_ids = {record.asset_id: record.asset_name for record in project_files}
        if len(project_file_ids) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponseSignal.NO_FILES_ERROR.value
            )
    
    process_controller = ProcessController(project_id)
    chunk_model = await DataChunkModel.create_instance(request.app.db_client)

    no_records = 0
    no_files = 0
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project.project_id)

    for asset_id, file_id in project_file_ids.items():
        file_content = process_controller.get_file_content(file_id)
        if file_content is None:
            logger.error(f'Error while processing file {file_id}')
            continue
        text_chunks = process_controller.process_file_content(file_id,file_content,chunk_size,overlap_size)
        if text_chunks is None or  len(text_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'signal':ResponseSignal.FILE_PROCESSING_FAIL.value
                }
            )
    
        text_chunk_records = [
                                DataChunk(
                                    chunk_text= chunk.page_content,
                                    chunk_metadata= chunk.metadata,
                                    chunk_project_id=project.project_id,
                                    chunk_asset_id=asset_id
                                )
                                for i, chunk in enumerate(text_chunks)
                                ]

        no_records += await chunk_model.insert_many_chunks(text_chunk_records)
        no_files += 1
    
    return {
        'signal': ResponseSignal.FILE_PROCESSING_SUCCESS.value,
        'no_inseted_chunks': no_records,
        'processed_files': no_files
    }
