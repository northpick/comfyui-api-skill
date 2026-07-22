import json, os, time, random, shutil, requests, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = SKILL_DIR / "registry.json"
WORKFLOWS_DIR = SKILL_DIR / "workflows"

COMFY_API = "http://127.0.0.1:8184"
COMFY_OUTPUT = r"D:\software\ComfyUI_windows_portable\ComfyUI\output"
COMFY_INPUT = r"D:\software\ComfyUI_windows_portable\ComfyUI\input"
DST = SKILL_DIR / "outputs"

os.makedirs(DST, exist_ok=True)
os.makedirs(COMFY_INPUT, exist_ok=True)

def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_workflow(req):
    registry = load_registry()
    wf_name = req["workflowName"]
    wf_meta = registry.get(wf_name)
    if not wf_meta:
        raise ValueError(f"Unknown workflow: {wf_name}. Available: {list(registry.keys())}")

    wf_path = WORKFLOWS_DIR / wf_meta["file"]
    with open(wf_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    prompt = data.get("prompt", data)

    for item in req.get("nodeInfoList", []):
        node_id = item["nodeId"]
        field = item["fieldName"]
        value = item["fieldValue"]
        target = prompt.get(node_id)
        if not target:
            raise KeyError(f"Node '{node_id}' not found in workflow '{wf_name}'")
        if "widgets_values" in target.get("inputs", {}):
            wi = item.get("widgetIndex", 0)
            target["inputs"]["widgets_values"][wi] = value
        else:
            target["inputs"][field] = value

    seeds = {}
    for pk in prompt:
        if prompt[pk].get("class_type") == "KSampler":
            s = random.randint(100000, 99999999)
            prompt[pk]["inputs"]["seed"] = s
            seeds[pk] = s

    output_name = req.get("output_name", f"output_{int(time.time())}")
    timeout_min = req.get("timeout_min", 8)
    return _submit(prompt, output_name, timeout_min, req, seeds)

def _submit(prompt, output_name, timeout_min, req, seeds):
    res = requests.post(f"{COMFY_API}/prompt", json={"prompt": prompt}, timeout=30)
    if res.status_code != 200:
        raise RuntimeError(f"ComfyUI submit failed: {res.status_code} {res.text[:500]}")
    pid = res.json().get("prompt_id", "")
    return _wait_for_completion(pid, output_name, timeout_min, req, seeds)

def _save_sidecar(output_name, req, seeds, pid, output_paths):
    meta = {
        "workflowName": req.get("workflowName"),
        "output_name": output_name,
        "prompt_id": pid,
        "timestamp": datetime.datetime.now().isoformat(),
        "seeds": seeds,
        "nodeInfoList": req.get("nodeInfoList", []),
        "outputs": output_paths,
    }
    sidecar = os.path.join(DST, f"{output_name}.json")
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  Meta: {sidecar}")

def _wait_for_completion(pid, output_name, timeout_min, req, seeds):
    start = time.time()
    deadline = start + timeout_min * 60
    while time.time() < deadline:
        try:
            hr = requests.get(f"{COMFY_API}/history/{pid}", timeout=5)
            if hr.status_code == 200:
                hist = hr.json()
                if pid in hist:
                    outputs = hist[pid].get("outputs", {})
                    images = []
                    for nid, no in outputs.items():
                        for key, items in no.items():
                            if isinstance(items, list):
                                for item in items:
                                    if isinstance(item, dict) and "filename" in item:
                                        sub = item.get("subfolder", "")
                                        images.append(os.path.join(sub, item["filename"]) if sub else item["filename"])
                    if images:
                        results = []
                        for i, rel_path in enumerate(images):
                            src = os.path.join(COMFY_OUTPUT, rel_path)
                            if os.path.exists(src):
                                ext = rel_path.rsplit(".", 1)[1]
                                dst = os.path.join(DST, f"{output_name}.{ext}") if len(images) == 1 else os.path.join(DST, f"{output_name}_{i+1}.{ext}")
                                shutil.copy2(src, dst)
                                results.append(str(dst))
                            else:
                                print(f"  MISSING: {src}")
                        if results:
                            _save_sidecar(output_name, req, seeds, pid, results)
                        return results
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)

    recent = sorted(
        [f for f in os.listdir(COMFY_OUTPUT) if os.path.isfile(os.path.join(COMFY_OUTPUT, f))],
        key=lambda f: os.path.getmtime(os.path.join(COMFY_OUTPUT, f)),
        reverse=True
    )[:3]
    if recent:
        paths = [str(os.path.join(COMFY_OUTPUT, f)) for f in recent]
        _save_sidecar(output_name, req, seeds, pid, paths)
        return paths
    raise TimeoutError(f"Timeout after {timeout_min}min, no output found")

def upload_image(filepath, name=None):
    if not name:
        name = os.path.basename(filepath)
    dst = os.path.join(COMFY_INPUT, name)
    shutil.copy2(filepath, dst)
    return name

def list_workflows():
    registry = load_registry()
    return {k: {"display": v["display"], "description": v["description"], "inputs": v["inputs"]} for k, v in registry.items()}
