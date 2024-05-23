import random

from sqlmodel import Session

from app import crud
from app.models import Action, ActionCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string, random_string


def create_random_action(db: Session) -> Action:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None

    chat_id = random_string()
    parent_id = random_string() if random.random() < 0.5 else None
    type = random.choice(["type1", "type2", "type3"])
    steps = {
        "key1": random_lower_string(),
        "key2": random_lower_string(),
    }
    result = (
        {
            "result_key": random_lower_string(),
            "result_value": random_lower_string(),
        }
        if random.random() < 0.5
        else None
    )
    status = random.choice(["pending", "in_progress", "completed", "failed"])

    action_in = ActionCreate(
        chat_id=chat_id,
        parent_id=parent_id,
        type=type,
        steps=steps,
        result=result,
        status=status,
    )

    return crud.create_action(session=db, action_in=action_in, owner_id=owner_id)
