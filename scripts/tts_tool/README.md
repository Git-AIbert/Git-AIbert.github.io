# TTS Tool

这个目录包含博客文章音频生成与播放器插入的模块化实现。

## 模块关系图

```text
scripts/generate_post_audio.py
  -> tts_tool.runtime
  -> tts_tool.cli
  -> tts_tool.batch.process_posts
       -> tts_tool.workflow.generate_audio
            -> tts_tool.paths
            -> tts_tool.text_cleaning
            -> tts_tool.synthesis
       -> tts_tool.workflow.generate_audio_and_update_post
            -> tts_tool.workflow.generate_audio
                 -> tts_tool.paths
                 -> tts_tool.text_cleaning
                 -> tts_tool.synthesis
            -> tts_tool.post_update
            -> tts_tool.paths.path_to_site_url
```

## 结构图

```text
               +---------------------------+
               | generate_post_audio.py    |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | tts_tool.batch            |
               | process_posts()           |
               +-------------+-------------+
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
      +----------------------+   +---------------------------+
      | workflow.generate_   |   | workflow.generate_audio_ |
      | audio()              |   | and_update_post()        |
      +----------+-----------+   +-------------+------------+
                 |                             |
                 v                             v
      +----------------------+   +----------------------+
      | text_cleaning.py     |   | post_update.py       |
      | synthesis.py         |   | paths.path_to_site_  |
      | paths.py             |   | url()                |
      +----------------------+   +----------------------+
```

## 模块职责

- `runtime.py`: 保证入口脚本运行在正确的 Python 环境中。
- `cli.py`: 统一管理命令行参数，并约束单文件/多文件场景的参数组合。
- `paths.py`: 处理输入文章路径、默认音频输出路径和站点 URL。
- `text_cleaning.py`: 负责 Markdown 清洗、替换规则和中文朗读文本预处理。
- `synthesis.py`: 负责设备选择、模型加载、TTS 合成和 `ffmpeg` 转码。
- `post_update.py`: 负责幂等插入或更新文章中的 `<audio>` 播放器。
- `workflow.py`: 定义单篇文章的核心工作流。
- `batch.py`: 负责批量处理多个文章输入，并决定是否更新文章中的播放器。

## 入口脚本

- `scripts/generate_post_audio.py`: 统一入口。支持单篇、多篇，以及通过参数决定是否更新文章。

## 常用命令

生成一篇文章音频并更新播放器：

```bash
python3 scripts/generate_post_audio.py "posts/death-course-01-课程介绍.md" --device cuda
```

一次生成两篇文章音频并更新播放器：

```bash
python3 scripts/generate_post_audio.py \
  "posts/death-course-01-课程介绍.md" \
  "posts/death-course-02-人的本质：二元论与物理主义.md" \
  --device cuda
```

只生成音频，不修改文章：

```bash
python3 scripts/generate_post_audio.py \
  "posts/death-course-01-课程介绍.md" \
  --device cuda \
  --audio-only
```
