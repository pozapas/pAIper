import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Optimize for better hydration
  reactStrictMode: true,
  // Don't fail production builds on lint or TS issues
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Webpack configuration
  webpack: (config, { isServer }) => {
    // Help with hydration by ensuring consistent builds
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
};

export default nextConfig;
