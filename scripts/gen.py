"""Simplified ComfyUI generation entry point.
Usage:
    from gen import submit, upload, available

    # Text-to-image
    submit("flux", [{"nodeId": "693:135", "fieldName": "text", "fieldValue": "a cat"}])

    # Image-to-image (upload first, then submit)
    upload("my_photo.png")
    submit("multi_ref", [
        {"nodeId": "111", "fieldName": "prompt", "fieldValue": "edit this photo"},
        {"nodeId": "129", "fieldName": "image", "fieldValue": "my_photo.png"},
    ])
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from executor import run_workflow, list_workflows, upload_image as _upload

def submit(workflow_name, node_info_list, output_name=None, timeout_min=8):
    req = {
        "workflowName": workflow_name,
        "nodeInfoList": node_info_list or [],
        "output_name": output_name,
        "timeout_min": timeout_min,
    }
    return run_workflow(req)

def upload(filepath, name=None):
    return _upload(filepath, name)

def available():
    return list_workflows()
