# ComfyUI Workflow API Skill

这是一个 **opencode / AI 智能体技能包**，让你的 AI 助手（opencode、Cursor 等）具备通过 API 调用 ComfyUI 工作流的能力。

把它所在目录交给 AI 后，AI 会自动理解：
- 怎么连接你的 ComfyUI
- 有哪些工作流可用
- 每个工作流需要什么参数
- 需不需要先上传图片

---

## 这东西是干嘛的

你在 ComfyUI 里拖了一堆节点，搭了很棒的工作流。但每次生成都要打开网页、拖图、改参数，烦。

这个 skill 让 **AI 替你干这些事**——你只需要对 AI 说一句"给这个角色去个背景"或者"生成一张场景概念图"，AI 就会自动调 ComfyUI 帮你完成。

---

## 你需要做什么

### 1. 确保 ComfyUI 在运行

启动 ComfyUI，确保 `http://127.0.0.1:8184` 能访问（端口可以在 `scripts/executor.py` 里改）。

### 2. 把这个目录交给 AI

把 `comfyui-api-skill` 整个文件夹放进你的项目，或者告诉 AI 这个路径，AI 读 `SKILL.md` 后就知道怎么用了。

### 3. （可选）启动 API 服务

如果 AI 支持 HTTP 调用，可以启动 FastAPI 服务：

```bash
cd comfyui-api-skill
pip install fastapi uvicorn requests pydantic
uvicorn scripts.server:app --host 127.0.0.1 --port 8000
```

不启动也行，AI 可以直接通过 Python import 调用。

---

## 使用示例

**对 AI 说：**
> "用 flux 生成一张赛博朋克猫，1024x1024"

AI 会自动执行：

```python
from gen import submit
submit("flux", [
    {"nodeId": "693:135", "fieldName": "text", "fieldValue": "a cyberpunk cat with neon fur"},
    {"nodeId": "96", "fieldName": "text", "fieldValue": "blurry, low quality"},
    {"nodeId": "693:129", "fieldName": "width", "fieldValue": 1024},
    {"nodeId": "693:129", "fieldName": "height", "fieldValue": 1024},
])
```

**对 AI 说：**
> "把 character.png 去背景"

AI 会自动先上传再提交：

```python
from gen import submit, upload
upload("character.png")
submit("rmbg_nocrop", [
    {"nodeId": "6", "fieldName": "image", "fieldValue": "character.png"},
])
```

结果会输出到 `outputs/` 目录，同时生成一个 `.json` 文件记录本次生成参数。

---

## 内置工作流参考

以下工作流已注册在 `registry.json` 中，AI 可以直接使用。但注意：**workflows/ 里的 JSON 来源于用户自己的 ComfyUI 环境和自定义节点，不一定能直接在你的 ComfyUI 上跑通**。建议改成你自己导出工作流（见下文）。

| 名称 | 类别 | 说明 |
|------|------|------|
| `ideogram4` | 文本生图 | 画质最高，需要传结构化 JSON caption |
| `qwen` | 文本生图 | 真实感强，中文理解好 |
| `flux` | 文本生图 | 速度快 |
| `z_image` | 文本生图 | 最快文生图 |
| `qwen_single` | 图生图 | 单图参考编辑 |
| `qwen_dual` | 图生图 | 双图融合 |
| `qwen_triple` | 图生图 | 三图融合 |
| `storyboard` | 图生图 | 双场景分镜 |
| `rmbg_nocrop` | 去背景 | 去背保持原尺寸（RGBA） |
| `rmbg_crop` | 去背景 | 去背并裁剪透明边缘 |
| `ltx23_i2v` | 图生视频 | 首尾帧视频 |
| `ltx_director` | 视频 | 时间线导演台 |
| `bernini` | 图生视频 | 最慢但效果最好 |
| `video_to_frames*` | 视频 | 拆帧（可选去背景） |
| `music` | 音乐生成 | ACE-Step |
| `stable_audio_3` | 音频生成 | 音效/音乐 |

---

## 注册你自己的 ComfyUI 工作流

`workflows/` 里的 JSON 文件只是示例（来源：用户自己在 ComfyUI 中搭建并导出的工作流）。**你需要导出你自己的工作流**，才能在你的 ComfyUI 上正常运行。

### 步骤

#### 1. 在 ComfyUI 中搭好工作流并导出 API 格式

在 ComfyUI 中：
1. 点击右上角 ⚙ → **Enable Dev Mode Options**
2. 菜单 → **Save (API Format)**，导出 API 格式 JSON

API 格式是 ComfyUI 专门为程序调用设计的格式，只保留节点类型和连接信息，不带画布布局数据。

> 分不清 API 格式和普通格式？不知道在哪导出？上网搜 **"ComfyUI export API format"**，一堆教程和截图。

#### 2. 找出要控制的节点 ID

打开导出的 JSON，结构像这样：

```json
{
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "a cat",
      "clip": ["4", 1]
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": { "seed": 123456, "steps": 20, "cfg": 7 }
  }
}
```

每个数字 key 就是节点 ID。找到你希望 AI 能修改的节点——比如正面提示词节点（通常是 CLIPTextEncode）、尺寸节点（EmptyLatentImage）、图片输入节点（LoadImage）等，记下它们的 nodeId 和字段名。

#### 3. 复制 JSON 到 workflows/ 目录

```bash
cp your_workflow.json comfyui-api-skill/workflows/
```

#### 4. 在 registry.json 中注册

加一条记录，告诉 AI 这个工作流叫什么名字、有哪些参数可以改：

```json
{
  "my_workflow": {
    "file": "my_workflow.json",
    "display": "我的工作流",
    "description": "一句话说清楚干啥用的",
    "inputs": [
      { "nodeId": "6", "fieldName": "text", "label": "正面提示词", "type": "string" },
      { "nodeId": "7", "fieldName": "text", "label": "负面提示词", "type": "string" },
      { "nodeId": "5", "fieldName": "width", "label": "宽度", "type": "int", "default": 1024 },
      { "nodeId": "5", "fieldName": "height", "label": "高度", "type": "int", "default": 1024 }
    ],
    "output_node": "9"
  }
}
```

> 不知道字段类型填什么？不确定 nodeId 是哪个？**直接把这些交给 AI——让它读你的 JSON、分析节点、帮你写好 registry 条目**。你只需要说"把我导出的这个工作流注册进去"。

#### 5. 告诉 AI 新增了工作流

重启服务或直接告诉 AI 工作流名称即可使用。

---

## 工作流名称约定（AI 会参考）

你在 `registry.json` 注册的工作流名称（key）AI 会优先使用：

- 纯文生图：用 `ideogram4` 或 `flux` 这类
- 图生图（需要参考图）：用 `qwen_single` 等，AI 会自动先调 `upload()`
- 图生视频：同理会先上传再提交

AI 会根据注册信息中的 `type: "image"` 字段自动判断是否需要先上传图片。

---

## 给 AI 用时的提示词参考

你可以直接对 AI 这样说：

> "用 comfyui-api-skill，帮我生成..."
> "调用 rmbg_nocrop 把这张图去背景"
> "执行 flux 工作流生成一张 1024x1024 的..."
> "我用 ComfyUI 搭了一个工作流在 workflows/ 里，帮我注册到 registry 里"

AI 读了这个 skill 就知道怎么做了。

---

## 目录结构

```
comfyui-api-skill/
├── SKILL.md              ← AI 读的说明书（最重要的文件）
├── README.md             ← 你现在看的（人类说明书）
├── REFERENCE.md          ← 参数参考
├── registry.json         ← 工作流注册表（AI 靠这个知道有哪些工作流）
├── scripts/
│   ├── server.py         ← FastAPI 服务
│   ├── executor.py       ← 核心引擎：提交/轮询/拷贝
│   ├── gen.py            ← Python 入口：submit() / upload() / available()
│   ├── api_check.py      ← 健康检查工具
│   └── inspect_wf.py     ← 工作流 JSON 检查工具
├── workflows/            ★ 放你的 ComfyUI 工作流 JSON（API 格式）
├── templates/            ← 提示词模板参考
└── outputs/              ← 生成结果存放处
```

---

## 常见问题

| 问题 | 回答 |
|------|------|
| 工作流跑不通 | `workflows/` 里的是示例，需要用你自己的 ComfyUI 导出 API 格式。不知道怎么做？上网搜索 **"ComfyUI export API format workflow"** |
| ComfyUI 连不上 | 确认 ComfyUI 在 `localhost:8184` 运行。端口可以在 `executor.py` 里改 |
| 找不到节点 | `registry.json` 里的 nodeId 要和你 JSON 文件里的 key 一致 |
| 尺寸不对 | 大部分工作流默认尺寸是 0，记得传 width/height，值要能被 128 整除 |
| 图片找不到 | 图生图类工作流必须先用 `upload()` 上传 |
| 超时了 | 大模型生成本来就慢——FLUX 约 5 分钟，Qwen 最多 8 分钟 |
| 不知道参数类型 | 直接在 ComfyUI 里找到对应节点，看 inputs 里是什么类型 |

---

> **不知道 ComfyUI 怎么导出 API 工作流？不知道 API 格式和普通格式的区别？不知道 LoadImage 节点的字段名叫什么？—— 上网搜。关键词示例：`ComfyUI export API format`、`ComfyUI workflow JSON node IDs`、`ComfyUI /prompt API`。网上有大量图文教程和视频。**
