"""FastAPI server for ComfyUI workflow execution service.

POST /prompt_workflow
POST /upload_image
GET  /workflows
GET  /health

Start:
    uvicorn server:app --host 127.0.0.1 --port 8000
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from router import handle_prompt_workflow, handle_upload, handle_list_workflows

app = FastAPI(title="ComfyUI Workflow API", version="2.0")

class NodeInfo(BaseModel):
    nodeId: str
    fieldName: str
    fieldValue: object

class PromptWorkflowRequest(BaseModel):
    workflowName: str
    prompt_id: Optional[str] = None
    client_id: Optional[str] = None
    partial_execution_targets: Optional[list] = None
    nodeInfoList: Optional[list[NodeInfo]] = None
    output_name: Optional[str] = None
    timeout_min: Optional[int] = 8

class UploadRequest(BaseModel):
    filepath: str
    name: Optional[str] = None

@app.post("/prompt_workflow")
def prompt_workflow(req: PromptWorkflowRequest):
    try:
        body = req.model_dump()
        body["nodeInfoList"] = [
            {"nodeId": n.nodeId, "fieldName": n.fieldName, "fieldValue": n.fieldValue}
            for n in (req.nodeInfoList or [])
        ]
        results = handle_prompt_workflow(body)
        return {"status": "ok", "outputs": results}
    except (ValueError, KeyError, TimeoutError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload_image")
def upload_image(req: UploadRequest):
    try:
        fn = handle_upload({"filepath": req.filepath, "name": req.name})
        return {"status": "ok", "filename": fn["filename"]}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/workflows")
def list_workflows():
    return handle_list_workflows()

@app.get("/health")
def health():
    return {"status": "ok"}
