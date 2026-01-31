import './globals.css'

export const metadata = {
  title: 'Kalm - Your Recovery Companion',
  description: 'AI-powered support for addiction recovery',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
