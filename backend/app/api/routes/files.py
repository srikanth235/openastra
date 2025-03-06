import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import get_logger
from app.models import Message
from app.services.api_search_service import (
    delete_embeddings,
    search_endpoints,
    store_embeddings,
)
from app.services.file_service import upload_files_to_project

router = APIRouter()
logger = get_logger(__name__, service="files")


class UploadResponse(BaseModel):
    message: str
    files: list[str]


class FileContentRequest(BaseModel):
    file: str


class FileContentResponse(BaseModel):
    data: Any
    file: str


class SearchResponse(BaseModel):
    success: bool
    query: str
    results: list[dict] = []
    metadata: dict = {
        "totalEndpoints": 0,
        "searchMethod": "fts",
        "timestamp": "",
        "searchParameters": {"includeExamples": False, "limit": 50, "where": None},
    }
    error: str | None = None


# Create upload directory if it doesn't exist
def ensure_upload_dir(project_id: str) -> Path:
    upload_path = Path(settings.UPLOAD_DIR) / project_id
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.post("/", response_model=UploadResponse)
async def upload_files(
    *,
    project_id: str,
    files: list[UploadFile] = File(...),
) -> Any:
    """
    Upload files to a project and generate embeddings for API collections.
    Returns a list of safe filenames that were successfully uploaded.
    """
    uploaded_files = await upload_files_to_project(project_id=project_id, files=files)

    # Generate embeddings for potential API collections
    for file_path in uploaded_files:
        filename = Path(file_path).name
        if filename.lower().endswith((".json", ".yaml", ".yml")):
            try:
                full_path = Path(settings.UPLOAD_DIR) / file_path
                with full_path.open("r", encoding="utf-8") as f:
                    content = (
                        json.load(f)
                        if filename.lower().endswith(".json")
                        else yaml.safe_load(f)
                    )
                    store_embeddings(project_id, filename, content)
                    logger.info(f"Generated embeddings for file: {filename}")
            except Exception as e:
                logger.error(f"Error processing file for embeddings: {str(e)}")

    return UploadResponse(
        message=f"Successfully uploaded {len(uploaded_files)} files",
        files=uploaded_files,
    )


@router.delete("/", response_model=Message)
async def delete_file(*, file: str) -> Any:
    """Delete a file and its embeddings from a project."""
    logger.info(f"Attempting to delete file: {file}")
    if not file:
        logger.warning("Delete request received with empty file path")
        raise HTTPException(status_code=404, detail="File not found in project")

    full_path = Path(settings.UPLOAD_DIR) / file
    try:
        if full_path.exists():
            full_path.unlink()
            logger.info(f"File deleted: {file}")

            # Delete embeddings if they exist
            project_id = Path(file).parts[0]
            delete_embeddings(project_id, Path(file).name)
            logger.info(f"Embeddings deleted for file: {file}")

    except Exception as e:
        logger.error(f"Error deleting file {file}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    return Message(message=f"File deleted successfully: {file}")


@router.get("/", response_model=FileContentResponse)
async def get_file_content(file: str) -> Any:
    """Get the content of a file."""
    if not file:
        raise HTTPException(status_code=400, detail="File path is required")

    file_path = Path(settings.UPLOAD_DIR) / file

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Try to parse as JSON if it's a JSON file
        if file_path.suffix.lower() == ".json":
            try:
                return FileContentResponse(data=json.loads(content), file=file)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file")

        # Try to parse as YAML if it's a YAML file
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            try:
                return FileContentResponse(data=yaml.safe_load(content), file=file)
            except yaml.YAMLError:
                raise HTTPException(status_code=400, detail="Invalid YAML file")

        # Return raw content for other files
        return FileContentResponse(data=content, file=file)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading file content: {str(e)}"
        )


@router.get("/search", response_model=SearchResponse)
async def search_api_collections(
    project_id: str,
    query: str,
    limit: int = 10,
    where: str | None = None,
) -> Any:
    """
    Search for API endpoints using semantic similarity with optional metadata filtering.
    """
    logger.info(
        f"Searching API collections for project {project_id} with query: {query}"
    )
    try:
        where_filter = None
        if where:
            try:
                where_filter = json.loads(where) or None
                logger.debug(f"Using where filter: {where_filter}")
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid where filter format: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid where filter format. Must be valid JSON",
                )

        results = search_endpoints(project_id, query, limit, where_filter)

        # Process results
        processed_results = []

        # Check if we have valid results
        if (
            results.get("documents")
            and results.get("metadatas")
            and results.get("distances")
            and len(results["documents"]) > 0
        ):
            # Get the first result set (ChromaDB returns nested lists)
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, metadata, distance in zip(
                documents, metadatas, distances, strict=True
            ):
                result = {
                    "endpoint": json.loads(doc) if isinstance(doc, str) else doc,
                    "metadata": metadata,
                    "score": float(distance),
                }
                processed_results.append(result)

        logger.info(
            f"Search completed successfully with {len(processed_results)} results"
        )
        return SearchResponse(
            success=True,
            query=query,
            results=processed_results,
            metadata={
                "totalEndpoints": len(processed_results),
                "searchMethod": "semantic_similarity",
                "timestamp": datetime.now().isoformat(),
                "searchParameters": {
                    "limit": limit,
                    "where": where_filter,
                },
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed for project {project_id}: {str(e)}", exc_info=True)
        return SearchResponse(
            success=False,
            query=query,
            error=f"Search failed: {str(e)}",
        )
