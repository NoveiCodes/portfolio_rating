from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import FeedbackCreate, FeedbackResponse, FeedbackUpdate
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(feedback: FeedbackCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(
        models.User.id == feedback.user_id))
    user = result

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_feedback = models.Feedback(
        rating=feedback.rating,
        feedback=feedback.feedback,
        user_id=feedback.user_id
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback, attribute_names=["author"])
    return new_feedback


@router.get("", response_model=list[FeedbackResponse])
async def get_feedbacks(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Feedback).options(selectinload(models.Feedback.author)))
    feedbacks = result.scalars().all()
    return feedbacks


@router.get("/{feedback_id}", response_model=list[FeedbackResponse])
async def get_feedback(feedback_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Feedback).options(selectinload(models.Feedback.author)).where(
        models.Feedback.id == feedback_id))
    feedback = result.scalars().all()
    if feedback:
        return feedback
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )


@router.patch("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback_partial(feedback_id: int, feedback_data: FeedbackUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Feedback).options(selectinload(models.Feedback.author)).where(
        models.Feedback.id == feedback_id))
    feedback = result.scalars().first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
        )

    update_data = feedback_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)

    await db.commit()
    await db.refresh(feedback, attribute_names=["author"])
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(email: str, feedback_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    user = result.scalars().first()

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post."
        )

    result = await db.execute(select(models.Feedback).options(selectinload(models.Feedback.author)).where(
        models.Feedback.id == feedback_id))
    feedback = result.scalars().first()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
        )

    await db.delete(feedback)
    await db.commit()
