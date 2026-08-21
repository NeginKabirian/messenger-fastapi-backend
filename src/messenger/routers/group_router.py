from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.core.database import get_db
from messenger.models.User import User
from messenger.schemas.group_schema import CreateGroupDto
import messenger.services.group_service as group_service
from messenger.services.user_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", status_code=201)
async def create_group(
    group_dto: CreateGroupDto,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = await group_service.create_group(
        dto=group_dto, current_user=current_user, db=db
    )

    if group is None:
        raise HTTPException(status_code=400, detail="Failed to create group")

    return {
        "status": "success",
        "message": f"User {current_user.username} created group '{group.name}' successfully.",
        "data": {"group_id": group.id, "group_name": group.name},
    }


from messenger.schemas.group_schema import AddMemberDto


@router.post("/{group_id}/members", status_code=200)
async def add_members_to_group(
    group_id: str,
    dto: AddMemberDto,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status, message = await group_service.add_member(group_id, dto, current_user, db)

    if status:
        return {"status": "success", "message": "Members added successfully!"}

    if message == "group_not_found":
        raise HTTPException(status_code=404, detail="Group not found.")
    elif message == "forbidden":
        raise HTTPException(
            status_code=403, detail="Only group admins can add members."
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="No new users were added (maybe invalid IDs or already in group).",
        )
