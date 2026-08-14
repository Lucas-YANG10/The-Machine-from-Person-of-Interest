import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Machine: Manhattan",
  description:
    "An interactive, fully synthetic crime-involvement inference simulation inspired by speculative television interfaces.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
