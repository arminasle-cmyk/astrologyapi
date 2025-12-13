from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/docs-test")
def docs_test():
    return {"docs": "should work"}
