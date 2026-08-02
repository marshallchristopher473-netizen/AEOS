#!/bin/bash
set -e

echo "Preparing AEOS frontend deployment for Vercel..."

if [ ! -d frontend ]; then
  mkdir -p frontend
fi

cd frontend

if [ ! -f package.json ]; then
  cat > package.json <<'EOF'
{
  "name": "aeos-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.15",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}
EOF
fi

if [ ! -f next.config.js ]; then
  cat > next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
EOF
fi

mkdir -p app public

cat > app/page.tsx <<'EOF'
export default function HomePage() {
  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>AEOS MVP Dashboard</h1>
      <p>AI-powered education operations for pilot schools.</p>
    </main>
  );
}
EOF

cat > app/layout.tsx <<'EOF'
export const metadata = {
  title: "AEOS",
  description: "AI Education Operations System",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

echo "Frontend scaffold created."
echo "Deploy with: vercel --prod"
