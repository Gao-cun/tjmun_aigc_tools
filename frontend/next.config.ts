import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  eslint: {
    // 使用独立的 npm run lint 做代码检查，避免 Next 15 与 flat ESLint 配置在 build 阶段冲突。
    ignoreDuringBuilds: true
  }
};

export default nextConfig;
