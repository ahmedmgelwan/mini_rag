from fastapi import FastAPI, APIRouter,UploadFile, status, Depends, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from models.enums import ResposeSignal
import aiofiles
from helpers.config import get_settings, Settings
import logging
from .schemes import ProcessRequest
from models import ProjectModel,DataChunkModel
from models.db_schemes import DataChunk


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
            while chunk := await file.read(app_settings.FILE_DEFUALT_CHUNK_SIZE):
                await f.write(chunk)
        return {
            'signal': ResposeSignal.FILE_UPLODED_SUCESS.value,
            'file_id': file_id,
            'projec_id': str(project.id)
        }
    except Exception as e:
        logger.error(f'Error while uploading {file.filename}: {e}')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResposeSignal.FILE_UPLOADED_FAIL.value
            }
        )


@data_router.post('/process/{project_id}')
async def process(request:Request, project_id:str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    project_model = await ProjectModel.create_instance(db_clinet=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id)
    file_content = process_controller.get_file_content(file_id)
    text_chunks = process_controller.process_file_content(file_id,file_content,chunk_size,overlap_size)
    if text_chunks is None or  len(text_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal':ResposeSignal.FILE_PROCESSING_FAIL.value
            }
        )
    
    text_chunk_records = [
                            DataChunk(
                                chunk_text= chunk.page_content,
                                chunk_metadata= chunk.metadata,
                                chunk_order = i+1,
                                project_id=project.id
                            )
                            for i, chunk in enumerate(text_chunks)
                            ]
    chunk_model = await DataChunkModel.create_instance(request.app.db_client)
    # return text_chunk_records
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project.id)

    no_records = await chunk_model.insert_many_chunks(text_chunk_records)
    return {
        'signal': ResposeSignal.FILE_PROCESSING_SUCCESS.value,
        'no_inseted_chunks': no_records
    }
