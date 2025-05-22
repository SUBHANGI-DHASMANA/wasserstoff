import logging
import json
import requests
import hashlib
from typing import Dict, Any, List, Optional
from ..config import OLLAMA_API_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

RESPONSE_CACHE = {}

class OllamaService:
    @staticmethod
    def is_available() -> bool:
        try:
            try:
                response = requests.get(f"{OLLAMA_API_URL.rstrip('/api')}/version", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Ollama is available at {OLLAMA_API_URL.rstrip('/api')}/version")
                    return True
            except Exception as e:
                logger.warning(f"Could not connect to Ollama version endpoint: {str(e)}")

            try:
                response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [model.get("name", "").split(":")[0] for model in models]

                    logger.info(f"Available Ollama models: {model_names}")

                    if OLLAMA_MODEL in model_names or any(model.startswith(OLLAMA_MODEL) for model in model_names):
                        logger.info(f"Ollama model {OLLAMA_MODEL} is available")
                        return True
                    else:
                        logger.warning(f"Ollama is available but model {OLLAMA_MODEL} is not found. Available models: {model_names}")
                        return False

                logger.info(f"Ollama is available at {OLLAMA_API_URL}")
                return True
            except Exception as e:
                logger.warning(f"Could not connect to Ollama API endpoint: {str(e)}")

            return False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {str(e)}")
            return False

    @staticmethod
    def generate_response(prompt: str, system_message: Optional[str] = None, max_tokens: int = 1000) -> Optional[str]:
        try:
            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }

            if system_message:
                data["system"] = system_message

            response = requests.post(
                f"{OLLAMA_API_URL}/generate",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

            response_data = response.json()
            return response_data.get("response", "")

        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return None

    @staticmethod
    def extract_answer_from_document(document_text: str, query: str) -> Dict[str, Any]:
        if not OllamaService.is_available():
            logger.warning("Ollama API not available. Make sure Ollama is installed and running.")
            return {
                "extracted_answer": "Unable to extract answer: Ollama API not available",
                "citations": []
            }

        try:
            system_message = """
            You are a document analysis assistant. Your task is to:
            1. Extract relevant information from the document text that answers the query
            2. Provide a concise answer based on the document content
            3. Include citations with page numbers, paragraphs, and relevant sentences
            4. Only use information from the provided document
            5. If the document doesn't contain relevant information, state that clearly

            Format your response as JSON with the following structure:
            {
                "extracted_answer": "The concise answer based on the document",
                "citations": [
                    {
                        "page_number": 1,
                        "paragraph": 2,
                        "sentence": "The exact sentence from the document that supports the answer",
                        "relevance_score": 0.95
                    }
                ]
            }
            """

            max_chars = 4000
            if len(document_text) > max_chars:
                truncated_text = document_text[:max_chars] + "... [text truncated]"
                logger.info(f"Document text truncated from {len(document_text)} to {max_chars} characters")
            else:
                truncated_text = document_text

            prompt = f"Query: {query}\n\nDocument Text:\n{truncated_text}"

            cache_key = hashlib.md5((prompt + (system_message or "")).encode()).hexdigest()

            if cache_key in RESPONSE_CACHE:
                logger.info(f"Using cached response for query: {query[:30]}...")
                response = RESPONSE_CACHE[cache_key]
            else:
                response = OllamaService.generate_response(prompt, system_message, max_tokens=2000)
                if response:
                    RESPONSE_CACHE[cache_key] = response
                    if len(RESPONSE_CACHE) > 100:
                        RESPONSE_CACHE.pop(next(iter(RESPONSE_CACHE)))

            if not response:
                return {
                    "extracted_answer": "Unable to extract answer due to API error",
                    "citations": []
                }

            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)

                    # Validate the structure
                    if "extracted_answer" not in result:
                        result["extracted_answer"] = "Answer extraction failed: Invalid response format"

                    if "citations" not in result or not isinstance(result["citations"], list):
                        result["citations"] = []

                    return result
                else:
                    return {
                        "extracted_answer": response,
                        "citations": []
                    }

            except json.JSONDecodeError:
                return {
                    "extracted_answer": response,
                    "citations": []
                }

        except Exception as e:
            logger.error(f"Error extracting answer: {str(e)}")
            return {
                "extracted_answer": f"Error extracting answer: {str(e)}",
                "citations": []
            }

    @staticmethod
    def identify_themes(document_responses: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        if not OllamaService.is_available():
            logger.warning("Ollama API not available. Make sure Ollama is installed and running.")
            return [{
                "theme_name": "Theme Identification Unavailable",
                "description": "Theme identification is unavailable because Ollama API is not available.",
                "document_ids": [],
                "supporting_evidence": ["Please make sure Ollama is installed and running to enable theme identification."]
            }]

        try:
            document_responses_text = ""
            for i, doc_response in enumerate(document_responses):
                document_responses_text += f"Document {i+1} (ID: {doc_response['document_id']}, Title: {doc_response['document_title']}):\n"
                document_responses_text += f"Answer: {doc_response['extracted_answer']}\n\n"

            system_message = """
            You are a research assistant that identifies themes in document responses.
            Analyze the document responses to a query and identify meaningful themes.

            If there are multiple documents, identify common themes across them.
            If there is only one document, identify the main themes within that document.

            For each theme:
            1. Provide a clear theme name
            2. Write a concise description of the theme
            3. List the document IDs that support this theme
            4. Include supporting evidence from the documents

            Format your response as JSON with the following structure:
            [
                {
                    "theme_name": "Name of Theme 1",
                    "description": "Description of Theme 1",
                    "document_ids": ["doc1", "doc2"],
                    "supporting_evidence": ["Evidence 1", "Evidence 2"]
                }
            ]

            Identify at least 2-3 themes if possible, but only include genuinely meaningful themes.
            """

            max_chars = 3000
            if len(document_responses_text) > max_chars:
                truncated_text = document_responses_text[:max_chars] + "... [text truncated]"
                logger.info(f"Document responses text truncated from {len(document_responses_text)} to {max_chars} characters")
            else:
                truncated_text = document_responses_text

            prompt = f"Query: {query}\n\nDocument Responses:\n\n{truncated_text}"

            cache_key = hashlib.md5((prompt + (system_message or "")).encode()).hexdigest()

            if cache_key in RESPONSE_CACHE:
                logger.info(f"Using cached theme response for query: {query[:30]}...")
                response = RESPONSE_CACHE[cache_key]
            else:
                response = OllamaService.generate_response(prompt, system_message, max_tokens=3000)
                if response:
                    RESPONSE_CACHE[cache_key] = response
                    if len(RESPONSE_CACHE) > 100:
                        RESPONSE_CACHE.pop(next(iter(RESPONSE_CACHE)))

            if not response:
                return [{
                    "theme_name": "Theme Identification Error",
                    "description": "An error occurred during theme identification.",
                    "document_ids": [],
                    "supporting_evidence": ["Please check that Ollama is running correctly."]
                }]

            try:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    themes = json.loads(json_str)

                    if not isinstance(themes, list):
                        return [{
                            "theme_name": "Theme Identification Error",
                            "description": "Invalid response format from Ollama API.",
                            "document_ids": [],
                            "supporting_evidence": ["The API response was not in the expected format."]
                        }]

                    return themes
                else:
                    return [{
                        "theme_name": "Theme Identification Error",
                        "description": "Could not parse themes from Ollama API response.",
                        "document_ids": [],
                        "supporting_evidence": ["The API response did not contain valid JSON."]
                    }]

            except json.JSONDecodeError:
                return [{
                    "theme_name": "Theme Identification Error",
                    "description": "Could not parse themes from Ollama API response.",
                    "document_ids": [],
                    "supporting_evidence": ["The API response did not contain valid JSON."]
                }]

        except Exception as e:
            logger.error(f"Error identifying themes: {str(e)}")
            return [{
                "theme_name": "Theme Identification Error",
                "description": f"An error occurred during theme identification: {str(e)}",
                "document_ids": [],
                "supporting_evidence": ["Please check that Ollama is running correctly."]
            }]
