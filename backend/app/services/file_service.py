import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__, service="file_service")


async def upload_files_to_project(
    project_id: str, files: list[UploadFile]
) -> list[str]:
    """
    Upload files to a project.
    Returns a list of safe filenames that were successfully uploaded.
    """
    logger.info(f"Starting file upload for project_id: {project_id}")
    upload_dir = ensure_upload_dir(project_id)
    uploaded_files = []

    for upload_file in files:
        filename = Path(upload_file.filename).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = upload_dir / safe_filename

        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            logger.debug(f"File saved successfully: {safe_filename}")
            relative_path = str(Path(project_id) / safe_filename)
            uploaded_files.append(relative_path)

        finally:
            upload_file.file.close()

    logger.info(
        f"Successfully uploaded {len(uploaded_files)} files to project {project_id}"
    )
    return uploaded_files


def ensure_upload_dir(project_id: str) -> Path:
    """Create upload directory if it doesn't exist"""
    upload_path = Path(settings.UPLOAD_DIR) / project_id
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path
