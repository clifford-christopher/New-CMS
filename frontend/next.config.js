/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // API proxy configuration for backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL || 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Disable x-powered-by header
  poweredByHeader: false,

  // Enable SWC minification
  swcMinify: true,
};

module.exports = nextConfig;
