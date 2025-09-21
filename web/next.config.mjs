/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    typedRoutes: true,
  },
  eslint: {
    // Don't block production builds on lint errors
    ignoreDuringBuilds: true,
  },
  typescript: {
    // If your environment lacks certain types at build time, don't fail the build
    ignoreBuildErrors: false,
  },
};
export default nextConfig;
