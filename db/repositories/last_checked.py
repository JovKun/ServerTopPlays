# Import the necessary libraries
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import LastChecked

# Method to get the last checked timestamp (only one entry is expected in the last_checked table)
async def get_last_checked_time(session: AsyncSession) -> str | None:

    # Execute the select query to retrieve the last checked timestamp
    result = await session.execute(
        select(LastChecked).order_by(LastChecked.id.desc()).limit(1)
    )

    # Get the first (and only) entry from the result
    last_checked_entry = result.scalars().first()

    # If an entry exists, return its last_checked timestamp as a string; otherwise, return None
    if last_checked_entry:
        return str(last_checked_entry.last_checked)
    else:
        return None

# Method to update the last checked timestamp (only one entry is expected in the last_checked table)
async def update_last_checked_time(session: AsyncSession) -> None:

    # Execute the select query to retrieve the last checked entry
    result = await session.execute(
        select(LastChecked).order_by(LastChecked.id.desc()).limit(1)
    )

    # Get the first (and only) entry from the result
    last_checked_entry = result.scalars().first()

    # If an entry exists, update its last_checked timestamp to the current UTC time
    if last_checked_entry:
        last_checked_entry.last_checked = datetime.now(timezone.utc)
        await session.commit()

    # If no entry exists, create a new entry with the current UTC time
    else:
        new_entry = LastChecked(last_checked=datetime.now(timezone.utc))
        session.add(new_entry)
        await session.commit()