import uvicorn

from app.main import app

if __name__ == "__main__":
    print(app.host())
    uvicorn.run("start_server:app", host="127.0.0.1", port=8000, reload=True)
