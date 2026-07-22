---
name: comfyui-api
description: Execute ComfyUI image generation via a service-oriented POST /prompt_workflow API.
  Workflows are registered in registry.json — no hardcoded node IDs.
  Use when user says "comfyui-api" / "generate image" / "text to image" / "ComfyUI" /
  or needs ComfyUI image generation, workflow execution, or automated rendering.
  Covers workflow registry, prompt_workflow API, node parameter injection, image upload, and output retrieval.
---

# ComfyUI Workflow API Skill

Base directory: `C:\Users\Lenovo.LAPTOP-HPKIE7PL\.config\opencode\skills\comfyui-api-skill`

## Architecture

```
User/Agent
  ↓ 1. upload("photo.png")             ← images must be uploaded FIRST
  ↓ 2. POST /prompt_workflow { workflowName, nodeInfoList }
ComfyUI Workflow API
  ├── server.py     — FastAPI entry point
  ├── router.py     — request routing
  ├── executor.py   — core: load registry → patch nodes → submit → wait → copy
  ├── gen.py        — Python entry: submit(), upload(), available()
  └── registry.json — workflow metadata (nodeId × fieldName mapping)
  ↓ POST /prompt
ComfyUI (port 8184)
```

## Quick Start

```python
import sys
sys.path.insert(0, r"C:\Users\Lenovo.LAPTOP-HPKIE7PL\.config\opencode\skills\comfyui-api-skill\scripts")
from gen import submit, upload, available
```

## ⚠️ Image-Based Workflows Require Upload First

Workflows that take **reference images** (`multi_ref`, `storyboard`, `ltx23_i2v`, `rmbg_nocrop`, `rmbg_crop`) need the image file in ComfyUI's `input/` directory. Call `upload()` before `submit()`:

```python
upload(r"photo.png", "photo.png")          # must upload first
submit("multi_ref", [                       # then submit
    {"nodeId": "129", "fieldName": "image", "fieldValue": "photo.png"},
])
```

## ⚠️ Size Must Be Set Explicitly

Most image workflows default sizes to `0` — you must provide `width` and `height`. Values must be divisible by 128.

```python
submit("flux", [
    {"nodeId": "693:129", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "693:129", "fieldName": "height", "fieldValue": 1024},
])
```

Exception: `ideogram4` and `rmbg_*` workflows don't need dimension inputs.

## Core API

### `POST /prompt_workflow`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflowName` | string | **yes** | Workflow name from registry.json |
| `nodeInfoList` | array | no | `[{nodeId, fieldName, fieldValue}]` |
| `output_name` | string | no | Output filename (auto-generated if omitted) |
| `timeout_min` | int | no | Max wait time (default 8) |

Returns:
```json
{ "status": "ok", "outputs": ["outputs/result.png"] }
```

### `POST /upload_image`

**Must be called first** for workflows requiring reference images.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filepath` | string | **yes** | Local path to image file |
| `name` | string | no | Target filename in ComfyUI input dir (basename if omitted) |

### `GET /workflows`

List registered workflows with their available inputs and types.

### `GET /health`

Simple health check.

## Available Workflows

| Name | Type | Description | Speed |
|------|------|-------------|-------|
| `ideogram4` | text-to-image | **画像質最高**，接近闭源顶级水平。纯文生图默认首选。结构化JSON caption。不支持图生图 | 中速（~30s） |
| `qwen` | text-to-image | 真实感最强，细节丰富，中文理解好 | 5-8min |
| `flux` | text-to-image | 速度快，性价比高 | 3-5min |
| `z_image` | text-to-image | 通用真实感，无LoRA | 2-4min |
| `qwen_single` | image-to-image | **Qwen图生图（单图参考）**，根据参考图+prompt编辑生成 | 4-6min |
| `qwen_dual` | image-to-image | **Qwen图生图（双图参考）**，两张参考图融合 | 4-6min |
| `qwen_triple` | image-to-image | **Qwen图生图（三图参考）**，三张参考图融合 | 4-6min |
| `storyboard` | image-to-image | 双场景分镜，正面+负面提示词 | 5-8min |
| `ltx23_i2v` | image-to-video | LTX 2.3 首尾帧图生视频 | 2-5min |
| `rmbg_nocrop` | image-to-image | **移除背景**，保持原图尺寸。RMBG-2.0。输出RGBA | 10-30s |
| `rmbg_crop` | image-to-image | **移除背景+裁剪透明边缘**。RMBG-2.0+CropByMask | 10-30s |
| `music` | text-to-music | ACE-Step AI音乐生成 | 1-3min |

---

## Text-to-Image Workflows

### ideogram4 — 最高质量，结构化JSON（纯文生图首选）

**不支持图生图。** 必须传入结构化JSON caption（纯文本会触发安全过滤）。

> ⚠️ **默认工作流**：`ideogram4` 是纯文生图的**默认推荐**，画像質最高、接近闭源顶级水平。所有纯文本→图片的场景（角色参考图、场景四宫格、道具三视图等）优先使用此 workflow。

```python
import sys, json
sys.path.insert(0, r"C:\Users\Lenovo.LAPTOP-HPKIE7PL\.config\opencode\skills\comfyui-api-skill\scripts")
from gen import submit

caption = {
    "high_level_description": "A medium-shot photograph of a barista pouring latte art in a cozy cafe.",
    "style_description": {
        "aesthetics": "warm, inviting, soft",
        "lighting": "warm golden hour sunlight streaming through windows",
        "photo": "shallow depth of field, 50mm, f/1.8",
        "medium": "photograph",
        "color_palette": ["#D4A574", "#F5E6D3", "#8B5E3C", "#2C1810", "#C4A882"]
    },
    "compositional_deconstruction": {
        "background": "A warmly lit cafe interior with wooden shelves, plants, and soft ambient glow from pendant lights.",
        "elements": [
            {"type": "obj", "desc": "A barista with rolled-up sleeves, hands steady, pouring steamed milk into a ceramic cup, creating a rosetta pattern."}
        ]
    }
}

submit("ideogram4", [
    {"nodeId": "10", "fieldName": "value", "fieldValue": json.dumps(caption, separators=(",", ":"), ensure_ascii=False)},
    {"nodeId": "696", "fieldName": "value", "fieldValue": 1024},
    {"nodeId": "697", "fieldName": "value", "fieldValue": 1024},
], output_name="my_ideogram4")
```

注意：
- 尺寸自动对齐到16的倍数（最小256）
- **分辨率策略**：简单内容图（单角色/场景/道具）→ 1024×576；复杂内容图（身份板/展板/多宫格）→ **1536×864**
- 无单独负面提示词（内部用ConditioningZeroOut）

### qwen — 真实感最强

```python
submit("qwen", [
    {"nodeId": "9", "fieldName": "text", "fieldValue": "a beautiful landscape with mountains and a lake at sunset, vibrant colors, highly detailed"},
    {"nodeId": "29", "fieldName": "text", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
], output_name="my_qwen")
```

### flux — 速度快

```python
submit("flux", [
    {"nodeId": "693:135", "fieldName": "text", "fieldValue": "a cyberpunk cat with neon fur and glowing eyes, sitting on a rainy street at night"},
    {"nodeId": "96", "fieldName": "text", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
    {"nodeId": "693:129", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "693:129", "fieldName": "height", "fieldValue": 1024},
], output_name="my_flux")
```

### z_image — 最快，无LoRA

```python
submit("z_image", [
    {"nodeId": "11", "fieldName": "text", "fieldValue": "a cute dog sitting in a field of flowers, digital painting style"},
    {"nodeId": "17", "fieldName": "text", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
    {"nodeId": "13", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "13", "fieldName": "height", "fieldValue": 1024},
], output_name="my_zimage")
```

---

## Image-to-Image Workflows

> **智能选择**：在脚本中可根据参考图数量自动选择 workflow：0张→`ideogram4`，1张→`qwen_single`，2张→`qwen_dual`，3张→`qwen_triple`。

### qwen_single — 单图参考编辑

1张参考图，根据参考图内容和prompt生成新图。

```python
upload(r"character.png", "character.png")

submit("qwen_single", [
    {"nodeId": "111", "fieldName": "prompt", "fieldValue": "a young woman in a red dress standing in a sunlit garden, smiling warmly"},
    {"nodeId": "138", "fieldName": "prompt", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
    {"nodeId": "112", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "112", "fieldName": "height", "fieldValue": 1024},
    {"nodeId": "129", "fieldName": "image", "fieldValue": "character.png"},
])
```

### qwen_dual — 双图参考融合

2张参考图，融合两者特征生成。

```python
upload(r"person.png", "person.png")
upload(r"product.png", "product.png")

submit("qwen_dual", [
    {"nodeId": "111", "fieldName": "prompt", "fieldValue": "a person holding a product in a sunlit room, smiling naturally"},
    {"nodeId": "138", "fieldName": "prompt", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
    {"nodeId": "112", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "112", "fieldName": "height", "fieldValue": 1024},
    {"nodeId": "129", "fieldName": "image", "fieldValue": "person.png"},
    {"nodeId": "130", "fieldName": "image", "fieldValue": "product.png"},
])
```

### qwen_triple — 三图参考融合

3张参考图融合，保持角色/场景元素一致性。

```python
upload(r"person.png", "person.png")
upload(r"product.png", "product.png")
upload(r"scene.png", "scene.png")

submit("qwen_triple", [
    {"nodeId": "111", "fieldName": "prompt", "fieldValue": "a person standing in a sunlit room holding a product, smiling naturally, warm atmosphere"},
    {"nodeId": "138", "fieldName": "prompt", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed"},
    {"nodeId": "112", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "112", "fieldName": "height", "fieldValue": 1024},
    {"nodeId": "129", "fieldName": "image", "fieldValue": "person.png"},
    {"nodeId": "130", "fieldName": "image", "fieldValue": "product.png"},
    {"nodeId": "135", "fieldName": "image", "fieldValue": "scene.png"},
])
```

---

## Background Removal Workflows

Both use **RMBG-2.0** model. Upload image first, then submit.

### rmbg_nocrop — 去背不裁剪

移除背景，保留原始图片尺寸。输出**RGBA PNG**（带透明通道）。

```python
upload(r"character.png", "character.png")

submit("rmbg_nocrop", [
    {"nodeId": "6", "fieldName": "image", "fieldValue": "character.png"},
], output_name="character_alpha")
```

### rmbg_crop — 去背并裁剪

移除背景后自动裁剪透明边缘（保留20px边距，对齐到8px）。

```python
upload(r"character.png", "character.png")

submit("rmbg_crop", [
    {"nodeId": "6", "fieldName": "image", "fieldValue": "character.png"},
], output_name="character_cropped")
```

注意：
- 裁剪版(`rmbg_crop`)内部经过CropByMask节点，透明信息可能丢失
- 如需保留alpha，使用`rmbg_nocrop`后再手动裁剪
- 两工作流均不需要传尺寸参数

---

## Image-to-Video

### ltx23_i2v — 图生视频（首尾帧）

需先upload首帧和尾帧两张参考图。提示词要求（LTX-2官方风格）：
- 聚焦详细、按时间顺序的动作和场景描述
- 单个流畅段落，直接以动作开头，控制在200词以内

```python
upload(r"start_frame.png", "start.png")
upload(r"end_frame.png", "end.png")

submit("ltx23_i2v", [
    {"nodeId": "468:364", "fieldName": "text", "fieldValue": "A woman in a flowing red dress walks confidently down a dimly lit city street at night, her heels clicking on the wet pavement. Rain begins to fall, catching the glow of neon signs. The camera slowly dollies in as she turns and looks over her shoulder."},
    {"nodeId": "468:374", "fieldName": "text", "fieldValue": "blurry, low quality, bad anatomy, watermark, text, signature, ugly, deformed, static, no motion"},
    {"nodeId": "468:362", "fieldName": "value", "fieldValue": 24},
    {"nodeId": "468:363", "fieldName": "value", "fieldValue": 5},
    {"nodeId": "457", "fieldName": "image", "fieldValue": "start.png"},
    {"nodeId": "458", "fieldName": "image", "fieldValue": "end.png"},
], output_name="my_video")
```

帧率和时长决定总帧数：`总帧数 = 时长 × 帧率 + 1`。输出视频FPS自动翻倍（默认48fps）。

---

## Music Generation

### music — AI音乐生成

**必须始终提供 `lyrics`**（工作流有默认歌词示例，需覆盖）：

| 场景 | lyrics值 | 说明 |
|------|---------|------|
| 纯音乐 | `""` | 空字串 |
| 有歌词 | 完整歌词 | 时长与歌词量需匹配 |

歌词长度参考：
- 30秒 → 1段Verse + 1段Chorus（约4-8行）
- 60秒 → 2段Verse + 2段Chorus + Bridge（约12-20行）
- 120秒 → 完整结构（约20-40行）

```python
submit("music", [
    {"nodeId": "94", "fieldName": "tags", "fieldValue": "nostalgic piano lullaby, soft warm tones, gentle melody, ambient, emotional"},
    {"nodeId": "94", "fieldName": "lyrics", "fieldValue": "Sleep little one, the night is deep\nMemories we vow to keep\nThe stars will guide you through the dark\nUntil the morning leaves its mark"},
    {"nodeId": "94", "fieldName": "bpm", "fieldValue": 70},
    {"nodeId": "94", "fieldName": "keyscale", "fieldValue": "F major"},
    {"nodeId": "111", "fieldName": "value", "fieldValue": 30},
], output_name="my_lullaby")
```

**keyscale 调性参考：**

| 大调 | 小调 |
|------|------|
| C major, C# major, Db major, D major | C minor, C# minor, Db minor, D minor |
| D# major, Eb major, E major, F major | D# minor, Eb minor, E minor, F minor |
| F# major, Gb major, G major, G# major | F# minor, Gb minor, G minor, G# minor |
| Ab major, A major, A# major, Bb major | Ab minor, A minor, A# minor, Bb minor |
| B major | B minor |

默认：`C major`

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `Unknown workflow` | Run `GET /workflows` for available names |
| ComfyUI not reachable | Is ComfyUI running on port 8184? |
| Timeout | Increase `timeout_min` (FLUX ~5min, Qwen ~8min) |
| Node not found | Does `registry.json` have the correct `nodeId`? |
| Image not found | Did you call `upload()` before submitting? File in ComfyUI `input/`? |
| Output missing | Check `executor.py` → `COMFY_OUTPUT` path |

## File Layout

```
comfyui-api-skill/
├── SKILL.md                   # This file
├── REFERENCE.md               # Detailed reference
├── registry.json              # Workflow registry (nodeId mappings)
├── scripts/
│   ├── server.py              # FastAPI server
│   ├── router.py              # Request routing
│   ├── executor.py            # Core: upload → load → patch → submit → wait → copy
│   ├── gen.py                 # Python entry: submit(), upload(), available()
│   ├── api_check.py           # Health & registry checker
│   └── inspect_wf.py          # Workflow node inspector
└── workflows/                 # ComfyUI workflow JSON files
    ├── Ideogram4.json
    ├── FLUX 2 Klein 9B.json
    ├── Qwen文本生图.json
    ├── z-image.json
    ├── 多图参考.json
    ├── 分镜 api.json
    ├── LTX2.3首尾帧.json
    ├── 抠图不裁剪.json
    ├── 抠图裁剪.json
    └── ACE-Step-音乐新版.json
```
