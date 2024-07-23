# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.staticfiles import StaticFiles
from auth_api.app.database_management import get_db, User, Session as DBSession
from datetime import datetime
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY_AUTH'))
# app.mount("/static", StaticFiles(directory="static"), name="static")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': os.getenv('redirect_url_auth')
    }
)

templates = Jinja2Templates(directory="templates")


@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )
    user_info = token.get('userinfo')
    response = RedirectResponse(url=os.getenv('redirect_url_after_login'))
    if user_info:
        request.session['user'] = dict(user_info)
        response.set_cookie(key='user', value=user_info)

        # Save user information in the database
        db_user = db.query(User).filter(User.email == user_info['email']).first()
        if not db_user:
            db_user = User(
                email=user_info['email'],
                name=user_info['name'],
                given_name=user_info['given_name'],
                family_name=user_info['family_name'],
                picture=user_info['picture'],
                created_at=datetime.utcnow()
            )
            db.add(db_user)

            # Save session information in the database
            db_session = DBSession(
                email=user_info['email'],
                name=user_info['name'],
                last_login_time=datetime.utcnow()
            )
            db.add(db_session)
            db.commit()
            print("User Created")
        else:
            print("User already exists")
    return response


@app.get('/logout')
def logout(request: Request, db: Session = Depends(get_db)):
    user_info = request.session.get('user')
    if user_info:
        db_session = db.query(DBSession).filter(DBSession.email == user_info['email']).first()
        if db_session:
            db_session.logout_time = datetime.utcnow()
            db.commit()

    request.session.pop('user')
    request.session.clear()
    response = RedirectResponse(url=os.getenv('redirect_url_after_login'))
    response.delete_cookie('user')
    return response


@app.get('/authenticate')
async def authenticate(request: Request):
    user = request.session.get('user')
    if user:
        return {"status": True}
    return {"status": False}


@app.get('/get_user_details')
async def authenticate(request: Request, email: str):
    user = request.session.get('user')
    if user:
        print(user)
        return True

