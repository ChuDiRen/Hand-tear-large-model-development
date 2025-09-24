# 图表渲染功能

## 功能概述

前端现在支持自动识别和渲染图表链接。当AI消息中包含特定的图表服务链接时，这些链接会被自动渲染为嵌入式图片，而不是普通的文本链接。

## 支持的图表服务

目前支持以下图表服务的链接自动渲染：

- **阿里云对象存储**: `mdn.alipayobjects.com`
- **QuickChart**: `quickchart.io`
- **Google Charts**: `chart.googleapis.com`
- **Chart.io**: `api.chart.io`
- **MongoDB Charts**: `charts.mongodb.com`

## 工作原理

1. **链接识别**: `MarkdownText` 组件会检测markdown中的链接
2. **域名匹配**: 使用 `isChartUrl()` 函数检查链接是否属于支持的图表服务
3. **自动渲染**: 图表链接被渲染为 `<img>` 标签，普通链接保持原有行为
4. **加载状态**: 显示加载指示器，支持错误处理和回退

## 技术实现

### 核心文件

- `src/components/thread/markdown-text.tsx`: 主要实现文件
- `next.config.mjs`: Next.js图片域名配置

### 关键组件

```typescript
// 图表链接检测
const isChartUrl = (url: string): boolean => {
  const chartDomains = [
    'mdn.alipayobjects.com',
    'quickchart.io',
    // ...
  ];
  // 检查URL域名是否匹配
}

// 图表图片组件
const ChartImage: FC<{ src: string; alt?: string }> = ({ src, alt }) => {
  // 处理加载状态、错误状态
  // 渲染图片或错误信息
}
```

### 自定义链接处理器

```typescript
a: ({ href, children, ...props }) => {
  // 检测是否为图表链接
  if (href && isChartUrl(href)) {
    return <ChartImage src={href} alt={...} />;
  }
  
  // 普通链接的默认行为
  return <a href={href} target="_blank" {...props}>{children}</a>;
}
```

## 使用示例

当AI返回包含图表链接的消息时：

```markdown
**图表链接：** https://quickchart.io/chart?c=%7B%22type%22%3A%22bar%22...

查看上面的图表了解数据分布情况。
```

前端会自动将图表链接渲染为嵌入式图片，用户可以直接在聊天界面中查看图表，无需点击链接跳转。

## 错误处理

- **加载中**: 显示"加载图表中..."指示器
- **加载失败**: 显示错误信息和原始链接，用户可点击查看
- **网络问题**: 自动回退到链接形式

## 配置说明

### Next.js 图片域名配置

在 `next.config.mjs` 中配置允许的外部图片域名：

```javascript
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: 'mdn.alipayobjects.com',
      pathname: '/**',
    },
    // 其他图表服务域名...
  ],
}
```

## 扩展支持

要添加新的图表服务支持：

1. 在 `isChartUrl()` 函数中添加新的域名
2. 在 `next.config.mjs` 中添加对应的 `remotePatterns`
3. 测试新服务的图表链接渲染

## 注意事项

- 某些图表服务可能有跨域限制
- 图片加载速度取决于外部服务的响应时间
- 建议使用支持HTTPS的图表服务
- 大型图片可能影响页面加载性能
