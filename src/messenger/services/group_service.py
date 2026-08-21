import logging
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.models.Group import Group
from messenger.models.GroupMember import GroupMember
from messenger.models.User import User
from messenger.schemas.group_schema import CreateGroupDto, AddMemberDto
from sqlalchemy import select
from messenger.services.user_service import get_user_id
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_group(
    dto: CreateGroupDto, current_user: User, db: AsyncSession
) -> Group:
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
    stmt = (
        select(Group).options(selectinload(Group.members)).where(group_id == Group.id)
    )
    result = await db.execute(stmt)
    group = result.scalars().first()
    if group is None:
        msg = "Not Found"
        return False, msg
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
