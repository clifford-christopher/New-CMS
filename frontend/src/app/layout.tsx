/**
 * Root Layout Component
 *
 * This is the root layout for the Next.js application using the App Router.
 * It includes:
 * - Bootstrap CSS import
 * - Global CSS
 * - Navbar and Footer components
 * - HTML structure with semantic layout
 * - Metadata configuration
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './globals.css';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI-Powered News CMS',
  description: 'Content management system for equity market research news generation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main className="container-fluid py-4">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
