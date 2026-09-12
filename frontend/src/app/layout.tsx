import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI College Learning Assistant",
  description: "Next-generation college learning platform combining structured data, RAG, deterministic rules, and analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
