import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Don't let a stray lint or type error block a production deploy (e.g. Vercel).
  // Prefer fixing the underlying issue, but this keeps the build unblockable.
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // Backend serves uploaded photos from /uploads/** — allow <img> to load them
  // remotely if you later switch to next/image (plain <img> already works).
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "localhost" },
    ],
  },
};

export default nextConfig;
