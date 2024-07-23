from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse


app = FastAPI()


@app.get("/login")
async def login(request: Request):
    return RedirectResponse(url="http://localhost:8000/login", status_code=302)


@app.get("/logout")
async def logout(request: Request):
    return RedirectResponse(url="http://localhost:8000/logout", status_code=302)


@app.get("/protected")
async def protected(request: Request):
    user = request.cookies.get('user')
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    else:
        return {"message": user}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)
