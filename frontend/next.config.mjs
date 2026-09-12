/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Proxy API requests to FastAPI backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
