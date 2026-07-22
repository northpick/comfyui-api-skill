# ComfyUI Workflow API — Reference

## Size Rule

All sizes must be explicitly set per task. Values must be **divisible by 128**. Default reference: `1024`.

## Workflow Details

### qwen (Qwen文本生图)

File: `workflows/Qwen文本生图.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `9` | CLIPTextEncode | `text` | **正面提示词** |
| `29` | CLIPTextEncode | `text` | **负面提示词** |
| `24` | EmptySD3LatentImage | `width`/`height` | Output size |
| `12` | KSampler | `seed` | Auto-randomized |
| `28` | Image Save | — | Output node |

### flux (FLUX 2 Klein 9B)

File: `workflows/FLUX 2 Klein 9B.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `693:135` | CLIPTextEncode | `text` | **正面提示词** |
| `96` | CLIPTextEncode | `text` | **负面提示词** |
| `693:129` | EmptyFlux2LatentImage | `width`/`height` | Output size |
| `693:695` | KSampler | `seed` | Auto-randomized |
| `95` | Image Save | — | Output node |

Recommended: ≤300 characters for FLUX prompt.

### qwen_single (qwen单图参考)

File: `workflows/qwen单图参考.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `111` | TextEncodeQwenImageEditPlus | `prompt` | **正面提示词** |
| `138` | TextEncodeQwenImageEditPlus | `prompt` | **负面提示词** |
| `112` | EmptySD3LatentImage | `width`/`height` | Output size |
| `129` | LoadImage | `image` | Reference image 1 |
| `137` | Image Save | — | Output node |

### qwen_dual (qwen双图参考)

File: `workflows/qwen双图参考.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `111` | TextEncodeQwenImageEditPlus | `prompt` | **正面提示词** |
| `138` | TextEncodeQwenImageEditPlus | `prompt` | **负面提示词** |
| `112` | EmptySD3LatentImage | `width`/`height` | Output size |
| `129` | LoadImage | `image` | Reference image 1 |
| `130` | LoadImage | `image` | Reference image 2 |
| `137` | Image Save | — | Output node |

### qwen_triple (qwen三图参考)

File: `workflows/qwen三图参考.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `111` | TextEncodeQwenImageEditPlus | `prompt` | **正面提示词** |
| `138` | TextEncodeQwenImageEditPlus | `prompt` | **负面提示词** |
| `112` | EmptySD3LatentImage | `width`/`height` | Output size |
| `129` | LoadImage | `image` | Reference image 1 |
| `130` | LoadImage | `image` | Reference image 2 |
| `135` | LoadImage | `image` | Reference image 3 |
| `137` | Image Save | — | Output node |

### storyboard (分镜 api)

File: `workflows/分镜 api.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `110` | TextEncodeQwenImageEditPlus | `prompt` | **负面提示词** |
| `111` | TextEncodeQwenImageEditPlus | `prompt` | **正面提示词** |
| `112` | EmptySD3LatentImage | `width`/`height` | Output size |
| `129` | LoadImage | `image` | Reference image 1 |
| `130` | LoadImage | `image` | Reference image 2 |
| `136` | Image Save | — | Output node |

### pixel (z-image_像素)

File: `workflows/z-image_像素.json`

| Node ID | Class Type | Field | Role |
|---------|-----------|-------|------|
| `11` | CLIPTextEncode | `text` | **正面提示词** |
| `17` | CLIPTextEncode | `text` | **负面提示词** |
| `13` | EmptySD3LatentImage | `width`/`height` | Output size |
| `10` | KSampler | `seed` | Auto-randomized |
| `16` | Image Save | — | Output node |

## Prompt Length Limits

| Model | Recommended Max |
|-------|----------------|
| FLUX 9B | 300 characters |
| Qwen | 500 characters |
| Pixel | 200 characters |

## Output Directory

Generated images are saved to `outputs/` under the skill directory, named by `output_name`. Each output has a sidecar `.json` with full generation parameters.

## Registry Format

```json
{
  "workflow_name": {
    "file": "workflow.json",
    "display": "Name",
    "description": "What it does",
    "inputs": [
      {
        "nodeId": "string",
        "fieldName": "string",
        "label": "标签",
        "type": "string|int|image",
        "default": 0
      }
    ],
    "output_node": "string"
  }
}
```

## API Error Codes

| HTTP | Meaning |
|------|---------|
| 400 | Bad request: unknown workflow, missing node, timeout, ComfyUI error |
| 422 | Validation error (malformed request body) |
| 500 | Internal server error |
