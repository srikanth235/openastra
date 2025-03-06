from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.routes.teams import check_team_permissions
from app.core.logger import get_logger
from app.models import (
    Project,
    ProjectOut,
    ProjectsOut,
    Team,
    TeamRole,
)
from app.models.utils import UtilsMessage

router = APIRouter()

logger = get_logger(__name__, service="projects")


def get_project(session: SessionDep, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectOut)
async def create_project(
    *,
    session: SessionDep,
    title: str = Form(...),
    description: str | None = Form(None),
    model: str = Form(...),
    instructions: str | None = Form(None),
    files: list[UploadFile] = File(None),
) -> Any:
    """Create new project with optional file uploads."""
    try:
        # Get team_id
        team_id = session.exec(select(Team.id)).one()

        # Create project first without files
        project_data = {
            "title": title,
            "description": description,
            "model": model,
            "instructions": instructions,
            "team_id": team_id,
            "files": [],  # Initialize empty files list
        }

        # Create and save project to get project_id
        project = Project.model_validate(project_data)
        session.add(project)
        session.commit()
        session.refresh(project)

        # Handle file uploads if present by delegating to the files endpoint
        if files:
            from app.api.routes.files import upload_files

            # Call the upload_files function directly
            upload_response = await upload_files(
                project_id=str(project.id), files=files
            )

            # Update project with the uploaded file paths
            project.files = upload_response.files
            session.add(project)
            session.commit()
            session.refresh(project)

        return ProjectOut.model_validate(project.model_dump())

    except Exception as e:
        # No need for manual cleanup as it's handled by the files endpoint
        raise HTTPException(
            status_code=500, detail=f"Failed to create project: {str(e)}"
        )


@router.get("/", response_model=ProjectsOut)
def read_projects(
    session: SessionDep,
    team_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve projects."""

    # Check team permissions first
    # check_team_permissions(session, team_id, current_user.id)
    team_id = session.exec(select(Team.id)).one()
    statement = select(Project).where(Project.team_id == team_id)

    count = session.exec(select(func.count()).select_from(statement.subquery())).one()
    projects = session.exec(statement.offset(skip).limit(limit)).all()
    projects_out = [
        ProjectOut(
            id=p.id,
            team_id=p.team_id,
            title=p.title,
            description=p.description,
            model=p.model,
            instructions=p.instructions,
            files=p.files,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]
    return ProjectsOut(data=projects_out, count=count)


@router.get("/{project_id}", response_model=ProjectOut)
def read_project(
    *, session: SessionDep, current_user: CurrentUser, project_id: str
) -> Any:
    """Get project by ID."""
    project = get_project(session, project_id)
    # Check if user has access to this project's team
    check_team_permissions(session, project.team_id, current_user.id)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    *,
    session: SessionDep,
    project_id: str,
    title: str = Form(...),
    description: str | None = Form(None),
    model: str = Form(...),
    instructions: str | None = Form(None),
    files: str = Form(None),
    new_files: list[UploadFile] = File(None),
) -> Any:
    """Update a project."""
    logger.info(f"Starting update for project: {project_id}")
    project = get_project(session, project_id)

    # Create update data dictionary from form fields
    update_data = {
        "title": title,
        "description": description,
        "model": model,
        "instructions": instructions,
    }

    # Handle file deletions
    current_files = project.files or []
    files_list = files.split(",") if files and files.strip() else []

    # Find files that need to be deleted
    files_to_delete = [f for f in current_files if f not in files_list]

    # Delete files that are no longer needed
    if files_to_delete:
        logger.info(f"Deleting {len(files_to_delete)} files from project {project_id}")
        from app.api.routes.files import delete_file

        for file_path in files_to_delete:
            try:
                await delete_file(file=file_path)
                logger.debug(f"Successfully deleted file: {file_path}")
            except HTTPException as e:
                # Log error but continue with other deletions
                logger.error(f"Error deleting file {file_path}: {str(e)}")

    # Update project's file list
    project.files = files_list

    # Handle new file uploads
    if new_files:
        logger.info(f"Uploading {len(new_files)} new files to project {project_id}")
        from app.api.routes.files import upload_files

        upload_response = await upload_files(
            project_id=str(project.id), files=new_files
        )
        project.files = project.files + upload_response.files

    # Update other fields
    for field, value in update_data.items():
        setattr(project, field, value)

    session.add(project)
    session.commit()
    session.refresh(project)

    logger.info(f"Successfully updated project {project_id}")
    return ProjectOut.model_validate(project.model_dump())


@router.delete("/{project_id}", response_model=UtilsMessage)
def delete_project(
    *, session: SessionDep, current_user: CurrentUser, project_id: str
) -> Any:
    """Delete a project."""
    project = get_project(session, project_id)
    # Check if user has admin permissions in the team
    check_team_permissions(
        session, project.team_id, current_user.id, [TeamRole.OWNER, TeamRole.ADMIN]
    )

    session.delete(project)
    session.commit()
    return UtilsMessage(message="Project deleted successfully")
