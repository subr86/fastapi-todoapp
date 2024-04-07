from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models import Users
from database import SessionLocal
from routers.auth import bcrypt_context
from routers_html.auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def user_edit_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    return templates.TemplateResponse("user.html", {"request": request, "user": user_model})


@router.post("/", response_class=HTMLResponse)
async def user_edit(request: Request,
                    first_name: str = Form(...),
                    last_name: str = Form(...),
                    phone_number: str = Form(...),
                    db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        msg = "User does not exists"
    else:
        user_model.first_name = first_name
        user_model.last_name = last_name
        user_model.phone_number = phone_number

        db.add(user_model)
        db.commit()

        msg = "Account saved"

    return templates.TemplateResponse("user.html", {"request": request, "message": msg, "user": user_model})


@router.post("/change_password", response_class=HTMLResponse)
async def user_edit(request: Request,
                    current_password: str = Form(...),
                    new_password: str = Form(...),
                    db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        msg = "User does not exists"
    else:
        if not bcrypt_context.verify(current_password, user_model.password):
            msg = "Current password is incorrect."
        else:
            user_model.password = bcrypt_context.hash(new_password)
            db.add(user_model)
            db.commit()

            msg = "Password changed successfully"

    return templates.TemplateResponse("user.html", {"request": request, "message_ch_pass": msg, "user": user_model})
