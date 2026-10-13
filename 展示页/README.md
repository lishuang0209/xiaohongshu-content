# 功能展示页

纯静态 HTML、CSS、JavaScript 页面，无构建依赖。页面中的流程与风格切换均为交互演示，不访问用户的小红书账号。

## 本地预览

先在仓库根目录运行 `python3 scripts/build_release.py`，生成公开源码下载包、安装指南与许可证副本，再启动网页：

```bash
python3 -m http.server 4173 --directory 展示页/dist --bind 127.0.0.1
```

浏览器打开 `http://127.0.0.1:4173`。也可用其他静态网页服务器托管 `展示页/dist`。

页面支持移动端菜单、四步流程切换、十种风格示意、安装命令切换与复制、提示词复制、FAQ 展开和源码下载。图形为原创 SVG 示意；Google Fonts 不可用时回退到系统字体。

项目仓库：https://github.com/lishuang0209/xiaohongshu-content

公开网页：https://lishuang0209.github.io/xiaohongshu-content/

开源区链接至项目 GitHub，安装区提供源码包下载；第三方 MCP 链接指向上游项目。推送到 main 后由 GitHub Actions 自动更新网页。fork 项目时可在 `dist/index.html` 和主 README 中修改自己的链接。

Sites 托管配置与服务标识保留在本机 `.openai` 目录，不包含在开源压缩包中。自行使用其他静态托管平台不需要该目录。
