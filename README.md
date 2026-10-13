# 小红书图文创作 Skill

输入主题，先调研真实小红书笔记，再制作标题、正文、话题标签和配图。适用于支持 Skills 的 **Cursor** 与 **Codex**。配图使用当前环境的内置生图工具：Cursor 用 `GenerateImage`，Codex 用 `imagegen`。

[功能展示页](https://lishuang0209.github.io/xiaohongshu-content/) · [GitHub 仓库](https://github.com/lishuang0209/xiaohongshu-content)

## 能做什么

- 调研正好 3 条同题参考笔记，核验标题、来源、点赞、收藏与采集时间。默认点赞 ≥ 1000 且收藏 ≥ 300；缺失数据不能视为达标。
- 优先复用 24 小时内合格缓存，再用已连接的小红书 MCP 按「最多收藏」「最多点赞」各读取前 10 条并去重；仅为缺少数据的候选补读详情，最多 6 条。
- 仍不足时最多补 2 个近义关键词，再请用户决定扩大选题、降低门槛或明确跳过调研；不编造互动数据。
- 生成 3 个标题备选、约 300–600 字正文和 5–8 个标签。
- 提供 10 种视觉风格（含背景、文字、强调色），用户确认后默认生成 1 张竖版封面（3:4，1080×1440）；内容页按需制作。
- 落盘后核验真实像素，并用 `ensure_3x4.py` 把非 3:4 的图垫色或居中裁成 1080×1440。
- 登录由用户扫码确认；创作流程仅查询，不执行点赞、收藏、评论或发布。

平台数据受登录状态、访问限制和搜索结果影响。凑不够 3 条合格笔记时按技能说明扩词或询问是否降低门槛，不编造数据；用户可以明确要求跳过调研。已连接的小红书搜索 MCP 仍可用来查询，安装见下文。

## 快速安装

需要支持 Skills 的 Cursor 或 Codex，以及 Python 3.11+。图片生成使用 Cursor 的 `GenerateImage` 或 Codex 的 `imagegen`；本仓库不包含图片模型或 API 凭据。校正画幅的 `ensure_3x4.py` 需要 Pillow（`python3 -m pip install Pillow`）。

下载本仓库后，在仓库目录执行：

```bash
python3 scripts/install_skill.py --project /你的项目路径
```

脚本把 `小红书创作技能` 复制到该项目的两处技能目录，并打印实际写入的路径：

- `.agents/skills/xiaohongshu-content/`（Codex）
- `.cursor/skills/xiaohongshu-content/`（Cursor）

需要用户级 Cursor 技能时加上 `--user`，额外复制到 `~/.cursor/skills/xiaohongshu-content/`。

目标目录里已有不同内容时，脚本会退出并打印该路径，留待人工比较或备份。内容相同，或该目录已链接到本仓库技能源时，会跳过该路径。

也可以手动把 `小红书创作技能` 文件夹中的全部内容（含 `scripts/ensure_3x4.py`）复制到上述目录。打开该项目后检查技能是否被识别，必要时新建会话。

本仓库的技能源文件使用可见的中文文件夹，方便编辑；安装后使用固定的英文技能名 `xiaohongshu-content`。

## 使用

```text
使用本项目的 $xiaohongshu-content，主题是「租房卧室改造」。
```

也可指定风格、受众和张数，例如：

```text
使用 $xiaohongshu-content，主题是「新手咖啡入门」，面向上班族，风格用 5。
```

数据调研完成后选择风格。默认先制作封面；要完整套图时明确说「封面和内容页都要」或「再生成内容页」。

生图后若真实像素不是 1080×1440，在技能目录或本仓库执行：

```bash
python3 scripts/ensure_3x4.py 输入图 [-o 输出.png] [--bg R,G,B] [--mode pad|crop]
```

默认在输入文件旁写出 `*-3x4.png`。`--bg` 为垫底的 `R,G,B`，可对照技能中的风格色板。仓库根目录的 `scripts/ensure_3x4.py` 与技能目录中的副本相同。

## 接入小红书搜索

本技能使用独立的第三方项目 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)。安装技能不会自动安装 MCP，也不会共享作者的登录会话。

详见 [搜索工具安装与维护](docs/搜索工具安装与维护.md)。本仓库提供的安装辅助脚本适用于 **Apple Silicon Mac + Python 3.11 或更新版本**，固定对应 MCP v2.5.5。其他系统按上游说明安装，再配置相同的登录、搜索和详情工具。

## 文件说明

- `小红书创作技能/`：技能说明、`scripts/ensure_3x4.py` 及界面配置，安装时需完整复制。
- `scripts/`：技能安装、3:4 画幅校正、浏览器准备、MCP 接入、连接检查与开源打包脚本。
- `docs/`：搜索工具安装与维护说明。
- `展示页/`：功能展示页源码，包含流程演示、风格预览和安装入口；见[预览说明](展示页/README.md)。
- `LICENSE`：本仓库原创文件采用 MIT 许可证。
- `THIRD_PARTY_NOTICES.md`：第三方依赖与许可证说明。

本地可能另有 `本地资料/`、`output/`、`.agents/` 和 `.cursor/`；它们用于安装包、个人调研输出和本机技能发现，均排除在 Git 提交与发布包之外。请勿把整个工作文件夹直接拖到 GitHub 网页上传：网页上传不会自动遵守 `.gitignore`。

## 生成可上传的开源包

```bash
python3 scripts/build_release.py
```

生成 `dist/xiaohongshu-content-source.zip`，只包含明确列出的源码、技能和文档。解压后上传里面的项目文件即可；若想让 GitHub 展示项目首页，请上传解压后的文件，而非只上传 zip。

开源包不包含账号会话、二维码、访问令牌、历史笔记、安装二进制或浏览器组件。首次安装需自行下载依赖并扫码登录。当前维护者曾在 Apple Silicon Mac 验证登录、两种搜索排序和笔记详情读取；其他平台与全新环境仍需验证。

## 网页自动部署

推送到 `main` 后，`.github/workflows/pages.yml` 会生成公开下载包，将 `展示页/dist` 部署到 GitHub Pages。首次使用或 fork 后，在仓库 Settings → Pages 中选择 **GitHub Actions** 作为发布来源。工作流只发布静态网页与公开下载文件，不包含本地 MCP 服务。

## 许可证

本仓库原创技能、文档和辅助脚本按 [MIT](LICENSE) 提供。第三方搜索工具、浏览器组件及小红书内容各自适用其原有条款，不因本仓库的许可证而改变。
