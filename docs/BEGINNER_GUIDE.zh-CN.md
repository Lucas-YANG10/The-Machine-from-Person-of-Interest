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
engine/generate_synthetic_data.py
        ↓ 生成虚拟原始数据
data/synthetic/*.json
        ↓ 被推断引擎读取
engine/run_pipeline.py
        ↓ 生成模型结果
app/data/machine-output.json
        ↓ 被构建脚本嵌入
tools/build_standalone.py
        ↓
standalone/the-machine-manhattan.html
```

### 2. 修改虚拟人物和记录

先编辑：

```text
engine/generate_synthetic_data.py
```

然后在项目根目录依次运行：

```bash
python engine/generate_synthetic_data.py
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

不要一开始试图读完整个文件。先找到一个能在网页上看见的元素，再沿着它追到对应代码。
