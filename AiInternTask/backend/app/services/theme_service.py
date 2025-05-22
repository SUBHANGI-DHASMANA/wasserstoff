import logging
from typing import List
from ..models.query import Query, ThemeResponse
from ..core.database import queries_collection
from .ollama_service import OllamaService

logger = logging.getLogger(__name__)

class ThemeService:
    @staticmethod
    def identify_themes(query: Query) -> List[ThemeResponse]:
        if not OllamaService.is_available():
            logger.warning("Ollama not available. Skipping theme identification.")
            return [
                ThemeResponse(
                    theme_name="Theme Identification Unavailable",
                    description="Theme identification is unavailable because Ollama is not running.",
                    document_ids=[],
                    supporting_evidence=["Please make sure Ollama is installed and running to enable theme identification."]
                )
            ]

        try:
            doc_responses = []
            for response in query.document_responses:
                doc_responses.append({
                    "document_id": response.document_id,
                    "document_title": response.document_title,
                    "extracted_answer": response.extracted_answer
                })

            theme_results = OllamaService.identify_themes(doc_responses, query.text)

            themes = []
            for theme in theme_results:
                themes.append(ThemeResponse(
                    theme_name=theme.get("theme_name", "Unnamed Theme"),
                    description=theme.get("description", "No description provided"),
                    document_ids=theme.get("document_ids", []),
                    supporting_evidence=theme.get("supporting_evidence", [])
                ))

            queries_collection.update_one(
                {"_id": query.id},
                {"$set": {"themes": [theme.model_dump() for theme in themes]}}
            )

            return themes
        except Exception as e:
            logger.error(f"Error identifying themes: {str(e)}")
            error_theme = ThemeResponse(
                theme_name="Theme Identification Error",
                description=f"An error occurred during theme identification: {str(e)}",
                document_ids=[],
                supporting_evidence=["Please check your Ollama configuration."]
            )

            queries_collection.update_one(
                {"_id": query.id},
                {"$set": {"themes": [error_theme.model_dump()]}}
            )

            return [error_theme]
