# Git 提交指南

## 步骤 1: 初始化 Git 仓库（如果还没有）

```bash
cd d:\Code\binviewer\binviewer
git init
```

## 步骤 2: 添加所有文件

```bash
git add .
```

## 步骤 3: 提交到本地仓库

```bash
git commit -m "Initial commit: BIN Viewer - Binary file visualization tool"
```

## 步骤 4: 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 仓库名称：`bin-viewer` 或 `binviewer`
3. 描述：`A powerful binary file visualization tool for operator development and model debugging`
4. 选择 Public（公开）
5. **不要**勾选 "Add a README file"（我们已经有了）
6. **不要**勾选 "Add .gitignore"（我们已经有了）
7. **不要**选择 License（我们已经有了）
8. 点击 "Create repository"

## 步骤 5: 关联远程仓库

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/bin-viewer.git
```

## 步骤 6: 推送到 GitHub

```bash
# 推送主分支
git branch -M main
git push -u origin main
```

## 步骤 7: 添加演示视频（可选）

如果 demo.mp4 文件较大（>100MB），建议使用 Git LFS：

```bash
# 安装 Git LFS
git lfs install

# 追踪视频文件
git lfs track "*.mp4"

# 添加 .gitattributes
git add .gitattributes

# 提交
git commit -m "Add Git LFS tracking for video files"
git push
```

或者将视频上传到其他平台（如 YouTube、Bilibili），然后在 README 中添加链接。

## 常用命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 添加新文件
git add <file>
git commit -m "描述信息"
git push

# 拉取更新
git pull
```

## 推荐的 README 徽章

在 GitHub 仓库创建后，可以添加更多徽章：

```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/bin-viewer?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/bin-viewer?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/bin-viewer)
```

## 完成！

现在你的项目已经在 GitHub 上了！🎉

访问：`https://github.com/YOUR_USERNAME/bin-viewer`
