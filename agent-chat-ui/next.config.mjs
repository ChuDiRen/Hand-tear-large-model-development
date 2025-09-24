/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    },
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'mdn.alipayobjects.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'quickchart.io',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'chart.googleapis.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'api.chart.io',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'charts.mongodb.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
