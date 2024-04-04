import numpy as np
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any, List, Dict, Optional

from ..database import BingoCard
from .checks import BINGO_TASKS
from .type_hints import ProductType


def generate_bingo_card(
    size: int,
    product_types: List[ProductType]
) -> Dict[str, None]:
    filtered_bingo_tasks = {
        idx: task for idx, task in enumerate(BINGO_TASKS, start=1)
        if any([t in task.products for t in product_types])
    }

    p = np.array([task.weight for task in filtered_bingo_tasks.values()])
    p /= p.sum()

    return {
        str(n): None
        for n in np.random.choice(
            a=list(filtered_bingo_tasks.keys()),
            size=size,
            replace=False,
            p=p
        )
    }


async def db_get_bingo_card(
    db: AsyncSession,
    user_id: int
) -> Optional[BingoCard]:
    return (await db.execute(
        select(BingoCard)
        .filter_by(user_id=user_id)
        .limit(1)
    )).scalars().one_or_none()


async def db_update_bingo_card(
    db: AsyncSession,
    user_id: int,
    data: Dict[str, Any]
) -> None:
    await db.execute(
        update(BingoCard)
        .where(BingoCard.user_id == user_id)
        .values(**data)
    )


def count_completed_tasks(bingo_stats: Dict[str, Optional[str]]) -> int:
    count = 0
    for i in bingo_stats.values():
        if i is not None:
            count += 1
    return count
