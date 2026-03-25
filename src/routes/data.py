from fastapi import FastAPI, APIRouter,UploadFile, status, Depends
from fastapi.responses import JSONResponse
from controllers import DataController
from models.enums import ResposeSignal
import aiofiles
from helpers.config import get_settings, Settings
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix='/api/v1',
    tags=['v1','data'],
)

@data_router.post('/upload/{project_id}')
async def upload(project_id:str ,file:UploadFile, app_settings:Settings =Depends(get_settings)):
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
            'file_path': file_id
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
async def process(project_id):
    return {
        'Process':'processing',
        'project_id':project_id
    }
