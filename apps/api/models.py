from sqlalchemy import String, ForeignKey, DateTime, func
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
