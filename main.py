from fastapi import FastAPI, HTTPException, status
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import models
from database import engine
from routers import auth, todos, admin, user
from routers_html import todos as todos_html
from routers_html import auth as auth_html
from routers_html import user as user_html

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthy", status_code=status.HTTP_200_OK)
async def healthy():
    return {"status": "ok"}


@app.get("/", status_code=status.HTTP_200_OK)
async def home_page():
    return RedirectResponse("/todos", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

app.include_router(todos_html.router)
app.include_router(auth_html.router)
app.include_router(user_html.router)
