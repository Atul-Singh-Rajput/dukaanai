import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DukaanAI | Smart Kirana Manager",
  description: "Apni dukaan, ab apni awaaz se chalao.",
  manifest: "/manifest.json",
  themeColor: "#176b45",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="hi">
      <body>{children}</body>
    </html>
  );
}
