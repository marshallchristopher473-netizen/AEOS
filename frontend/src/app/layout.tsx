import './globals.css';
import type { Metadata } from 'next';

import AppHeader from '@/components/AppHeader';

export const metadata: Metadata = {
  title: 'AEOS Teacher Portal',
  description: 'Teacher dashboard for student management',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppHeader />
        {children}
      </body>
    </html>
  );
}
