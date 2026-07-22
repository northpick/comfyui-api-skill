"""Check ComfyUI API connectivity and workflow registry health."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import requests
from executor import COMFY_API, REGISTRY_PATH

def check_comfy():
    print(f"Checking ComfyUI at {COMFY_API}...")
    try:
        r = requests.get(f"{COMFY_API}/prompt", timeout=5)
        print(f"  ComfyUI: {'OK' if r.status_code in (200, 405) else f'Status {r.status_code}'}")
    except requests.exceptions.ConnectionError:
        print(f"  ComfyUI: NOT REACHABLE")

def check_registry():
    print(f"Checking registry at {REGISTRY_PATH}...")
    if not os.path.exists(REGISTRY_PATH):
        print("  REGISTRY NOT FOUND")
        return
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)
    base = os.path.join(os.path.dirname(REGISTRY_PATH), "workflows")
    for name, meta in reg.items():
        wf_path = os.path.join(base, meta["file"])
        exists = os.path.exists(wf_path)
        inputs = len(meta.get("inputs", []))
        print(f"  [{name}] file={'OK' if exists else 'MISSING'} inputs={inputs}")

if __name__ == "__main__":
    check_comfy()
    check_registry()
