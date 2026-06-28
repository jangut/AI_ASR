# SpeechNote 项目知识库

## 一句话

SpeechNote 是一个本地 AI 语音笔记软件，将麦克风语音实时转换为结构化 Markdown 笔记，采用事件驱动、Pipeline 流水线架构。

---

## 技术栈

```
语言：Python 3.14
ASR：FunASR + SenseVoiceSmall（CPU 推理）
音频：sounddevice + numpy
GUI：PySide6（Qt6 for Python）
数据：dataclass + SQLite（以后）
```

---

## 架构总览

```
┌──────────────────────────────────────────────────────┐
│                   PySide6 GUI                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  实时字幕（最新一句高亮，自动滚动）              │  │
│  ├────────────────────────────────────────────────┤  │
│  │  历史笔记（所有已输出的 Sentence）               │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  状态栏：🔴 录音中 | VAD | 麦克风 | 00:23     │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                │ 订阅 EventBus
                ▼
┌──────────────────────────────────────────────────────┐
│                   Python 后端                          │
│                                                       │
│  Microphone                                           │
│      │                                                │
│      ▼                                                │
│  RingBuffer          ← 100ms 一帧                     │
│      │                                                │
│      ▼                                                │
│  ASRWorker           ← 缓存/VAD/窗口调度              │
│      │                                                │
│      ▼                                                │
│  SenseVoice          ← FunASR CPU 推理                │
│      │                                                │
│      ▼                                                │
│  CorrectorPipeline   ← 责任链处理                     │
│      │                                                │
│      ▼                                                │
│  EventBus ────────── → Plugins + GUI                  │
└──────────────────────────────────────────────────────┘
```

---

## GUI 界面设计

```
┌─────────────────────────────────────────────────────────┐
│  🎤  SpeechNote  v0.3                   📌  —  □  ×  │
├─────────┬───────────────────────────────────────────────┤
│         │                                               │
│  📝     │  ┌─────────────────────────────────────────┐  │
│  输出    │  │  🎯 正在识别...                         │  │
│         │  │                                          │  │
│         │  │  摘一颗苹果等你从门前经过                 │  │  ← 最新一句（高亮）
│         │  │  ─────────────────────────────────────  │  │
│         │  │                                          │  │
│         │  │  - 摘一颗苹果等你从门前经过              │  │
│  ⚙️     │  │  - 收到你的手中帮你解渴                  │  │  ← 历史记录
│  设置    │  │  - 天的夏天的可乐像冬天的可可            │  │
│         │  │  - 你是对的时间对的角色                  │  │
│         │  │  - 已经约定好一起过下个周末              │  │  ← 实时更新
│  ❓     │  │  - ...                                   │  │
│  帮助    │  └─────────────────────────────────────────┘  │
│         │                                               │
│         │                                               │
├─────────┴───────────────────────────────────────────────┤
│  🔴 录音中  │  VAD 模式  │  来源: 麦克风  │  00:23  │
│  ⏸ 暂停    ⏹ 停止                                    │
└─────────────────────────────────────────────────────────┘
```

### 布局说明

| 区域 | 内容 |
| --- | --- |
| **标题栏** | 🎤 SpeechNote v0.3 + 窗口控制（最小化/最大化/关闭） |
| **左侧边栏** | 📝 输出  /  ⚙️ 设置  /  ❓ 帮助（三个 Tab） |
| **主区域（上）** | 实时字幕，最新一句高亮，自动滚动 |
| **主区域（下）** | 历史笔记，累积所有已输出的 Sentence |
| **状态栏** | 录音状态 🔴/⏸  | 模式 VAD/Window | 来源 麦克风 | 时长 |
| **控制区** | ⏸ 暂停  ⏹ 停止（快捷键支持） |

### 快捷键（初版）

| 快捷键 | 动作 |
| --- | --- |
| `Ctrl+R` | 开始 / 暂停录音 |
| `Ctrl+Shift+R` | 停止录音 |
| `Ctrl+E` | 导出当前笔记 |
| `Ctrl+,` | 打开设置 |
| `Ctrl+K` | 清空当前字幕 |

---

## 核心设计决策

### 1. PySide6 直连 EventBus（不分开跑）

Python 后端和 GUI 在同一个进程内，EventBus 的信号直接连 Qt 信号槽，零 IPC，零延迟。

```
EventBus.emit(SENTENCE)
    │
    ▼
GUI.on_sentence(sentence)
    │
    ▼
QTextEdit.append(sentence.text)
```

优点：
- 砍掉通信协议（不需要 JSON/stdout/QProcess）
- 实时性最好，广播即到
- 不需要写 StdoutPlugin
- AGENTS.md 少写三页文档
- Python 改代码 → 重启即生效，不用跨语言调试

### 2. Config 配置驱动

所有参数集中在 config.py，Qt 设置界面可遍历字段自动生成表单：

```python
@dataclass(slots=True, frozen=True)
class Config:
    app_name: str = "SpeechNote"
    version: str = "0.3.0"
    sample_rate: int = 16000
    channels: int = 1
    block_size: int = 1600
    model_dir: str = r"C:\...\damo\SenseVoiceSmall"
    device: str = "cpu"
    mode: str = "vad"                    # "vad" | "window"
    recognize_window: float = 4.0
    overlap_window: float = 1.0
    enable_vad: bool = True
    vad_threshold: float = 0.005
    silence_timeout: float = 0.5
    # hotwords: list[str] = field(default_factory=list)  # 以后
```

### 3. assert 消除 Optional

生命周期初始化完成后，成员理论上绝不 None：

```python
def start(self):
    assert self._recognizer is not None
    assert self._worker is not None
    assert self._recorder is not None
```

此后 IDE 类型自动收窄为具体类型。

### 4. CorrectorPipeline（责任链）

```python
self._pipeline = CorrectorPipeline([
    DuplicateCorrector(),
    # DictionaryCorrector(hotwords=["SpeechNote"]),  # 待做
    # LLMCorrector(),                                 # 待做
])
```

Worker 零改动，Recognizer 零改动。

### 5. 双模式识别

| 模式 | 行为 | 适合场景 |
| --- | --- | --- |
| `mode = "vad"`（默认） | VAD 检测到静音 0.5s 即 flush，无重叠 | 对话、会议、口述 |
| `mode = "window"` | 固定 4s 窗口 + 1s overlap | 安静环境、歌曲、独白 |

Config 一行切换，Worker 自动调整。

---

## 当前功能状态（v0.3 Alpha）

### ✅ 已完成
- [x] Config 配置中心（dataclass, slots=True, frozen=True）
- [x] Application 生命周期管理（init → initialize → start → wait → stop）
- [x] EventBus 事件总线（发布/订阅）
- [x] RingBuffer 线程安全缓存（基于 queue.Queue）
- [x] MicrophoneRecorder（sounddevice，100ms/帧）
- [x] SenseVoiceRecognizer（FunASR，CPU 推理）
- [x] _clean_text() 去除 SenseVoice 标签
- [x] Worker 音频缓存（累计 → 拼接 → 识别）
- [x] Overlap Window（1s，防止切句）
- [x] DuplicateCorrector（后缀-前缀最长匹配去重）
- [x] CorrectorPipeline（责任链，可扩展）
- [x] 能量检测 VAD（RMS 阈值 0.005，零依赖）
- [x] 双模式（vad / window）
- [x] 识别异常保护（try-except 不退出线程）
- [x] MarkdownPlugin 输出到 notes/*.md

### 📋 待做

**v0.4 — Corrector 增强**
- [ ] DictionaryCorrector（热词纠正，编辑距离 ≤ 1）
- [ ] NumberCorrector（"一二三四" → "1234"）
- [ ] PunctuationCorrector（句末自动加标点）

**v0.5 — 体验优化**
- [ ] VAD 阈值自适应
- [ ] GPU 推理支持（修复 CUDA kernel 兼容性）
- [ ] 识别结果合并（同句话片段自动拼接）

**v1.0 — AI 增强**
- [ ] LLMCorrector（大模型上下文纠错）
- [ ] Sentence Accumulator（完整段落累积后发送）

**v2.0 — Qt GUI**
- [ ] PySide6 主窗口布局
- [ ] EventBus → Qt 信号桥接
- [ ] 实时字幕显示 + 历史记录
- [ ] 状态栏 + 控制按钮
- [ ] 快捷键
- [ ] 设置界面（Config 遍历生成表单）
- [ ] 笔记文件浏览器

---

## 目录结构

```
SpeechNote/
├── main.py                  # 入口
├── app.py                   # Application 生命周期
├── config.py                # 全局配置
├── AGENTS.md                # 本文件
├── README.md                # 完整开发路线图
│
├── core/
│   ├── event.py             # EventBus
│   ├── events.py            # 事件类型枚举
│   ├── sentence.py          # 统一数据模型
│   └── logger.py            # 日志
│
├── audio/
│   ├── base.py              # BaseRecorder
│   ├── recorder.py          # MicrophoneRecorder
│   └── ringbuffer.py        # RingBuffer
│
├── asr/
│   ├── base.py              # BaseRecognizer
│   ├── recognizer.py        # FakeRecognizer + SenseVoiceRecognizer
│   └── worker.py            # ASRWorker（核心调度）
│
├── corrector/
│   ├── base.py              # BaseCorrector
│   ├── identity.py          # 直通
│   ├── duplicate.py         # 去重
│   └── pipeline.py          # CorrectorPipeline
│
├── plugins/
│   ├── base.py              # BasePlugin
│   └── markdown.py          # MarkdownPlugin
│
├── gui/                     # PySide6（待实现）
│   ├── __init__.py
│   ├── main_window.py       # 主窗口
│   ├── subtitle_widget.py   # 字幕控件
│   ├── sidebar.py           # 侧边栏
│   ├── status_bar.py        # 状态栏
│   └── settings_dialog.py   # 设置对话框
│
└── notes/                   # 输出目录（自动生成）
```

---

## 关键文件说明

| 文件 | 职责 | 扩展方式 |
| --- | --- | --- |
| `config.py` | 所有配置 | 加字段，不改逻辑 |
| `app.py` | Application 生命周期 | Pipeline 列表里加一行 |
| `worker.py` | 缓存/VAD/窗口调度 | 不常改，改也不影响外部 |
| `recognizer.py` | 模型推理 + `_clean_text` | 换模型时替换这个文件 |
| `corrector/` | 文本处理流水线 | 新增一个类，Pipeline 加一行 |
| `plugins/` | 输出 | 新增一个类，Application 加一行 |
| `gui/` | PySide6 界面 | 独立模块，不侵入后端 |

---

## 注意事项

- 所有模块通过 EventBus 通信，禁止模块间直接调用
- Worker 只负责"什么时候送识别"，不负责"怎么处理"
- Recognizer 只负责模型推理，不负责缓存或调度
- Corrector 只修改 sentence.text，不修改 raw_text
- Plugin 只订阅事件，不主动拉取
- GUI 收到 SENTENCE 事件只管显示，不做任何业务逻辑
- CUDA 当前不可用（kernel 不兼容），全部走 CPU
- Sentence.metadata 保留给 GUI 展示每个 Corrector 的处理痕迹
