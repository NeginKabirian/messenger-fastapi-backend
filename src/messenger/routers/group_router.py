from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.core.database import get_db
from messenger.models.User import User
from messenger.schemas.group_schema import CreateGroupDto
import messenger.services.group_service as group_service
from messenger.services.user_service import get_current_user, get_admin_user
from messenger.schemas.group_schema import AddMemberDto, sendGroupMessageDto

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


@router.post("/{group_id}/messages", status_code=201)
async def send_message(
    group_id: str,
    dto: sendGroupMessageDto,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, message = await group_service.send_group_message(
        group_id=group_id, dto=dto, current_user=current_user, db=db
    )
    if status:
        return {"status": "success", "message": "Message sent successfully!"}

    if message == "group_not_found":
        raise HTTPException(status_code=404, detail="Group not found.")
    elif message == "forbidden":
        raise HTTPException(
            status_code=403, detail="Only the members can send message."
        )


@router.get("/{group_id}/messages", status_code=200)
async def view_group_messages(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, detail, messages = await group_service.get_group_message(
        group_id=group_id, current_user=current_user, db=db
    )
    if status:
        logger.info(
            f"'{current_user.username}' viewed their group {group_id} inbox via API."
        )
        if not messages:
            return {
                "status": "success",
                "data": [],
                "message": f"Your group {group_id} inbox is empty.",
            }

        resps = []
        for msg in messages:
            time_str = msg.created_at.strftime("%H:%M")

            if msg.sender.username == current_user.username:
                resps.append(f"You: {msg.content} | Time: {time_str}")
            else:
                resps.append(
                    f"{msg.sender.username} | {msg.content} | Time: {time_str}"
                )

        return {"status": "success", "data": resps}

    if detail == "group_not_found":
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found.")
    elif detail == "forbidden":
        raise HTTPException(
            status_code=403, detail="Only the members can view message."
        )


@router.delete("/{group_id}", status_code=200)
async def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, detail = await group_service.delete_group(
        group_id=group_id, current_user=current_user, db=db
    )
    if status:
        return {
            "status": "success",
            "message": f"Group {group_id} deleted successfully!",
        }
    if detail == "group_not_found":
        raise HTTPException(status_code=404, detail="Group not found.")
    elif detail == "forbidden":
        raise HTTPException(
            status_code=403, detail="Only the admin members can delete the group."
        )


@router.get("", status_code=200)
async def get_all_groups(
    admin_user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)
):
    groups = await group_service.get_all_groups(admin_user=admin_user, db=db)
    return {"status": "success", "data": groups}


@router.delete("/{group_id}/members")
async def delete_member_from_group(
    group_id: str,
    dto: AddMemberDto,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, detail = await group_service.delete_member(
        group_id=group_id, dto=dto, admin_user=current_user, db=db
    )
    if status:
        return {"status": "success", "message": "Members deleted successfully!"}

    if detail == "group_not_found":
        raise HTTPException(status_code=404, detail="Group not found.")
    elif detail == "forbidden":
        raise HTTPException(
            status_code=403, detail="Only group admins can delete members."
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="No user to delete",
        )


@router.delete("/{group_id}/messages/{message_id}")
async def delete_group_message(
    group_id: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, detail = await group_service.remove_message(
        group_id=group_id, message_id=message_id, current_user=current_user, db=db
    )
    if status:
        return {"status": "success", "message": "Message deleted successfully."}
    if detail == "group_not_found":
        raise HTTPException(status_code=404, detail="Group not found.")
    elif detail == "message_not_found":
        raise HTTPException(status_code=404, detail="Message not found in this group.")
    elif detail == "not_a_member":
        raise HTTPException(
            status_code=403, detail="You are not a member of this group."
        )
    elif detail == "forbidden":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own messages unless you are an admin.",
        )
