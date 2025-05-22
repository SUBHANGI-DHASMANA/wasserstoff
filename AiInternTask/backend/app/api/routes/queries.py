from fastapi import APIRouter, HTTPException, status
from ...models.query import QueryCreate, QueryResponse
from ...services.query_service import QueryService
from ...services.theme_service import ThemeService

router = APIRouter()

@router.post("/", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
def create_query(query_create: QueryCreate):
    try:
        query = QueryService.create_query(query_create)

        from ...services.ollama_service import OllamaService
        if OllamaService.is_available():
            try:
                themes = ThemeService.identify_themes(query)
            except Exception as theme_error:
                from ...services.theme_service import logger
                logger.error(f"Error identifying themes: {str(theme_error)}")
                from ...models.query import ThemeResponse
                themes = [
                    ThemeResponse(
                        theme_name="Theme Identification Error",
                        description="An error occurred during theme identification.",
                        document_ids=[],
                        supporting_evidence=[f"Error details: {str(theme_error)}"]
                    )
                ]
                from ...core.database import queries_collection
                if queries_collection is not None:
                    queries_collection.update_one(
                        {"_id": query.id},
                        {"$set": {"themes": [theme.model_dump() for theme in themes]}}
                    )
        else:
            from ...models.query import ThemeResponse
            themes = [
                ThemeResponse(
                    theme_name="Theme Identification Unavailable",
                    description="Theme identification is unavailable because Ollama is not running.",
                    document_ids=[],
                    supporting_evidence=["Please make sure Ollama is installed and running to enable theme identification."]
                )
            ]
            from ...core.database import queries_collection
            if queries_collection is not None:
                queries_collection.update_one(
                    {"_id": query.id},
                    {"$set": {"themes": [theme.model_dump() for theme in themes]}}
                )
        try:
            updated_query = QueryService.get_query(query.id)
            if updated_query is None:
                
                import logging
                logging.warning(f"Could not retrieve updated query with ID {query.id}, using original query object")
                updated_query = query
        except Exception as query_error:
            import logging
            logging.error(f"Error retrieving updated query: {str(query_error)}", exc_info=True)
            updated_query = query
        return QueryResponse(
            id=updated_query.id,
            query_text=updated_query.text,
            document_responses=updated_query.document_responses,
            themes=updated_query.themes or [],
            created_at=updated_query.created_at
        )
    except Exception as e:
        import logging
        logging.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/{query_id}", response_model=QueryResponse)
def get_query(query_id: str):
    try:
        query = QueryService.get_query(query_id)
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with ID {query_id} not found"
            )
        return QueryResponse(
            id=query.id,
            query_text=query.text,
            document_responses=query.document_responses,
            themes=query.themes,
            created_at=query.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting query: {str(e)}"
        )
