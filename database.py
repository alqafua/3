"""SQLAlchemy models and data-access helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    language = Column(String(8), nullable=True)
    plan = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default="new")
    expires_at = Column(DateTime, nullable=True)
    used_trial = Column(Boolean, nullable=False, default=False)
    invite_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class UsedTransaction(Base):
    __tablename__ = "used_transactions"

    txid = Column(String(255), primary_key=True)
    network = Column(String(16), nullable=False)
    used_by = Column(BigInteger, nullable=False)
    used_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_or_create_user(user_id: int, username: Optional[str] = None) -> User:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            user = User(user_id=user_id, username=username, status="new")
            session.add(user)
            session.commit()
            session.refresh(user)
        elif username and user.username != username:
            user.username = username
            session.commit()
            session.refresh(user)
        return user


def get_user(user_id: int) -> Optional[User]:
    with SessionLocal() as session:
        return session.get(User, user_id)


def set_language(user_id: int, language: str) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.language = language
            session.commit()


def set_pending_plan(user_id: int, plan: str) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.plan = plan
            user.status = "pending_payment"
            session.commit()


def set_status(user_id: int, status: str) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.status = status
            session.commit()


def activate_subscription(
    user_id: int,
    plan: str,
    expires_at: datetime,
    invite_link: Optional[str],
) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            return
        user.plan = plan
        user.status = "active"
        user.expires_at = expires_at
        user.invite_link = invite_link
        if plan == "trial":
            user.used_trial = True
        session.commit()


def mark_expired(user_id: int) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.status = "expired"
            session.commit()


def get_expired_users(now: datetime) -> list[User]:
    with SessionLocal() as session:
        users = (
            session.query(User)
            .filter(User.status == "active", User.expires_at.isnot(None), User.expires_at <= now)
            .all()
        )
        session.expunge_all()
        return users


def is_txid_used(txid: str) -> bool:
    with SessionLocal() as session:
        return session.get(UsedTransaction, txid) is not None


def mark_txid_used(txid: str, network: str, used_by: int) -> None:
    with SessionLocal() as session:
        if session.get(UsedTransaction, txid) is not None:
            return
        session.add(UsedTransaction(txid=txid, network=network, used_by=used_by))
        session.commit()
