import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Writing Consistency Analysis",
  description: "Delegate writing consistency analysis platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}

