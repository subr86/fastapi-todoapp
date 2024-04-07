from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from routers.auth import login_for_access_token, SECRET_KEY, ALGORITHM, get_db, bcrypt_context
from models import Users

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_login_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


templates = Jinja2Templates(directory="templates")


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            logout(request)
        return {
            "username": username,
            "id": user_id,
            "user_role": user_role
        }
    except JWTError:
        logout(request)
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_login_form()
        response = RedirectResponse("/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse("login.html", {"request": request, "message": msg})
        return response
    except HTTPException:
        msg = "Unknown error"
        return templates.TemplateResponse("login.html", {"request": request, "message": msg})


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Logout successful"
    response = templates.TemplateResponse("login.html", {"request": request, "message": msg})
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        email: str = Form(...),
                        username: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(...),
                        firstname: str = Form(...),
                        lastname: str = Form(...),
                        db: Session = Depends(get_db)):
    validation1 = db.query(Users).filter(Users.username == username).first()
    validation2 = db.query(Users).filter(Users.email == email).first()

    if password != password2 or validation1 or validation2:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "message": msg})

    user = Users(
        username=username,
        email=email,
        first_name=firstname,
        last_name=lastname,
        password=bcrypt_context.hash(password),
        role="user"
    )
    db.add(user)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "message": msg})
