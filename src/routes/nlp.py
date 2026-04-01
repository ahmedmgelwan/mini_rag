from fastapi import FastAPI, APIRouter, Request, status
from fastapi.responses import JSONResponse
from .schemes import PushRequest, SearchRequest
from models import ProjectModel, DataChunkModel
from models.enums import ResposeSignal
from controllers import NLPController

nlp_router = APIRouter(
    prefix='/api/v1',
    tags=['v1', 'nlp']
)


@nlp_router.post('/push/{project_id}')
async def push_project_index(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(request.app.db_client)
    chunk_model = await DataChunkModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResposeSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client
    )
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    
    
    while has_records:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=project.id,
            page_no=page_no)
        print('Page No.', page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) ==0:
            has_records = False
            break
        chunk_ids = list(range(idx+len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vecto_db(
            project=project,
            chunks=page_chunks,
            chunk_ids=chunk_ids,
            do_reset=push_request.do_reset
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'signal': ResposeSignal.INSERT_INTO_VECTOR_DB_ERROR.value
                }
            )
        inserted_items_count += len(page_chunks)
    
    return JSONResponse(
        content={
            "signal": ResposeSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            'inserted_items_count': inserted_items_count
        }
    )
        

@nlp_router.get('/info/{project_id}')
async def get_project_index_info(request: Request, project_id: str, ):
    project_model = await ProjectModel.create_instance(request.app.db_client)
    chunk_model = await DataChunkModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResposeSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            'signal': ResposeSignal.VECTOR_DB_COLLECTION_INFO_RETEIVED.value,
            'collection_info': collection_info
        }
    )


@nlp_router.post('/search/{project_id}')
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(request.app.db_client)
    chunk_model = await DataChunkModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResposeSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client
    )
    results = nlp_controller.search_vector_db_collection(project=project,
                                                         query=search_request.text,
                                                         limit=search_request.limit)
    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'singal': ResposeSignal.VECTOR_DB_SEARCH_ERROR.value
            }
        )
    
    return {
        'signal': ResposeSignal.VECTOR_DB_SEARCH_SUCCESS.value,
        "results": [r.dict() for r in results]
    }

