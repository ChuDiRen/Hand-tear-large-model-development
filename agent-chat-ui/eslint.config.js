// Copyright (c) 2025 左岚. All rights reserved.
import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // 允许使用 any 类型
      "@typescript-eslint/no-explicit-any": "off",
      // 允许未使用的变量（以下划线开头）
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      // 允许空的接口
      "@typescript-eslint/no-empty-interface": "off",
      // 允许 require
      "@typescript-eslint/no-var-requires": "off",
      // 关闭 React 在作用域中的检查（Next.js 不需要）
      "react/react-in-jsx-scope": "off",
      // 允许在 img 标签中使用 alt 属性为空
      "jsx-a11y/alt-text": "off",
    },
  },
];

export default eslintConfig;
