from sqlalchemy import String, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Organization(Base):
    __tablename__='organizations'

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(255),unique=True)
    created_at:Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now())

class User(Base):
    __tablename__='users'

    id:Mapped[int]=mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    hashed_password:Mapped[str]=mapped_column(String(255))
    role:Mapped[str]=mapped_column(String(50),default='member')
    organization_id:Mapped[int]=mapped_column(ForeignKey('organizations.id'))
    created_at:Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now())

class Evaluation(Base):
    __tablename__='evaluations'

    id:Mapped[int]=mapped_column(primary_key=True)
    job_id:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    owner_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    status:Mapped[str]=mapped_column(String(50))

class AuditLog(Base):
    __tablename__='audit_logs'

    id:Mapped[int]=mapped_column(primary_key=True)
    actor_user_id:Mapped[int | None]=mapped_column(ForeignKey('users.id'),nullable=True)
    organization_id:Mapped[int | None]=mapped_column(ForeignKey('organizations.id'),nullable=True)
    action:Mapped[str]=mapped_column(String(100),index=True)
    resource_type:Mapped[str]=mapped_column(String(100))
    resource_id:Mapped[str | None]=mapped_column(String(255),nullable=True)
    metadata_json:Mapped[dict | None]=mapped_column(JSON,nullable=True)
    created_at:Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now())
