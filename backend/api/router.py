from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string
from database import models, schemas, database
from services.recommendation_engine import get_recommendations
from services.adk_agents import run_adk_agents

router = APIRouter()

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

import json

@router.post("/group/create")
def create_group(payload: schemas.GroupCreate, db: Session = Depends(database.get_db)):
    code = generate_code()
    while db.query(models.Group).filter(models.Group.group_code == code).first():
        code = generate_code()
    new_group = models.Group(group_code=code, host_session_id=payload.session_id)
    db.add(new_group)
    db.commit()
    return {"group_code": code}

@router.post("/group/join")
def join_group(payload: schemas.UserJoin, db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.group_code == payload.group_code).first()
    if not group:
        raise HTTPException(status_code=404, detail="Invalid group code")
        
    user = db.query(models.User).filter(models.User.session_id == payload.session_id).first()
    if not user:
        user = models.User(session_id=payload.session_id, name=payload.name, group_id=group.id)
        db.add(user)
    else:
        user.name = payload.name
        user.group_id = group.id
    db.commit()
    return {"message": "Joined successfully", "group_code": group.group_code}

@router.post("/group/preferences")
def set_preferences(payload: schemas.PreferenceCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.session_id == payload.session_id).first()
    if not user or not user.group_id:
        raise HTTPException(status_code=400, detail="User not in a group")
        
    pref = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()
    if pref:
        pref.destination_type = payload.destination_type
        pref.budget = payload.budget
    else:
        pref = models.Preference(user_id=user.id, group_id=user.group_id, 
                                 destination_type=payload.destination_type, budget=payload.budget)
        db.add(pref)
    db.commit()
    return {"message": "Preferences saved"}

@router.post("/group/vote")
def cast_vote(payload: schemas.VoteCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.session_id == payload.session_id).first()
    if not user or not user.group_id:
        raise HTTPException(status_code=400, detail="User not in a group")
        
    vote = db.query(models.Vote).filter(models.Vote.user_id == user.id).first()
    if vote:
        vote.destination_name = payload.destination_name
    else:
        vote = models.Vote(user_id=user.id, group_id=user.group_id, destination_name=payload.destination_name)
        db.add(vote)
    db.commit()
    return {"message": "Vote cast"}

@router.post("/group/{group_code}/generate")
def generate_group_recommendations(group_code: str, payload: schemas.GroupCreate, db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.group_code == group_code).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    if group.host_session_id != payload.session_id:
        raise HTTPException(status_code=403, detail="Only the host can generate recommendations")
        
    total_budget = 0
    types = []
    for u in group.users:
        if u.preference:
            total_budget += u.preference.budget
            types.append(u.preference.destination_type)
            
    if total_budget == 0:
        raise HTTPException(status_code=400, detail="No budgets submitted yet")
        
    most_common_type = max(set(types), key=types.count) if types else "City"
    recs = get_recommendations(pooled_budget=total_budget, pref_type=most_common_type)
    adk_insights = run_adk_agents(group.id, total_budget, recs)
    
    group.recommendations_generated = 1
    group.stored_recommendations = json.dumps(recs)
    group.stored_adk_insights = adk_insights
    db.commit()
    
    return {"message": "Recommendations generated successfully"}

@router.get("/group/{group_code}/state")
def get_group_state(group_code: str, session_id: str, db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.group_code == group_code).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    users_data = []
    total_budget = 0
    
    for u in group.users:
        u_data = {"name": u.name, "has_voted": u.vote is not None, "has_pref": u.preference is not None}
        if u.preference:
            total_budget += u.preference.budget
        users_data.append(u_data)
        
    recs = json.loads(group.stored_recommendations) if group.stored_recommendations else []
        
    # Voting logic
    votes = {}
    for v in group.votes:
        votes[v.destination_name] = votes.get(v.destination_name, 0) + 1
        
    return {
        "group_code": group.group_code,
        "is_host": group.host_session_id == session_id,
        "recommendations_generated": bool(group.recommendations_generated),
        "users": users_data,
        "pooled_budget": total_budget,
        "recommendations": recs,
        "adk_insights": group.stored_adk_insights,
        "votes": votes
    }
