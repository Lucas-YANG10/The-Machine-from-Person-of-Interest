# 新手使用指南

这个项目现在有两种打开方式。建议从第一种开始。

## 方式一：直接双击 HTML

进入 `standalone` 文件夹，双击：

```text
the-machine-manhattan.html
```

它会使用 Chrome、Edge、Firefox 或 Safari 打开。整个网页只有这一个文件：

- 不需要 VPN；
- 不需要访问 `chatgpt.site`；
- 不需要登录；
- 不需要安装 Python、Node.js 或 npm；
- 不需要启动服务器；
- 断网也可以使用。

如果 Windows 弹出“选择打开方式”，选择 Chrome 或 Edge，并可勾选“始终使用”。

## 方式二：修改源码后重新生成

这一方式适合开始学习代码后使用。

### 1. 文件之间是什么关系？

```text
data/synthetic/*.json
        ↓ 直接作为虚拟原始数据，被推断引擎读取
engine/run_pipeline.py
        ↓ 生成模型结果
app/data/machine-output.json
        ↓ 被构建脚本嵌入
tools/build_standalone.py
        ↓
standalone/the-machine-manhattan.html
```

### 2. 修改虚拟人物和记录

直接编辑：

```text
data/synthetic/people.json
data/synthetic/observations.json
data/synthetic/events.json
data/synthetic/zones.json
data/synthetic/ground_truth.json
data/synthetic/scenario.json
```

这些 JSON 是数据源，不会再被 Python 生成器覆盖。编辑后在项目根目录依次运行：

```bash
python engine/run_pipeline.py
python tools/build_standalone.py
```

最后重新双击生成的 HTML。

### 3. 修改网页样式或交互

编辑：

```text
standalone/template.html
```

这个文件已经用中文注释分成六个部分：

1. 页面基础设置；
2. CSS 视觉样式；
3. HTML 固定骨架；
4. 内嵌数据；
5. JavaScript 状态与渲染；
6. 点击、滑杆等交互事件。

编辑后只运行：

```bash
python tools/build_standalone.py
```

## 建议的学习顺序

1. 先双击成品，逐个点击人物、模式和页面。
2. 在 `template.html` 搜索 `renderQueue`，理解左侧人物列表如何生成。
3. 搜索 `renderDossier`，理解右侧人物档案如何生成。
4. 搜索 `renderMap`，理解 JSON 坐标如何变成 SVG 地图。
5. 最后阅读 `engine/run_pipeline.py` 和 `docs/ALGORITHMS.md`，理解概率从哪里来。

目前数据包含 30 个虚构人物、10 个候选事件、38 个曼哈顿 NTA
区域和 3,400 条记录。绝大多数记录是不会影响模型分数的日常背景活动。

不要一开始试图读完整个文件。先找到一个能在网页上看见的元素，再沿着它追到对应代码。
