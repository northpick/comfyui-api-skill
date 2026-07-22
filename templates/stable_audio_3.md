## 一、正面描述 (Positive prompt)

正面描述是告诉模型你**想要**生成什么样的声音，是生成的核心输入。Stable Audio 3 的训练数据来自 Freesound 和 AudioSparx 等平台及其元数据，因此**描述得越详细、越接近这些数据集的标注风格，效果通常越好**。

### 1. 通用写作技巧

- **详细优于简短**：更多的细节通常带来更好的结果。
- **设定合理的时长**：模型的生成时长应与描述内容相匹配。
- **拥抱随机性**：每次生成结果都不同，如需复现可设置 `seed` 参数。
- **不知道怎么写时**：可以先用空提示词（无提示词）生成找灵感，或使用 Gradio 的提示词助手。

### 2. 音乐生成 (Music) 的正面描述写法

音乐生成应包含以下核心要素：

| 要素 | 说明 | 示例 |
|------|------|------|
| **风格/流派 (Genre)** | 音乐的风格类型 | "House music", "Synthpop", "Tech-house" |
| **乐器 (Instruments)** | 用了什么乐器，音色如何 | "pumping four-to-the-floor kick", "808 bass", "gospel house piano" |
| **情绪/氛围 (Mood & Energy)** | 表达什么情感 | "euphoric feeling", "dreamy", "hopeful" |
| **速度 (BPM)** | 指定节奏 | "124 BPM" |

**完整示例**：

> *"A triumphant and stylish UK bass-flavoured tech-house tune that evokes feelings of the last tune played in a DJ set. The pumping four-to-the-floor kick is supported by an 808 bass that is syncopated. There are gliding emotional synth leads that build sections to their climax. Playful stabs and chops support the rhythm of the drums in sections. There is a beautiful gospel house piano that plays in the drop, giving the track a euphoric feeling."*

> *"House music that encapsulates the feeling of being at a festival in the sunny weather with all your friends 124 BPM"*

> *"A dream-like Synthpop instrumental that would accompany a dream-sequence in a surrealist movie 120 BPM"*

### 3. 音效 (SFX / Audio Samples) 的正面描述写法

音效生成应描述声音的具体特征和场景：

**示例**：

> *"A cinematic piano and string sketch with gentle pulses, hopeful harmony, and spacious reverb."*

> *"A hopeful cinematic piano piece that slowly opens into strings and subtle electronic percussion. Keep the character smooth, warm, and believable."*

> *"Extend the source with glitchy lullaby beat with kalimba, soft 808, tape wow, and crystalline pad tails then add a clear new phrase without vocals."*

---

## 二、负面提示词 (Negative prompt)

负面提示词是用来告诉模型你**不想要**什么样的声音特征，引导生成过程避开你不希望出现的品质。使用负面提示词可以**显著提高生成音频的质量**。

### 1. 基本用法

在代码中通过 `negative_prompt` 参数传入：

```python
from stable_audio_3 import StableAudioModel
model = StableAudioModel.from_pretrained("medium")
audio = model.generate(
    prompt="120 BPM house loop",
    negative_prompt="poor quality",  # 负面提示词
    duration=30,
    steps=8,
    cfg_scale=1
)
```

### 2. 常用负面提示词示例

| 场景 | 负面提示词示例 |
|------|----------------|
| **通用质量** | `"low quality, average quality"` |
| **音质问题** | `"poor quality, distorted, clipping, noisy"` |
| **不想要的风格** | `"no vocals"`（用于纯音乐生成时避免人声） |
| **避免杂乱** | `"muddy, messy, overcompressed"` |

### 3. 使用建议

- 负面提示词是**可选的**，不是必须填写的。
- 描述越具体，避开效果越好。例如不只是说 "bad"，而是说 `"distorted, clipping, noisy, low fidelity"`。
- 对于音乐生成，如果只想要纯乐器，可以添加 `"no vocals, no singing"`。
- 在某些实现中，模型可能不强制要求负面提示词，但主动使用通常能提升质量。

---

## 三、时长控制

时长通过节点 74（PrimitiveFloat）控制，单位为秒。建议值：
- **音效 / 短乐句**：5-15 秒
- **音乐片段**：15-60 秒
- **完整曲目**：60-180 秒

注意生成的时长应与描述内容的丰富程度相匹配。
