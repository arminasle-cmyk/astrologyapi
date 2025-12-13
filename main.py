@app.get("/health")
def health():
    return {
        "status": "OK_FROM_NEW_DEPLOY"
    }
}
