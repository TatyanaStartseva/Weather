import uvicorn

if __name__ == "__main__":
    uvicorn.run("modules.app.server:app", host="127.0.0.1", port=8000, reload=True)
