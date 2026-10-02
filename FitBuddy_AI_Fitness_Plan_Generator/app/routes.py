from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from .database import SessionLocal, User, WorkoutPlan
from .schemas import UserInput
from .gemini_generator import (
    generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan
)

router = APIRouter()
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience: str = Form("Beginner"),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username, user_id=user_id, age=age, weight=weight,
            goal=goal, intensity=intensity, experience=experience
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={"error": f"Please check your entries: {exc}"},
            status_code=422
        )

    user = db.query(User).filter(User.user_id == data.user_id).first()
    if user is None:
        user = User(**data.model_dump())
        db.add(user)
    else:
        for key, value in data.model_dump().items():
            setattr(user, key, value)
    db.commit()
    db.refresh(user)

    try:
        plan = generate_workout_gemini(user)
        tip = generate_nutrition_tip_with_flash(user.goal)
    except RuntimeError as exc:
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={"error": str(exc), "previous": data.model_dump()},
            status_code=502
        )

    record = WorkoutPlan(
        user_id=user.user_id, original_plan=plan,
        nutrition_tip=tip
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return templates.TemplateResponse(
        request=request, name="result.html",
        context={"user": user, "plan": plan, "nutrition_tip": tip, "plan_id": record.id, "message": None}
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    plan_id: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    record = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user_id
    ).first()
    if not user or not record:
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={"error": "That saved plan could not be found. Please create a new plan."},
            status_code=404,
        )
    cleaned_feedback = feedback.strip()
    if len(cleaned_feedback) < 5 or len(cleaned_feedback) > 1000:
        return templates.TemplateResponse(
            request=request, name="result.html",
            context={
                "user": user,
                "plan": record.updated_plan or record.original_plan,
                "nutrition_tip": record.nutrition_tip,
                "plan_id": record.id,
                "message": "Feedback must be between 5 and 1000 characters.",
                "feedback_error": True,
            },
            status_code=422,
        )
    try:
        revised = update_workout_plan(user, record.updated_plan or record.original_plan, cleaned_feedback)
        tip = generate_nutrition_tip_with_flash(user.goal)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    record.updated_plan = revised
    record.feedback = cleaned_feedback
    record.nutrition_tip = tip
    db.commit()
    db.refresh(record)
    return templates.TemplateResponse(
        request=request, name="result.html",
        context={"user": user, "plan": revised, "nutrition_tip": tip,
                 "plan_id": record.id, "message": "Your plan has been updated using your feedback."}
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    records = db.query(WorkoutPlan).order_by(WorkoutPlan.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request, name="all_users.html",
        context={"users": users, "records": records}
    )


@router.post("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/view-all-users", status_code=303)
