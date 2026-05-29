import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "模联代表写作一致性分析器",
  description: "分析新文本与代表历史写作风格画像之间的一致性偏离"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
