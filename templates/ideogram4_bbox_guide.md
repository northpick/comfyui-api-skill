# ideogram4 bbox 坐标指南

## 坐标系统

```json
{"type":"obj|text","bbox":[y1,x1,y2,x2],"desc":"..."}
```

- 全部标准化到 **0–1000** 范围（不论图片实际像素）
- `y1` = 上边缘, `x1` = 左边缘, `y2` = 下边缘, `x2` = 右边缘
- `y1 < y2`, `x1 < x2`
- 坐标是**形状相关**的：16:9 图上 `[0, 0, 500, 500]` 是宽矩形，不是正方形

## 常见比例换算

### 16:9 (1536×864) — 最常用

| 列 | y范围 | x范围 | 用途 |
|---|-------|-------|------|
| COL1 | 20–970 | 10–240 | 左侧人物 |
| COL2 | 80–950 | 260–490 | 左侧道具 |
| COL3 | 20–970 | 510–740 | 右侧人物 |
| COL4 | 80–950 | 760–990 | 右侧道具 |
| 底部ID | 935–985 | 300–700 | 角色名 |

计算方法：1000 / 4列 = 250/列，列之间留20间隙。
```
COL1: x1=10,   x2=240  (宽230)
间隙:   240-260
COL2: x1=260,  x2=490  (宽230)
间隙:   490-510
COL3: x1=510,  x2=740  (宽230)
间隙:   740-760
COL4: x1=760,  x2=990  (宽230)
```

### 1:1 (1024×1024) — 单角色正方形

| 区域 | y范围 | x范围 |
|------|-------|-------|
| 角色 | 20–980 | 20–980 |

### 9:16 (864×1536) — 竖版海报

竖分3段：
```
上段:    20–330
中段:   370–680
下段:   720–980
```

## ⚠️ 常见错误

1. **列重叠**：COL1 和 COL3 的 x 范围必须不同
   - 正确：COL1 x=10-240, COL3 x=510-740
   - 错误：COL1 x=10-240, COL3 x=10-240 （重叠！）
2. **道具列太宽**：道具列 x 范围应和人物列一样窄（230左右）
   - 错误：COL2 x=80-920 （占了全宽！）
3. **y1 > y2**：违反规范，框会乱
4. **人物 vs 童眸差异不够**：必须在 desc 中明确强调区别
   - 常态：苍白、黑眼圈、疤痕、破衣、脏围巾、疲惫表情
   - 童眸：红润脸颊、雀斑、闪亮糖霜发、干净衣、鲜艳围巾、好奇表情

## JSON骨架模板

```python
cap = {
    'aspect_ratio': '16:9',
    'high_level_description': '...',
    'compositional_deconstruction': {
        'background': 'Pure white background, no environment, no props, no logo, no watermark.',
        'elements': [
            {
                'type': 'obj',
                'bbox': [20, 10, 970, 240],
                'desc': 'COLUMN 1: ...'
            },
            {
                'type': 'obj',
                'bbox': [80, 260, 950, 490],
                'desc': 'COLUMN 2: ...'
            },
            {
                'type': 'obj',
                'bbox': [20, 510, 970, 740],
                'desc': 'COLUMN 3: ...'
            },
            {
                'type': 'obj',
                'bbox': [80, 760, 950, 990],
                'desc': 'COLUMN 4: ...'
            },
            {
                'type': 'text',
                'bbox': [935, 300, 985, 700],
                'text': '...',
                'desc': '...'
            }
        ]
    }
}
```

## 提交流程

```python
from gen import submit
import json

r = submit('ideogram4', [
    {'nodeId': '10', 'fieldName': 'value', 'fieldValue': json.dumps(cap, separators=(',',':'), ensure_ascii=False)},
    {'nodeId': '696', 'fieldName': 'value', 'fieldValue': 1536},  # 宽
    {'nodeId': '697', 'fieldName': 'value', 'fieldValue': 864},   # 高
], output_name='output_name')
```
