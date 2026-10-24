from fastapi import FastAPI
from typing import Optional
from . import database

app = FastAPI()

@app.get("/")
def home_page():
    return {"message":"This is the home page!"}

@app.get("/test/{parameter}")
def path_param_test(parameter:int):
    return {"message":"This is a test for path parameters", "parameter":parameter}

@app.get("/test")
def req_param_test(p : Optional[int] = None):
    if p is None:
        test_msg = dict()
        test_msg["name"] = "This is a test message, hello!"
        test_msg["type"] = 0
        return [test_msg]
    return {"message":"This is a test for request parameters", "parameter":p}
