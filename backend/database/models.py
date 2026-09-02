from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(String, unique=True, index=True) # E.g., LUX89A
    host_session_id = Column(String) # Track who created the group
    recommendations_generated = Column(Integer, default=0) # SQLite doesn't have native boolean, use Int 0/1
    stored_recommendations = Column(String, default="[]") # JSON string
    stored_adk_insights = Column(String, default="")
    
    users = relationship("User", back_populates="group")
    preferences = relationship("Preference", back_populates="group")
    votes = relationship("Vote", back_populates="group")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True) # UUID from frontend localStorage
    name = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    
    group = relationship("Group", back_populates="users")
    preference = relationship("Preference", back_populates="user", uselist=False)
    vote = relationship("Vote", back_populates="user", uselist=False)

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    destination_type = Column(String)
    budget = Column(Float)
    
    user = relationship("User", back_populates="preference")
    group = relationship("Group", back_populates="preferences")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    destination_name = Column(String)
    
    user = relationship("User", back_populates="vote")
    group = relationship("Group", back_populates="votes")
