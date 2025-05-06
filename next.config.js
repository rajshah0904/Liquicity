/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      },
      {
        source: '/user/:path*',
        destination: 'http://localhost:8000/user/:path*'
      },
      {
        source: '/wallet/:path*',
        destination: 'http://localhost:8000/wallet/:path*'
      },
      {
        source: '/payment/:path*',
        destination: 'http://localhost:8000/payment/:path*'
      }
    ];
  }
};

module.exports = nextConfig; 