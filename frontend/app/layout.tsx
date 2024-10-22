import { Metadata } from "next";
import { SessionProvider } from "next-auth/react"
import { Toaster } from "sonner";

import { ThemeProvider } from "@/components/custom/theme-provider";

import "./globals.css";



export const metadata: Metadata = {
  metadataBase: new URL("https://chat.vercel.ai"),
  title: "Next.js Chatbot Template",
  description: "Next.js chatbot template using the AI SDK.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SessionProvider>
          <Toaster position="top-center" />
          <SessionProvider>
            {children}
          </SessionProvider>
          </SessionProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
