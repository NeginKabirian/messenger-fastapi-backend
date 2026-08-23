import logging
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.models.Group import Group
from messenger.models.GroupMember import GroupMember
from messenger.models.User import User
from messenger.models.Message import Message
from messenger.schemas.group_schema import (
    CreateGroupDto,
    AddMemberDto,
    sendGroupMessageDto,
)
from sqlalchemy import select
from messenger.services.user_service import get_user_id
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


async def create_group(dto: CreateGroupDto, current_user: User, db: AsyncSession) -> Group:
    logger.debug(f"Attempting to create group by user: {current_user.username}")
    group = Group(owner_id=current_user.id, name=dto.name, description=dto.description)
    owner_member = GroupMember(user_id=current_user.id, is_admin=True)
    group.members.append(owner_member)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    logger.info(
        f"User '{current_user.username}' successfully created group '{group.name}'."
    )
    return group


async def add_member(
    group_id: str, dto: AddMemberDto, current_user: User, db: AsyncSession
) -> tuple[bool, str]:
    logger.debug(
        f"Attempting to add members to group {group_id} by user: {current_user.username}"
    )
    stmt = select(Group).options(selectinload(Group.members)).where(group_id == Group.id)
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        return False, "group_not_found"
    current_member_record = next(
        (m for m in group.members if m.user_id == current_user.id), None
    )
    if current_member_record is None or not current_member_record.is_admin:
        logger.warning(
            f"User {current_user.username} tried to add members without admin rights!"
        )
        return False, "forbidden"
    existing_user = [m.user_id for m in group.members]
    count = 0
    for u_id in dto.users_ids:
        if u_id in existing_user:
            logger.info(f"User {u_id} is already in the group.")
            continue
        user_to_add = await get_user_id(u_id, db=db)
        if user_to_add is None:
            logger.info(f"User with ID {u_id} not found!")
            continue

        new_member = GroupMember(user_id=u_id)
        group.members.append(new_member)
        count += 1

    if count > 0:
        await db.commit()
        logger.info(f"{count} new members added to group {group.name}.")
        return True, "success"
    else:
        return False, "no_users_added"


async def delete_member(
    group_id: str, dto: AddMemberDto, admin_user: User, db: AsyncSession
) -> tuple[bool, str]:
    logger.debug(
        f"Attempting to delete members to group {group_id} by admin: {admin_user.username}"
    )
    stmt = select(Group).options(selectinload(Group.members)).where(Group.id == group_id)
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        return False, "group_not_found"
    current_member_record = next(
        (m for m in group.members if m.user_id == admin_user.id), None
    )
    if current_member_record is None or not current_member_record.is_admin:
        logger.warning(
            f"User {admin_user.username} tried to delete members without admin rights!"
        )
        return False, "forbidden"
    existing_user = [m.user_id for m in group.members]
    count = 0
    for u_id in dto.users_ids:
        if u_id in existing_user:
            # performance check
            stmt = select(GroupMember).where(
                group_id == GroupMember.group_id, u_id == GroupMember.user_id
            )
            result = await db.execute(stmt)
            group_member = result.scalars().first()
            await db.delete(group_member)
            count += 1

    if count > 0:
        await db.commit()
        logger.info(f"{count} members deleted from group {group.name}.")
        return True, "success"
    else:
        return False, "no_users_to_delete"


async def send_group_message(
    group_id: str, dto: sendGroupMessageDto, current_user: User, db: AsyncSession
) -> tuple[bool, str]:
    logger.debug(
        f"Attempting to send message to group {group_id} by user: {current_user.username}"
    )
    stmt = select(Group).options(selectinload(Group.members)).where(group_id == Group.id)
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        msg = "group_not_found"
        return False, msg
    current_member_record = next(
        (m for m in group.members if m.user_id == current_user.id), None
    )
    if current_member_record is None:
        logger.warning(
            f"User {current_user.username} tried to send mesage without membership!"
        )
        return False, "forbidden"

    current_user.last_seen = datetime.now()
    message = Message(sender_id=current_user.id, group_id=group_id, content=dto.content)
    db.add(message)
    await db.commit()
    return True, "success"


async def get_group_message(
    group_id: str, current_user: User, db: AsyncSession
) -> tuple[bool, str, List[Message]]:
    logger.debug(
        f"Attempting to view group {group_id} messages by user: {current_user.username}"
    )
    stmt = (
        select(Group)
        .options(
            selectinload(Group.messages).selectinload(Message.sender),
            selectinload(Group.members),
        )
        .where(group_id == Group.id)
    )
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        return False, "group_not_found", []
    current_member_record = next(
        (m for m in group.members if m.user_id == current_user.id), None
    )
    if current_member_record is None:
        logger.warning(
            f"User {current_user.username} tried to view mesage without membership!"
        )
        return False, "forbidden", []
    current_user.last_seen = datetime.now()
    await db.commit()
    group.messages.sort(key=lambda x: x.created_at, reverse=True)
    return True, "success", group.messages


async def delete_group(
    group_id: str, current_user: User, db: AsyncSession
) -> tuple[bool, str]:
    logger.debug(f"Attempting to delete group {group_id} by user: {current_user.username}")
    stmt = select(Group).options(selectinload(Group.members)).where(Group.id == group_id)
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        return False, "group_not_found"
    current_member_record = next(
        (m for m in group.members if m.user_id == current_user.id), None
    )
    if current_member_record is None:
        logger.warning(
            f"User {current_user.username} tried to delete group without membership!"
        )
        return False, "forbidden"
    if not current_member_record.is_admin:
        logger.warning(
            f"User {current_user.username} tried to delete group {group_id} without admin rights!"
        )
        return False, "forbidden"
    await db.delete(group)
    await db.commit()
    return True, "success"


async def get_all_groups(admin_user: User, db: AsyncSession):
    stmt = select(Group)
    result = await db.execute(stmt)
    logger.debug(f"Attempting to get all groups by admin: {admin_user.username}")
    return list(result.scalars().all())


async def remove_message(
    group_id: str, message_id: str, current_user: User, db: AsyncSession
) -> tuple[bool, str]:
    stmt = (
        select(Group)
        .options(selectinload(Group.messages), selectinload(Group.members))
        .where(Group.id == group_id)
    )
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        return False, "group_not_found"
    current_member_record = next(
        (m for m in group.members if m.user_id == current_user.id), None
    )

    if current_member_record is None:
        logger.warning(
            f"User {current_user.username} tried to remove message without membership!"
        )
        return False, "not_a_member"

    message_record = next((m for m in group.messages if m.id == message_id), None)

    if message_record is None:
        return False, "message_not_found"

    if message_record.sender_id != current_user.id and not current_member_record.is_admin:
        logger.warning(
            f"User {current_user.username} tried to delete someone else's message!"
        )
        return False, "forbidden"

    group.messages.remove(message_record)
    await db.commit()

    logger.info(
        f"Message {message_id} was successfully deleted from group {group.name} by {current_user.username}."
    )
    return True, "success"
