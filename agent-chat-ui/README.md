# 智能助手聊天界面

基于 Next.js 的中文智能助手聊天应用，提供简洁优雅的对话体验。

## 功能特性

- 🤖 智能对话界面
- 💬 支持文本、图片、PDF 文件上传
- 🗂️ 聊天历史管理（删除、重命名）
- 🎨 现代化 UI 设计
- 📱 响应式布局
- 🌙 深色/浅色主题切换
- 🔧 工具调用显示/隐藏

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 访问应用

打开浏览器访问 http://localhost:3000

## 配置说明

在首次使用时，需要配置：

- **部署 URL**: LangGraph 服务器地址（如：http://localhost:2024）
- **助手 ID**: 智能助手标识符（如：agent）
- **API 密钥**: LangSmith API 密钥（可选）

## 项目结构

```
src/
├── app/                  # Next.js 应用路由
├── components/           # React 组件
│   ├── thread/          # 聊天相关组件
│   └── ui/              # UI 基础组件
├── hooks/               # 自定义 Hooks
├── lib/                 # 工具函数
└── providers/           # Context 提供者
```

## 技术栈

- **框架**: Next.js 15
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **UI 组件**: Radix UI + shadcn/ui
- **状态管理**: React Context
- **图标**: Lucide React

## 开发说明

- 所有文本已完全汉化
- 移除了国际化功能，直接使用中文
- 支持聊天历史删除和管理
- 集成了文件上传功能

---

© 2025 左岚. All rights reserved.
