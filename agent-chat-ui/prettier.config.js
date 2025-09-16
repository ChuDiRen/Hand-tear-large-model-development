// Copyright (c) 2025 左岚. All rights reserved.
/** @type {import('prettier').Config} */
const config = {
  // 每行最大字符数
  printWidth: 80,
  // 缩进大小
  tabWidth: 2,
  // 使用空格而不是制表符
  useTabs: false,
  // 语句末尾添加分号
  semi: true,
  // 使用单引号
  singleQuote: false,
  // 对象属性引号：仅在需要时添加
  quoteProps: "as-needed",
  // JSX 中使用单引号
  jsxSingleQuote: false,
  // 尾随逗号：ES5 兼容
  trailingComma: "es5",
  // 对象字面量的大括号间添加空格
  bracketSpacing: true,
  // JSX 标签的 > 放在最后一行的末尾
  bracketSameLine: false,
  // 箭头函数参数括号：避免时省略
  arrowParens: "avoid",
  // 换行符：自动
  endOfLine: "auto",
  // 插件
  plugins: ["prettier-plugin-tailwindcss"],
};

export default config;
