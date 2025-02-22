import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ["g9kjzb1j-3000.inc1.devtunnels.ms", "localhost:3000"]
    }
  }
};

export default nextConfig;
