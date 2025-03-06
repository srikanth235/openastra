from pathlib import Path

from fastapi import UploadFile
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import ProjectCreate, TeamCreate, User, UserCreate
from app.services.file_service import upload_files_to_project

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


async def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Create the database if it doesn't exist
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud.create_user(session=session, user_create=user_in)
            team_in = TeamCreate(
                name="Default",
                description="Default team",
            )
            team = crud.create_team(  # noqa: F841
                session=session, team_create=team_in, owner_id=user.id
            )

            # Create default project
            project_in = ProjectCreate(
                title="Sample Project",
                description="This is a sample project with OpenAstra backend API collection.",
                model=settings.LLM_DEFAULT_MODEL,
                instructions="""For baseUrl, use host as localhost and port as 8000.
                 Health endpoint is hosted at GET /api/v1/utils/health.""",
                team_id=team.id,
            )
            project = crud.create_project(session=session, project_create=project_in)

            # Read the collection file
            collection_path = Path("./openapi_backend_spec.json")

            # Create upload file
            upload_file = UploadFile(
                filename="openapi_backend_spec.json", file=open(collection_path, "rb")
            )

            try:
                # Upload the collection file using the new service
                uploaded_files = await upload_files_to_project(
                    project_id=str(project.id), files=[upload_file]
                )

                # Update project with file path
                project.files = uploaded_files
                session.add(project)
                session.commit()
            finally:
                upload_file.file.close()
