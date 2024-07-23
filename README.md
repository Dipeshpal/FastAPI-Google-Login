# FastAPI-Google-Login
 

## First start auth service-

**Setup Auth API-**

1. `cd auth_api`
2. Edit `.env`
3. Run `python main.py`
   
   This will start auth api in `http://localhost:8000`


4. `cd ui_app`
5. Run `python main.py`

   This will start UI App in `http://localhost:8001`

6. Visit `http://localhost:8001/login` to login or signup
7. visit `http://localhost:8001/logout` to logout
8. Page required to log in before access- `http://localhost:8001/protected`


## How to create other API / Pages-
1. `cd ui_app`
2. Open `python main.py` here you can create your APIs or pages.


```
@app.get("/protected")
async def protected(request: Request):
    user = request.cookies.get('user')
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    else:
        return {"message": user}
```

