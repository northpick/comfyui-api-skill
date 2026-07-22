"""Inspect a workflow JSON: list nodes by class_type with key inputs."""
import json, sys, argparse
from pathlib import Path

def inspect(wf_path):
    with open(wf_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    prompt = data.get("prompt", data)

    print(f"\n=== {'='*40}")
    print(f"Workflow: {Path(wf_path).name}")
    print(f"Nodes: {len(prompt)}")
    print(f"{'='*50}")

    for k in sorted(prompt.keys(), key=lambda x: int(x) if x.isdigit() else 9999):
        node = prompt[k]
        ct = node.get("class_type", "?")
        ins = node.get("inputs", {})

        if ct in ("EmptyLatentImage", "EmptySD3LatentImage"):
            print(f"  [{k:>4}] {ct}")
            print(f"          size: {ins.get('width')}x{ins.get('height')} batch={ins.get('batch_size','?')}")
        elif ct == "CLIPTextEncode":
            text = str(ins.get("text", ""))
            print(f"  [{k:>4}] {ct} -> \"{text[:60]}{'...' if len(text)>60 else ''}\"")
        elif ct == "KSampler":
            print(f"  [{k:>4}] {ct} -> steps={ins.get('steps')} cfg={ins.get('cfg')} seed={ins.get('seed')}")
        elif ct in ("VAEDecode", "VAEEncode", "SaveImage", "PreviewImage"):
            print(f"  [{k:>4}] {ct}")
        else:
            shows = {kk: vv for kk, vv in ins.items() if isinstance(vv, (str, int, float, bool)) and kk != "images"}
            if shows:
                print(f"  [{k:>4}] {ct} -> {shows}")
            else:
                print(f"  [{k:>4}] {ct}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Workflow JSON path")
    args = parser.parse_args()
    inspect(args.path)
