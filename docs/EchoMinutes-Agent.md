# EchoMinutes-Agent 桌面端 AI 会议纪要工作台开发基线文档

> 本文档用于开启 `Codex /init`、生成或修订 `AGENTS.md`、以及指导后续多轮 AI coding agent 接力开发。  
> 产品定位：**借鉴讯飞听见的产品形态，但收敛为一个本地优先、跨平台桌面端的 AI 会议纪要工作台。**

---

## 0. 文档定位

本文档是 `EchoMinutes-Agent` 的产品、架构、交互和交付基线。

它面向以下使用场景：

- 使用 Codex、Claude Code 或类似 coding agent 初始化项目；
- 通过 `/init` 生成或补充 `AGENTS.md`；
- 在多轮开发中保持产品范围、技术栈和交付优先级一致；
- 每轮 coding task 开始前进行范围判断；
- 每轮 coding task 结束后进行验收对齐。

本文档不是商业计划书，不是完整 PRD，也不是 UI 高保真稿。

它更像一份面向 AI coding agent 的**交付契约**：

- 明确要做什么；
- 明确暂时不做什么；
- 明确先后顺序；
- 明确仓库结构；
- 明确接口边界；
- 明确每轮开发的行为纪律。

如果本文档与仓库中的 `AGENTS.md` 冲突，以 `AGENTS.md` 为准；如果 `AGENTS.md` 与用户最新明确指令冲突，以用户最新指令为准。

---

## 1. 产品名称

### 1.1 推荐名称

项目推荐名称：

```text
EchoMinutes-Agent
```

含义：

- `Echo`：声音、录音、语音内容；
- `Minutes`：会议纪要；
- `Agent`：AI 辅助处理工作流。

这个名称比 `Meeting Minutes Agent` 更短、更适合作为仓库名和桌面应用名，同时仍然能让用户理解产品方向。

### 1.2 可选备用名称

如果后续需要更换品牌名，可以从以下名称中选择：

```text
Meeting-Minutes-Agent
MinuteFlow-Agent
VoxMinutes-Agent
EchoBrief-Agent
NoteFlow-Minutes
MeetingNote-Studio
VoiceMinutes-Studio
```

首版仓库名建议使用：

```text
echominutes-agent
```

桌面应用显示名建议使用：

```text
EchoMinutes Agent
```

---

## 2. 产品定义

`EchoMinutes-Agent` 是一个**本地优先、跨平台桌面端 AI 会议纪要工作台**。

它解决一条核心工作流：

```text
本地音视频文件
  -> 云端或本地 ASR 转写
  -> 说话人分段
  -> 对话历史结构化
  -> AI 会议纪要生成
  -> 用户审阅与编辑
  -> Markdown / PDF / Word 导出
  -> 本地历史留存与复用
```

### 2.1 首版产品必须支持

首个可交付版本必须支持：

- Linux + Windows 桌面端；
- 导入本地音频或视频文件；
- 创建会议处理任务；
- 调用阿里云体系内的 ASR / 语音转写能力完成转写；
- 调用阿里百炼 Qwen API 生成结构化会议纪要；
- 支持中英文优先；
- 支持中文方言方向的扩展能力；
- 支持其他语言的配置扩展；
- 支持 `Speaker 1`、`Speaker 2`、`Speaker 3` 形式的说话人分段；
- 不自动识别真实姓名；
- 支持用户手动把 `Speaker 1` 改为真实姓名或角色；
- 支持转写结果查看、编辑和重新生成纪要；
- 支持生成固定结构会议纪要；
- 支持导出 Markdown、PDF、Word；
- 支持历史会议重新打开、继续编辑和再次导出；
- 支持本地 API Key 与模型配置；
- 不需要用户登录。

### 2.2 首版明确不做

首版不做：

- 实时录音；
- 在线协作；
- 多端同步；
- 用户注册、登录、会员体系；
- 支付、套餐、商城；
- SaaS 管理后台；
- 企业成员管理；
- 飞书、钉钉、企业微信集成；
- 跨会议知识库问答；
- 自动识别真实姓名；
- 完整人工精转服务；
- 云端长期存储；
- 打包分发的过早精细化。

这些功能只能在核心链路稳定后再讨论。

---

## 3. 借鉴讯飞听见后的产品收敛

参考对象提供了以下产品形态：

- 导入音视频；
- 实时录音；
- 人工精转；
- 会议记录；
- 课堂笔记；
- 在线直播；
- 采访调研；
- 企业版服务；
- 多语言 / 方言支持；
- 说话人区分；
- 文稿导出；
- 多端互通。

`EchoMinutes-Agent` 不复刻其页面结构、品牌表达和商业模式，只借鉴其中适合桌面端 MVP 的功能范式。

### 3.1 保留能力

首版保留：

| 能力 | 是否进入首版 | 产品实现方式 |
|---|---:|---|
| 导入音视频 | 是 | 本地文件导入 |
| 语音转文字 | 是 | 阿里云 ASR Provider 抽象 |
| 说话人分段 | 是 | Speaker 1 / 2 / 3 |
| 时间戳 | 是 | 每段转写保留开始和结束时间 |
| 对话历史 | 是 | 类聊天记录式转写工作区 |
| AI 纪要生成 | 是 | 阿里百炼 Qwen API |
| 人工编辑 | 是 | 本地可编辑纪要编辑器 |
| 导出 | 是 | Markdown -> PDF -> Word |
| 历史复用 | 是 | 本地数据库和工作区 |

### 3.2 延后能力

延后：

| 能力 | 延后原因 |
|---|---|
| 实时录音 | 技术复杂度高，容易拖慢 MVP |
| 多端互通 | 需要账号、云存储和同步机制 |
| 企业版服务 | 与本地优先桌面端冲突 |
| 人工精转服务 | 首版可转化为“人工校对模式” |
| 课堂笔记 | 可作为模板扩展，不作为首版主线 |
| 在线直播 | 与实时能力类似，暂缓 |
| 采访调研 | 可作为纪要模板扩展 |
| 知识库问答 | 等会议历史稳定后再扩展 |
| 思维导图 | 作为增强导出或高级视图 |

---

## 4. 目标用户与核心场景

### 4.1 目标用户

首版目标用户：

- 研究生、教师、科研人员；
- 产品经理、项目经理；
- 咨询、访谈、调研人员；
- 企业内部会议记录人员；
- 想做作品集展示的 AI 应用开发者。

### 4.2 核心使用场景

首版优先场景：

1. 会议录音整理；
2. 课堂或讲座录音整理；
3. 访谈音频整理；
4. 项目讨论复盘；
5. 汇报材料初稿生成。

### 4.3 核心价值主张

```text
把一段长会议录音，变成可编辑、可导出、可复用的结构化会议纪要。
```

更具体地说：

- AI 先生成高质量初稿；
- 用户再做低成本校正；
- 本地保存历史；
- 不强依赖账号体系；
- 不把产品做成复杂 SaaS。

---

## 5. 首版用户流程

首版用户流程必须保持简单：

```text
启动应用
  -> 首次配置 API Key
  -> 选择本地音频 / 视频文件
  -> 创建会议任务
  -> 等待转写
  -> 查看说话人分段对话
  -> 生成会议纪要
  -> 人工审阅和编辑
  -> 导出 Markdown / PDF / Word
  -> 在历史列表中重新打开
```

### 5.1 详细流程

1. 用户打开桌面应用；
2. 如果未配置 API Key，进入设置引导页；
3. 用户选择阿里百炼 Qwen API Key；
4. 用户配置 ASR Provider；
5. 用户返回首页；
6. 用户点击“导入音视频”；
7. 系统复制或引用本地文件；
8. 系统创建会议任务；
9. 后端进入转写工作流；
10. UI 显示处理进度；
11. 转写完成后展示对话历史；
12. 用户检查 `Speaker 1 / 2 / 3` 分段；
13. 用户可手动重命名 speaker；
14. 用户点击“生成纪要”；
15. 系统调用 Qwen 生成结构化纪要；
16. 用户在编辑器中修改纪要；
17. 用户导出文件；
18. 导出记录写入本地数据库；
19. 用户下次可从历史会议中重新打开。

---

## 6. 平台目标

首版平台目标：

| 平台 | 支持优先级 |
|---|---:|
| Windows | P0 必须支持开发态运行，P3 支持打包验证 |
| Linux | P0 必须支持开发态运行，P3 支持打包验证 |
| macOS | 首版不作为验收目标，但架构上不要主动破坏兼容性 |

### 6.1 平台注意事项

- 不要在代码中写死 Windows 路径分隔符；
- 使用 `path.join` 或 Python `pathlib`；
- 本地工作区路径必须可配置；
- Electron 主进程负责平台差异；
- FastAPI 后端不要依赖仅 Windows 可用的能力；
- PDF 渲染器和字体需要考虑 Linux 缺字体问题；
- 打包验证必须晚于核心流程稳定。

---

## 7. 技术栈

目标技术栈：

```text
Electron
Vue 3
TypeScript
Vite
FastAPI
Python AI Workflow Framework
SQLAlchemy
SQLite
Aliyun / Bailian Qwen API
Python export toolchain
```

### 7.1 桌面端

- `Electron`：桌面壳层、窗口管理、本地服务启动；
- `preload`：安全暴露 IPC 能力；
- `Vue 3 + TypeScript + Vite`：渲染层；
- `Pinia`：前端状态管理；
- `Vue Router`：页面路由；
- `Tailwind CSS` 或轻量 CSS 变量系统：UI 样式；
- 不要使用过重的 UI 框架，除非后续明确需要。

### 7.2 后端服务

- `FastAPI`：本地 HTTP API；
- `Uvicorn`：开发态服务；
- `SQLAlchemy`：数据持久化抽象；
- `SQLite`：首版本地数据库；
- `Pydantic`：数据模型校验；
- `LangGraph` 或等价 Python workflow 框架：会议处理工作流；
- `python-dotenv`：开发态环境变量；
- `httpx`：调用云端 API。

### 7.3 AI 能力

- ASR：优先阿里云体系内语音转写产品；
- LLM：阿里百炼 Qwen API；
- API 调用必须通过 provider 抽象层；
- 不要把 API 调用散落在业务代码中；
- 必须提供 mock provider，方便无 API Key 时开发和测试 UI。

---

## 8. 总体架构

系统整体架构：

```text
┌──────────────────────────────────────────┐
│ Electron Main Process                     │
│ - app lifecycle                           │
│ - window management                       │
│ - start / stop FastAPI                    │
│ - native file dialog                      │
└───────────────────┬──────────────────────┘
                    │ IPC
┌───────────────────▼──────────────────────┐
│ Electron Preload Bridge                   │
│ - safe APIs                               │
│ - no direct Node exposure                 │
└───────────────────┬──────────────────────┘
                    │
┌───────────────────▼──────────────────────┐
│ Vue 3 Renderer                            │
│ - meeting library                         │
│ - import page                             │
│ - processing status                       │
│ - transcript workspace                    │
│ - note editor                             │
│ - export center                           │
│ - settings                                │
└───────────────────┬──────────────────────┘
                    │ localhost HTTP
┌───────────────────▼──────────────────────┐
│ FastAPI Local Service                     │
│ - REST API                                │
│ - task orchestration                      │
│ - database access                         │
│ - provider invocation                     │
│ - export generation                       │
└───────────────────┬──────────────────────┘
                    │
┌───────────────────▼──────────────────────┐
│ Python Workflow Layer                     │
│ - ingestion                               │
│ - transcription                           │
│ - normalization                           │
│ - summarization                           │
│ - review persistence                      │
│ - export                                  │
└───────────────────┬──────────────────────┘
                    │
┌───────────────────▼──────────────────────┐
│ Local Workspace + SQLite                  │
│ - media                                   │
│ - transcripts                             │
│ - notes                                   │
│ - exports                                 │
│ - temp                                    │
│ - logs                                    │
│ - app.db                                  │
└──────────────────────────────────────────┘
```

---

## 9. 本地工作区结构

应用应使用一个可预测的本地工作区结构：

```text
echominutes-agent/
  app.db
  config/
    settings.json
  media/
    {meeting_id}/
      source.ext
  transcripts/
    {meeting_id}/
      raw_transcript.json
      normalized_segments.json
  notes/
    {meeting_id}/
      generated_note.md
      edited_note.md
  exports/
    {meeting_id}/
      meeting-note.md
      meeting-note.pdf
      meeting-note.docx
  temp/
  logs/
    app.log
    backend.log
```

### 9.1 工作区规则

- 默认工作区在用户文档目录或应用数据目录下；
- 用户后续可以在设置中修改；
- 媒体文件首版可以采用“复制到工作区”策略；
- 如果用户选择“不复制，仅引用路径”，必须处理源文件丢失情况；
- 所有导出文件路径必须写入数据库；
- 临时文件必须可清理；
- 日志不得记录完整 API Key。

---

## 10. 数据模型

首版建议数据模型如下。

### 10.1 Meeting

```text
Meeting
- id
- title
- source_file_name
- source_file_path
- workspace_media_path
- language
- accent_hint
- status
- created_at
- updated_at
- duration_seconds
- error_message
```

### 10.2 TranscriptSegment

```text
TranscriptSegment
- id
- meeting_id
- speaker_id
- speaker_label
- speaker_display_name
- speaker_gender_hint
- start_time_ms
- end_time_ms
- text
- confidence
- raw_payload
- created_at
- updated_at
```

### 10.3 MeetingNote

```text
MeetingNote
- id
- meeting_id
- template_type
- generated_markdown
- edited_markdown
- summary
- decisions_json
- action_items_json
- risks_json
- created_at
- updated_at
```

### 10.4 ExportRecord

```text
ExportRecord
- id
- meeting_id
- format
- file_path
- created_at
```

### 10.5 AppSetting

```text
AppSetting
- id
- key
- value
- encrypted
- created_at
- updated_at
```

### 10.6 Speaker 字段规则

说话人首版定义为：

```text
Speaker 1
Speaker 2
Speaker 3
...
```

系统不自动识别真实姓名。

允许用户手动把 speaker 重命名为：

```text
主持人
张老师
客户 A
产品经理
研发负责人
```

`gender_hint` 只能作为可选弱提示字段，不作为身份判断依据。

建议值：

```text
unknown
male_like_voice
female_like_voice
mixed_or_uncertain
```

规则：

- 默认值为 `unknown`；
- 只有 ASR Provider 明确返回且有置信度时才填充；
- UI 默认不要把性别标签放在核心位置；
- 用户可以手动修改或隐藏；
- 不要在纪要中把音色提示写成确定性事实。

---

## 11. AI Provider 策略

首版必须采用 Provider 抽象，不要把某个云厂商调用写死在业务逻辑中。

### 11.1 Provider 分层

```text
app/services/providers/
  asr/
    base.py
    aliyun_asr_provider.py
    mock_asr_provider.py
  llm/
    base.py
    qwen_bailian_provider.py
    mock_llm_provider.py
```

### 11.2 ASR Provider

ASR Provider 负责：

- 上传或读取本地音视频；
- 创建转写任务；
- 查询任务进度；
- 获取转写结果；
- 返回统一格式的说话人分段结果。

统一返回格式：

```json
{
  "language": "zh",
  "duration_seconds": 3600,
  "segments": [
    {
      "speaker_id": "speaker_1",
      "speaker_label": "Speaker 1",
      "speaker_gender_hint": "unknown",
      "start_time_ms": 0,
      "end_time_ms": 8200,
      "text": "大家好，我们开始今天的项目例会。",
      "confidence": 0.92
    }
  ],
  "raw_payload": {}
}
```

首版要求：

- 必须有 `MockASRProvider`；
- 必须有 provider interface；
- 阿里云 ASR 接入可以先通过配置占位和 mock 打通 UI；
- 真正接入云端 API 时必须集中在 `aliyun_asr_provider.py`；
- 不要让前端直接调用云 API。

### 11.3 LLM Provider

LLM Provider 负责调用阿里百炼 Qwen API 生成会议纪要。

统一输入：

```json
{
  "meeting_title": "项目周会",
  "language": "zh",
  "segments": [
    {
      "speaker_label": "Speaker 1",
      "start_time": "00:00:00",
      "end_time": "00:00:08",
      "text": "大家好，我们开始今天的项目例会。"
    }
  ],
  "template_type": "standard_meeting"
}
```

统一输出：

```json
{
  "markdown": "...",
  "summary": "...",
  "decisions": [],
  "action_items": [],
  "risks": []
}
```

首版要求：

- 默认模型服务：阿里百炼 Qwen API；
- 具体模型名从设置页读取；
- 必须支持 API Key 配置；
- 必须有 `MockLLMProvider`；
- 提示词必须集中管理；
- 不要在 UI 层拼接大段 prompt；
- prompt 输出优先 Markdown；
- action items 必须结构化保存。

---

## 12. 语言与方言支持策略

### 12.1 优先级

语言支持优先级：

| 语言 / 方言 | 优先级 |
|---|---:|
| 普通话中文 | P1 必须 |
| 中英混说 | P1 优先 |
| 英文 | P1 优先 |
| 粤语 | P2 |
| 四川话 | P2 |
| 上海话 | P2 |
| 其他中文方言 | P2 / P3 根据 ASR Provider 能力 |
| 其他国家语言 | P3 配置扩展 |

### 12.2 UI 配置

导入任务时允许用户选择：

```text
语言：
- 自动检测
- 中文
- 英文
- 中英混合
- 其他

中文口音 / 方言提示：
- 自动检测
- 普通话
- 粤语
- 四川话
- 上海话
- 其他中文方言
```

注意：

- 不要在产品文案中承诺“支持中国所有方言且准确无误”；
- 应表述为“面向中文多方言场景优化，具体效果取决于录音质量和所选 ASR 服务”；
- 首版可在设置中暴露 provider 能力说明；
- 方言能力主要由 ASR Provider 决定，LLM 只负责整理转写文本。

---

## 13. 会议纪要模板

首版至少支持一个默认模板：

```text
标准会议纪要
```

输出结构：

```markdown
# 会议纪要

## 1. 会议概览

- 会议主题：
- 会议时间：
- 会议来源：
- 主要参与人：
- 纪要生成时间：

## 2. 核心摘要

用 3 到 6 条概括会议主要内容。

## 3. 主要议题

### 议题 1：

- 背景：
- 讨论要点：
- 结论：

### 议题 2：

- 背景：
- 讨论要点：
- 结论：

## 4. 决议事项

| 序号 | 决议 | 相关人员 | 备注 |
|---|---|---|---|

## 5. 行动项

| 序号 | 任务 | 负责人 | 截止时间 | 状态 | 依据 |
|---|---|---|---|---|---|

## 6. 风险与待确认问题

| 序号 | 问题 | 影响 | 建议 |
|---|---|---|---|

## 7. 原文依据

列出与核心结论相关的原文时间段，便于用户回听确认。
```

### 13.1 后续模板

后续可扩展：

- 课堂笔记；
- 访谈整理；
- 项目复盘；
- 周会纪要；
- 客户会议纪要；
- 论文组会纪要。

但首版不要因为模板过多拖慢核心链路。

---

## 14. 工作流状态机

会议任务状态建议如下：

```text
created
imported
transcribing
transcribed
normalizing
normalized
summarizing
summarized
reviewing
exporting
exported
failed
cancelled
```

### 14.1 工作流阶段

```text
Ingestion
  -> Transcription
  -> Normalization
  -> Summarization
  -> Review
  -> Export
```

### 14.2 失败处理

任何阶段失败时，必须保存：

- 当前阶段；
- 错误摘要；
- 原始异常日志；
- 是否允许重试；
- 重试入口。

UI 不应只显示“失败”，而应该显示类似：

```text
转写失败：ASR Provider 返回超时。你可以稍后重试，或者检查 API Key 与网络连接。
```

---

## 15. 前端页面结构

首版页面建议：

```text
/
  Dashboard
/import
  ImportMeeting
/meetings
  MeetingLibrary
/meetings/:id
  MeetingWorkspace
/settings
  Settings
/exports
  ExportHistory
```

### 15.1 Dashboard

目标：

- 展示产品主入口；
- 显示最近会议；
- 显示 API 配置状态；
- 显示本地服务连接状态；
- 显示“导入音视频”主按钮。

### 15.2 ImportMeeting

目标：

- 选择本地音频 / 视频；
- 填写会议标题；
- 选择语言；
- 选择方言提示；
- 选择处理模式；
- 创建任务。

处理模式：

```text
标准模式：速度优先
高质量模式：纪要质量优先
开发模式：Mock Provider
```

### 15.3 MeetingLibrary

目标：

- 列出历史会议；
- 支持按时间排序；
- 支持按状态过滤；
- 支持搜索标题；
- 支持重新打开会议。

### 15.4 MeetingWorkspace

这是产品核心页面。

建议三栏布局：

```text
左侧：会议列表 / 当前会议信息 / 任务状态
中间：转写对话历史
右侧：AI 纪要编辑器
```

或者二栏布局：

```text
左侧 55%：转写对话
右侧 45%：纪要编辑器
```

核心组件：

- 音频时间轴；
- 转写段落；
- speaker 标签；
- speaker 重命名；
- 时间戳；
- 复制段落；
- 生成纪要按钮；
- 重新生成按钮；
- 编辑器；
- 导出按钮。

### 15.5 Settings

目标：

- 配置工作区；
- 配置阿里百炼 Qwen API Key；
- 配置 Qwen 模型名；
- 配置 ASR Provider；
- 测试连接；
- 选择默认导出目录；
- 查看日志目录；
- 清理缓存。

### 15.6 ExportHistory

目标：

- 查看所有导出记录；
- 打开导出文件所在目录；
- 重新导出；
- 删除导出记录。

---

## 16. UI 设计方向

视觉风格参考讯飞听见的“轻量、浅色、蓝紫渐变、玻璃拟态卡片”，但必须形成自己的桌面工作台特色，不复刻其网页结构。

推荐设计语言：

```text
Calm Aurora Desktop
```

关键词：

- 本地优先；
- 专业；
- 清爽；
- 可信；
- 安静；
- 适合长时间编辑；
- 轻微科技感；
- 不要过度营销化。

### 16.1 色彩建议

主色：

```text
Aurora Blue
```

辅助色：

```text
Soft Violet
Cyan Glow
Slate Gray
Warm White
```

使用原则：

- 大面积背景使用浅蓝灰；
- 主要按钮使用蓝紫渐变；
- 卡片使用白色或半透明白；
- 不要使用过多高饱和颜色；
- speaker 可以使用低饱和色标签区分；
- 警告和错误使用克制的红 / 橙。

### 16.2 布局建议

不要做成网页首页式宣传页。

桌面端应该更像工作台：

```text
顶部：应用标题 + 当前状态 + 设置入口
左侧：会议库 / 工作流步骤
中间：转写正文
右侧：纪要编辑器
底部：音频进度条 / 当前任务状态
```

### 16.3 关键 UI 组件

#### Workflow Stepper

顶部或左侧展示：

```text
导入 -> 转写 -> 整理 -> 纪要 -> 审阅 -> 导出
```

每一步有状态：

```text
未开始
进行中
已完成
失败
可重试
```

#### Transcript Card

每个转写段落展示：

```text
[Speaker 1] [00:00:03 - 00:00:12]
大家好，我们开始今天的会议。
```

支持：

- speaker 重命名；
- 点击时间戳定位音频；
- 复制文本；
- 标记重点；
- 置信度较低时弱提示。

#### Note Editor

右侧纪要编辑器：

- Markdown 编辑；
- 可预览；
- 支持 AI 重新生成；
- 支持保存；
- 支持导出；
- 支持从原文插入引用。

#### Export Modal

导出弹窗：

```text
导出格式：
- Markdown
- PDF
- Word

导出范围：
- 当前编辑版本
- AI 原始生成版本

导出位置：
- 默认 exports 目录
- 用户选择目录
```

### 16.4 UI 特色建议

为了区别于讯飞听见，可以加入以下特色：

1. **双栏审阅模式**  
   左边是原始对话，右边是纪要，适合人工校正。

2. **会议工作流时间线**  
   让用户明确看到当前任务处于“转写 / 纪要 / 导出”的哪一步。

3. **原文依据引用**  
   纪要中的关键结论可以对应原文时间戳。

4. **本地工作区可见性**  
   显示“数据保存在本地工作区”，增强可信感。

5. **模板化纪要**  
   标准会议、课堂笔记、访谈整理后续可切换。

6. **Speaker 管理面板**  
   用户可以统一把 Speaker 1 改成“张老师”，全局同步更新。

---

## 17. 后端 API 草案

首版 FastAPI 接口建议：

### 17.1 Health

```http
GET /api/health
```

返回：

```json
{
  "ok": true,
  "version": "0.1.0"
}
```

### 17.2 Settings

```http
GET /api/settings
PUT /api/settings
POST /api/settings/test-llm
POST /api/settings/test-asr
```

### 17.3 Meetings

```http
GET /api/meetings
POST /api/meetings
GET /api/meetings/{meeting_id}
PATCH /api/meetings/{meeting_id}
DELETE /api/meetings/{meeting_id}
```

### 17.4 Transcription

```http
POST /api/meetings/{meeting_id}/transcribe
GET /api/meetings/{meeting_id}/transcript
PATCH /api/meetings/{meeting_id}/segments/{segment_id}
```

### 17.5 Summary

```http
POST /api/meetings/{meeting_id}/summarize
GET /api/meetings/{meeting_id}/note
PUT /api/meetings/{meeting_id}/note
```

### 17.6 Export

```http
POST /api/meetings/{meeting_id}/export
GET /api/meetings/{meeting_id}/exports
```

### 17.7 Logs

```http
GET /api/logs/recent
```

仅开发态使用。

---

## 18. 导出策略

导出优先级按用户要求：

```text
P3a Markdown
P3b PDF
P3c Word
```

### 18.1 Markdown

Markdown 是第一优先级。

要求：

- 使用用户编辑后的 `edited_markdown`；
- 如果没有编辑版本，使用 `generated_markdown`；
- 文件名安全处理；
- 支持 UTF-8；
- 支持中文。

### 18.2 PDF

PDF 第二优先级。

建议策略：

```text
Markdown -> HTML Template -> PDF Renderer
```

要求：

- 视觉简洁；
- 支持中文字体；
- Linux 和 Windows 均可运行；
- 不追求复杂排版；
- 必须包含会议标题、摘要、行动项、正文。

### 18.3 Word

Word 第三优先级。

建议策略：

```text
Markdown / structured note -> python-docx -> docx
```

要求：

- 标题层级清晰；
- 表格可读；
- 中文字体尽量稳定；
- 不追求花哨样式。

---

## 19. 安全与隐私

首版是本地优先应用，但仍会调用云端 API。

必须明确：

- 音视频可能会被发送到 ASR Provider；
- 转写文本会被发送到 LLM Provider；
- API Key 保存在本地；
- 不做账号系统；
- 不做云端同步；
- 日志不记录 API Key；
- 错误提示不泄露密钥；
- 用户可以清理本地工作区。

设置页必须有清晰说明：

```text
本应用默认将会议文件和转写结果保存在本地工作区。
当你启用云端 ASR 或 Qwen API 时，相关音频或文本会被发送至对应服务商进行处理。
```

---

## 20. 仓库结构建议

建议仓库结构：

```text
echominutes-agent/
  AGENTS.md
  README.md
  package.json
  pnpm-workspace.yaml
  apps/
    package.json
    electron.vite.config.ts
    tsconfig.json
    electron/
      main/
      preload/
    renderer/
      src/
        app/
        components/
        pages/
        stores/
        services/
        styles/
  backend/
    pyproject.toml
    app/
      main.py
      api/
      core/
      db/
      models/
      schemas/
      services/
        workflow/
        providers/
          asr/
          llm/
        export/
      prompts/
      utils/
    tests/
  docs/
    EchoMinutes-Agent.md
  scripts/
    dev.ps1
    dev.sh
  workspace.example/
```

### 20.1 前端原则

- 所有请求通过统一 API client；
- 不在组件里硬编码后端地址；
- 不在渲染进程直接访问 Node 文件系统；
- 复杂状态进入 Pinia；
- 页面组件和通用组件分离；
- 不过早引入复杂 UI 框架。

### 20.2 后端原则

- API、service、provider、model 分层；
- Provider 可替换；
- Workflow 可测试；
- 数据模型集中定义；
- Prompt 集中管理；
- 导出逻辑独立；
- 单元测试至少覆盖核心 service。

---

## 21. AGENTS.md 建议规则

`AGENTS.md` 应至少包含以下规则：

### 21.1 每轮开始必须做

```text
1. 阅读 AGENTS.md。
2. 阅读 docs/EchoMinutes-Agent.md。
3. 审阅当前仓库结构和已有代码。
4. 判断当前处于 P0 / P1 / P2 / P3 哪一层。
5. 不要假设文档代表最新代码状态，以代码为准。
6. 在大规模改动前说明本轮最小可交付范围。
```

### 21.2 每轮结束必须做

```text
1. 总结完成内容。
2. 说明修改了哪些文件。
3. 说明如何运行或验证。
4. 说明哪些测试已通过。
5. 说明剩余风险。
6. 给出下一轮建议任务。
```

### 21.3 禁止事项

```text
- 不要一开始做登录系统。
- 不要一开始做 SaaS 后台。
- 不要一开始做实时录音。
- 不要一开始做在线协作。
- 不要绕过 Provider 抽象直接调用云 API。
- 不要把 API Key 写入仓库。
- 不要在 UI 层拼接 prompt。
- 不要在核心流程没打通前做复杂动效和打包分发。
```

### 21.4 验证纪律

每轮 coding 后必须至少做一种验证：

```text
- 前端 typecheck
- 前端 lint
- 后端 pytest
- 后端接口启动检查
- 本地端到端手工流程
```

如果无法验证，必须说明原因。

---

## 22. 交付分层

### P0. 基础骨架与开发态运行

目标：

建立可启动的最小桌面应用骨架。

范围：

- Electron 主进程；
- Vue 3 渲染层；
- FastAPI 本地服务；
- Electron 启动 FastAPI；
- 前端能检测后端 health；
- SQLite 初始化；
- Settings 基础读写；
- Mock Provider；
- Linux + Windows 开发态启动脚本。

验收标准：

- `pnpm dev` 或脚本能启动桌面端；
- FastAPI 能启动；
- UI 能显示后端连接状态；
- 设置能保存并重启后加载；
- Mock 数据可用于演示转写页面。

### P1. 文件导入与转写闭环

目标：

打通本地文件到说话人分段转写的闭环。

范围：

- 文件选择；
- 创建 Meeting；
- 保存源文件；
- 创建转写任务；
- ASR Provider interface；
- MockASRProvider；
- AliyunASRProvider 占位或初步接入；
- 转写状态更新；
- segment 入库；
- 转写页面展示。

验收标准：

- 用户能导入本地文件；
- 系统能生成或获取转写结果；
- UI 能显示 Speaker 分段和时间戳；
- 失败可见且可重试。

### P2. Qwen 纪要生成与编辑工作台

目标：

让转写结果变成可用会议纪要。

范围：

- Qwen Bailian provider；
- MockLLMProvider；
- Prompt 模板；
- 标准会议纪要模板；
- 纪要生成；
- Markdown 编辑器；
- 保存编辑版本；
- Speaker 重命名；
- 会议历史重新打开；
- 重新生成纪要。

验收标准：

- 转写完成后可生成纪要；
- 纪要结构固定；
- 用户可编辑并保存；
- 历史会议可重新打开；
- 重命名 Speaker 后对话视图同步。

### P3. 导出、稳定性与交付准备

目标：

让应用可演示、可交付、可日常试用。

范围：

- Markdown 导出；
- PDF 导出；
- Word 导出；
- 导出记录；
- 打开导出目录；
- 错误提示优化；
- 日志查看；
- 示例数据；
- Linux + Windows 打包验证。

验收标准：

- 导入 -> 转写 -> 纪要 -> 编辑 -> 导出可闭环；
- Markdown 可用；
- PDF 可用；
- Word 可用；
- Linux 和 Windows 至少完成开发态验证；
- 打包验证只在主流程稳定后执行。

---

## 23. 第一轮 Codex 任务建议

如果仓库还没有代码，第一轮 coding agent 应只做 P0 的最小骨架。

第一轮任务：

```text
Create the initial monorepo for EchoMinutes-Agent.

Requirements:
1. Create Electron + Vue 3 + TypeScript + Vite desktop app.
2. Create FastAPI backend app.
3. Add a health endpoint: GET /api/health.
4. Let the Vue renderer display local backend connection status.
5. Add basic Settings page with local placeholder settings.
6. Add SQLite initialization skeleton with SQLAlchemy.
7. Add MockASRProvider and MockLLMProvider placeholders.
8. Add docs and startup scripts for Windows and Linux.
9. Do not implement real Aliyun/Qwen calls yet.
10. Do not implement real file transcription yet.
```

第一轮验收：

```text
- Desktop app can launch.
- Backend can launch.
- Renderer can call /api/health.
- Settings page exists.
- Mock providers exist.
- Repository structure matches this document.
```

---

## 24. 第二轮 Codex 任务建议

第二轮进入 P1。

```text
Implement meeting file import and mock transcription flow.

Requirements:
1. Use Electron file dialog to select local audio/video files.
2. Create Meeting record in SQLite.
3. Copy selected file into workspace media directory.
4. Add transcription task API.
5. Use MockASRProvider to generate speaker-separated segments.
6. Persist transcript segments.
7. Display transcript in MeetingWorkspace.
8. Show task status transitions.
```

---

## 25. 第三轮 Codex 任务建议

第三轮进入 P2。

```text
Implement Qwen-style meeting note generation with MockLLMProvider first.

Requirements:
1. Add note data model.
2. Add summarize API.
3. Build prompt template for standard meeting notes.
4. Use MockLLMProvider to return fixed Markdown.
5. Add note editor in MeetingWorkspace.
6. Save edited Markdown.
7. Add regenerate note button.
8. Add Speaker rename support.
```

---

## 26. 第四轮 Codex 任务建议

第四轮进入 P3a / P3b / P3c。

```text
Implement export pipeline.

Requirements:
1. Export edited note to Markdown.
2. Add export record.
3. Add PDF export through HTML template.
4. Add Word export after PDF is stable.
5. Add export history list.
6. Add open export folder action.
```

---

## 27. 当前开放问题

以下问题暂时保留为 TODO，不阻塞 P0：

1. 具体使用阿里云哪一个 ASR 产品；
2. 阿里云 ASR 是否能直接返回 speaker diarization；
3. speaker gender hint 是否由 provider 返回；
4. PDF 渲染器最终选择；
5. 是否后续支持 Ollama 或 OpenAI-compatible fallback；
6. 是否后续支持课堂笔记模板；
7. 是否后续支持实时录音；
8. 是否后续支持思维导图导出。

---

## 28. 最终一句话

`EchoMinutes-Agent` 不是一个泛化 Agent 平台，也不是讯飞听见的复刻版。

它是一个：

```text
本地优先、跨平台、面向长会议音视频的 AI 会议纪要桌面工作台。
```

首版必须聚焦：

```text
导入音视频
  -> 说话人分段转写
  -> Qwen 生成会议纪要
  -> 人工编辑
  -> Markdown / PDF / Word 导出
  -> 本地历史复用
```

只有这条主链路稳定后，才允许扩展实时录音、课堂笔记、访谈模板、多端同步或企业服务。
