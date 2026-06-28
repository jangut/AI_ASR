# SpeechNote

> 一款面向学习、会议和创作的本地 AI 语音笔记软件。

SpeechNote 将麦克风语音实时转换为结构化 Markdown 笔记，并提供可扩展的文本处理流水线，为后续 AI 润色、知识整理、全文检索等功能提供统一架构。

---

# 项目目标

SpeechNote 的目标并不是做一个简单的"语音转文字"程序，而是搭建一套完整的本地 AI 笔记工作流。

整体流程如下：

```
Microphone
      │
      ▼
Recorder
      │
      ▼
RingBuffer
      │
      ▼
ASRWorker
      │
      ▼
SenseVoiceRecognizer
      │
      ▼
Sentence
      │
      ▼
CorrectorPipeline
      │
      ├── DuplicateCorrector
      ├── DictionaryCorrector（Future）
      ├── AICorrector（Future）
      └── ...
      │
      ▼
EventBus
      │
      ▼
Plugins
      ├── Markdown
      ├── SQLite（Future）
      ├── Qt GUI（Future）
      └── ...
```

整个系统采用事件驱动架构，各模块之间低耦合，可以独立替换和扩展。

---

# 当前功能（v2.2 Alpha）

## 已完成

* 项目整体架构
* 生命周期管理
* EventBus 事件总线
* RingBuffer 音频缓冲
* Recorder 麦克风采集
* ASRWorker 调度线程
* SenseVoice 接入
* Markdown 输出
* Sentence 数据模型
* CorrectorPipeline
* DuplicateCorrector（最长后缀-前缀去重）
* 全局 Logger
* Config 配置中心
* 异常恢复（Worker 不因识别异常退出）

---

# 项目结构

```
SpeechNote/

main.py

app.py

config.py

core/
    event_bus.py
    events.py
    logger.py
    sentence.py

audio/
    recorder.py
    ring_buffer.py

asr/
    base.py
    recognizer.py
    worker.py

corrector/
    base.py
    identity.py
    duplicate.py
    pipeline.py

plugin/
    markdown.py
```

所有模块职责单一。

Recognizer 负责识别。

Worker 负责调度。

Corrector 负责文本处理。

Plugin 负责输出。

任何模块都可以独立替换。

---

# 设计原则

## 单一职责（Single Responsibility）

每个模块只负责一件事情。

例如：

Recorder

只采集声音。

Recognizer

只负责识别。

Corrector

只负责文本修正。

Plugin

只负责输出。

---

## Pipeline（流水线）

所有文本统一经过：

```
Sentence
      │
      ▼
CorrectorPipeline
      │
      ▼
Sentence
```

以后增加：

* AI 修正
* 专业术语
* 标点恢复
* 人名识别

无需修改 Worker 和 Recognizer。

---

## Event Driven（事件驱动）

所有输出均通过 EventBus。

新增：

* GUI
* SQLite
* HTTP API

无需修改识别模块。

---

## Configuration First

所有参数均由 Config 控制。

例如：

* SampleRate
* RecognizeWindow
* OverlapWindow
* Device
* ModelPath

避免 Magic Number。

---

# 已实现优化

## Audio Cache

Recognizer 不再每 100 ms 推理。

Worker 自动缓存多个 Audio Block 后统一识别。

降低推理次数，提高识别准确率。

---

## DuplicateCorrector

采用最长后缀-前缀匹配算法。

例如：

```
上一句：
大家下午好

下一句：
下午好今天开始

↓

输出：

今天开始
```

避免 Overlap Window 导致重复文本。

---

## Error Recovery

Worker 内部统一：

```
try:

recognize()

↓

pipeline.correct()

↓

emit()

except:

log

↓

ERROR Event

↓

continue
```

任何识别异常都不会导致线程退出。

---

# Future

## ASR

* VAD
* Streaming ASR
* Overlap Window 优化
* 多语言支持

## AI

* AI 自动润色
* AI 自动摘要
* AI 自动生成标题
* AI 自动整理会议纪要

## GUI

* Qt
* 实时字幕
* Markdown 编辑器
* 设置界面

## Storage

* SQLite
* 全文搜索
* 标签
* 时间轴

---

# License

MIT
