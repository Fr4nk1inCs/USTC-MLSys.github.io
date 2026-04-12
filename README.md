# Lab Website

这是一个适合部署到 GitHub Pages 的纯静态实验室官网模板，源码和构建环境都放在 `website/` 目录里。

## 目录

- `content/`: 站点内容数据，直接改这里最省事
- `assets/`: 样式、脚本、图标
- `labsite/`: Python 生成器
- `build.py`: 构建静态页面到 `dist/`
- `preview.py`: 本地预览
- `dist/`: 构建后的可部署静态文件

## 初始化环境

```bash
cd website
python3 -m venv .venv
./.venv/bin/python --version
```

这个站点的构建只用 Python 标准库，不依赖额外第三方包。

## 构建

根域名部署：

```bash
cd website
./.venv/bin/python build.py --base-path /
```

GitHub Pages 项目页部署，比如仓库名是 `lab-site`：

```bash
cd website
./.venv/bin/python build.py --base-path /lab-site/
```

## 本地预览

```bash
cd website
./.venv/bin/python preview.py --port 8000
```

然后打开 `http://127.0.0.1:8000`。

## 改内容

常改的是这几个文件：

- `content/site.json`
- `content/projects.json`
- `content/publications.json`
- `content/news.json`
- `content/team.json`

## 部署到 GitHub Pages

最稳的做法是把 `dist/` 作为最终产物发布。

如果你之后把整个仓库放到 GitHub 上，有两种常见方式：

1. 用 GitHub Actions 构建 `website/dist/` 后发布到 Pages。
2. 手动构建后，把 `dist/` 里的文件推到 Pages 对应分支或目录。

这个模板已经处理了 `base path`，所以既支持：

- `https://username.github.io/`
- `https://username.github.io/repo-name/`

## 备注

当前内容是可直接运行的示例内容，你后面只需要把实验室名、项目、论文、新闻和成员替换掉就可以继续用。
