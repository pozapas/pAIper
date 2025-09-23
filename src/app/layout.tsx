import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "pAIper - AI-Powered Research Discovery",
  description: "An intelligent research tool that uses AI to generate optimized search queries, discover academic papers from Google Scholar and Scopus, and create comprehensive research reports with APA citations.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg"
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Immediate hydration fix for browser extensions
              (function() {
                function cleanExtensionAttributes() {
                  const html = document.documentElement;
                  const attrs = ['data-lt-installed', 'data-grammarly-extension-installed', 'data-new-gr-c-s-check-loaded', 'data-gr-ext-installed'];
                  attrs.forEach(attr => html.removeAttribute(attr));
                }
                
                // Run immediately
                cleanExtensionAttributes();
                
                // Run when DOM is ready
                if (document.readyState === 'loading') {
                  document.addEventListener('DOMContentLoaded', cleanExtensionAttributes);
                } else {
                  cleanExtensionAttributes();
                }
              })();
            `
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning={true}
      >
        {children}
      </body>
    </html>
  );
}
