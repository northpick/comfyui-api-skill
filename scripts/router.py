from executor import run_workflow, upload_image, list_workflows

def handle_prompt_workflow(req):
    return run_workflow(req)

def handle_upload(req):
    filepath = req.get("filepath")
    name = req.get("name")
    return {"filename": upload_image(filepath, name)}

def handle_list_workflows():
    return list_workflows()
