'use client';

import { useAuth, UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();

  // Remove automatic redirect - let users see the home page first

  if (!isLoaded) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #000000, #1a1a1a, #000000)' }}
      >
        <div className="text-center">
          <div 
            className="animate-spin rounded-full h-12 w-12 mx-auto mb-4"
            style={{ 
              border: '4px solid rgba(74, 158, 255, 0.3)',
              borderTop: '4px solid #4A9EFF'
            }}
          ></div>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Loading CrawlMind...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen"
      style={{ background: 'linear-gradient(135deg, #000000, #1a1a1a, #000000)' }}
    >
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 relative">
              <Image
                src="/artificial-intelligence.png"
                alt="CrawlMind Logo"
                width={40}
                height={40}
                className="object-contain"
              />
            </div>
            <span 
              className="text-3xl font-bold"
              style={{ color: '#4A9EFF' }}
            >
              CrawlMind
            </span>
          </div>
          
          <nav className="flex items-center space-x-4">
            {isSignedIn ? (
              <>
                <Link 
                  href="/dashboard" 
                  className="px-4 py-2 font-medium transition-colors duration-200"
                  style={{ color: '#4A9EFF' }}
                  onMouseEnter={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.color = '#87CEEB'
                  }}
                  onMouseLeave={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.color = '#4A9EFF'
                  }}
                >
                  Dashboard
                </Link>
                <UserButton afterSignOutUrl="/" />
              </>
            ) : (
              <>
                <Link 
                  href="/sign-in" 
                  className="px-4 py-2 font-medium transition-colors duration-200"
                  style={{ color: '#4A9EFF' }}
                  onMouseEnter={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.color = '#87CEEB'
                  }}
                  onMouseLeave={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.color = '#4A9EFF'
                  }}
                >
                  Sign In
                </Link>
                <Link 
                  href="/sign-up" 
                  className="px-6 py-3 font-semibold rounded-xl transition-all duration-300 shadow-lg"
                  style={{ 
                    background: 'linear-gradient(135deg, #4A9EFF, #2d7fff)',
                    color: '#ffffff'
                  }}
                  onMouseEnter={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.background = 'linear-gradient(135deg, #2d7fff, #1e5ba8)'
                    target.style.transform = 'translateY(-2px) scale(1.02)'
                    target.style.boxShadow = '0 12px 35px rgba(74, 158, 255, 0.4)'
                  }}
                  onMouseLeave={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.background = 'linear-gradient(135deg, #4A9EFF, #2d7fff)'
                    target.style.transform = 'translateY(0) scale(1)'
                    target.style.boxShadow = '0 8px 25px rgba(74, 158, 255, 0.25)'
                  }}
                >
                  Sign Up
                </Link>
              </>
            )}
          </nav>
        </header>

        {/* Main Content */}
        <main>
          <div className="max-w-4xl mx-auto text-center">
            <h1 
              className="text-6xl font-bold mb-6"
              style={{ color: '#ffffff' }}
            >
              AI-Powered Document Analysis
            </h1>
            <p 
              className="text-xl mb-10 leading-relaxed"
              style={{ color: 'rgba(255, 255, 255, 0.8)' }}
            >
              Upload documents, crawl websites, and chat with AI to extract insights from your content. 
              CrawlMind combines advanced web crawling with intelligent document processing.
            </p>
            
            <div className="flex justify-center space-x-6 mb-16">
              {!isSignedIn ? (
                <>
                  <Link 
                    href="/sign-up" 
                    className="px-8 py-4 font-bold text-lg rounded-lg transition-all duration-300 shadow-lg"
                    style={{ 
                      background: 'linear-gradient(135deg, #4A9EFF, #2d7fff)',
                      color: '#ffffff'
                    }}
                    onMouseEnter={(e) => {
                      const target = e.target as HTMLAnchorElement
                      target.style.background = 'linear-gradient(135deg, #2d7fff, #1e5ba8)'
                      target.style.transform = 'translateY(-2px) scale(1.02)'
                      target.style.boxShadow = '0 12px 35px rgba(74, 158, 255, 0.4)'
                    }}
                    onMouseLeave={(e) => {
                      const target = e.target as HTMLAnchorElement
                      target.style.background = 'linear-gradient(135deg, #4A9EFF, #2d7fff)'
                      target.style.transform = 'translateY(0) scale(1)'
                      target.style.boxShadow = '0 8px 25px rgba(74, 158, 255, 0.25)'
                    }}
                  >
                    Get Started Free
                  </Link>
                  <Link 
                    href="/sign-in" 
                    className="px-8 py-4 font-bold text-lg rounded-lg transition-all duration-300 shadow-lg"
                    style={{ 
                      background: 'rgba(0, 0, 0, 0.8)',
                      color: '#4A9EFF',
                      border: '2px solid #4A9EFF'
                    }}
                    onMouseEnter={(e) => {
                      const target = e.target as HTMLAnchorElement
                      target.style.background = 'rgba(74, 158, 255, 0.1)'
                      target.style.transform = 'translateY(-2px) scale(1.02)'
                      target.style.boxShadow = '0 12px 35px rgba(74, 158, 255, 0.3)'
                    }}
                    onMouseLeave={(e) => {
                      const target = e.target as HTMLAnchorElement
                      target.style.background = 'rgba(0, 0, 0, 0.8)'
                      target.style.transform = 'translateY(0) scale(1)'
                      target.style.boxShadow = '0 8px 25px rgba(74, 158, 255, 0.15)'
                    }}
                  >
                    Sign In
                  </Link>
                </>
              ) : (
                <Link 
                  href="/dashboard" 
                  className="px-8 py-4 font-bold text-lg rounded-lg transition-all duration-300 shadow-lg"
                  style={{ 
                    background: 'linear-gradient(135deg, #4A9EFF, #2d7fff)',
                    color: '#ffffff'
                  }}
                  onMouseEnter={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.background = 'linear-gradient(135deg, #2d7fff, #1e5ba8)'
                    target.style.transform = 'translateY(-2px) scale(1.02)'
                    target.style.boxShadow = '0 12px 35px rgba(74, 158, 255, 0.4)'
                  }}
                  onMouseLeave={(e) => {
                    const target = e.target as HTMLAnchorElement
                    target.style.background = 'linear-gradient(135deg, #4A9EFF, #2d7fff)'
                    target.style.transform = 'translateY(0) scale(1)'
                    target.style.boxShadow = '0 8px 25px rgba(74, 158, 255, 0.25)'
                  }}
                >
                  Open Dashboard
                </Link>
              )}
            </div>

            {/* Feature Grid */}
            <div className="grid md:grid-cols-3 gap-8 mb-16">
              <div 
                className="p-8 rounded-xl shadow-lg backdrop-blur-sm transition-all duration-300"
                style={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: '1px solid rgba(74, 158, 255, 0.3)'
                }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.6)'
                  target.style.transform = 'translateY(-5px)'
                  target.style.boxShadow = '0 20px 40px rgba(74, 158, 255, 0.15)'
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.3)'
                  target.style.transform = 'translateY(0)'
                  target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)'
                }}
              >
                <div style={{ color: '#4A9EFF' }} className="text-4xl mb-4">🕷️</div>
                <h3 className="text-xl font-semibold mb-4" style={{ color: '#ffffff' }}>Smart Web Crawling</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Advanced crawling with JavaScript execution, CSS selectors, and intelligent content extraction.
                </p>
              </div>
              <div 
                className="p-8 rounded-xl shadow-lg backdrop-blur-sm transition-all duration-300"
                style={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: '1px solid rgba(74, 158, 255, 0.3)'
                }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.6)'
                  target.style.transform = 'translateY(-5px)'
                  target.style.boxShadow = '0 20px 40px rgba(74, 158, 255, 0.15)'
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.3)'
                  target.style.transform = 'translateY(0)'
                  target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)'
                }}
              >
                <div style={{ color: '#4A9EFF' }} className="text-4xl mb-4">📄</div>
                <h3 className="text-xl font-semibold mb-4" style={{ color: '#ffffff' }}>Document Processing</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Upload PDFs, text files, and more. Our AI extracts and understands your content.
                </p>
              </div>
              <div 
                className="p-8 rounded-xl shadow-lg backdrop-blur-sm transition-all duration-300"
                style={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: '1px solid rgba(74, 158, 255, 0.3)'
                }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.6)'
                  target.style.transform = 'translateY(-5px)'
                  target.style.boxShadow = '0 20px 40px rgba(74, 158, 255, 0.15)'
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLDivElement
                  target.style.borderColor = 'rgba(74, 158, 255, 0.3)'
                  target.style.transform = 'translateY(0)'
                  target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)'
                }}
              >
                <div style={{ color: '#4A9EFF' }} className="text-4xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold mb-4" style={{ color: '#ffffff' }}>AI Chat Interface</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Chat with your documents using Google Gemini AI. Ask questions, get summaries, and insights.
                </p>
              </div>
            </div>

            {/* Tech Stack */}
            <div 
              className="rounded-xl shadow-lg p-8 backdrop-blur-sm"
              style={{ 
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: '1px solid rgba(74, 158, 255, 0.3)'
              }}
            >
              <h3 className="text-2xl font-semibold mb-6" style={{ color: '#ffffff' }}>Powered by Modern Tech</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex flex-col items-center">
                  <span className="font-semibold" style={{ color: '#4A9EFF' }}>Next.js</span>
                  <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Frontend</span>
                </div>
                <div className="flex flex-col items-center">
                  <span className="font-semibold" style={{ color: '#4A9EFF' }}>FastAPI</span>
                  <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Backend</span>
                </div>
                <div className="flex flex-col items-center">
                  <span className="font-semibold" style={{ color: '#4A9EFF' }}>Google Gemini</span>
                  <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>AI Engine</span>
                </div>
                <div className="flex flex-col items-center">
                  <span className="font-semibold" style={{ color: '#4A9EFF' }}>ChromaDB</span>
                  <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Vector Database</span>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-20 text-center" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          <p>&copy; 2025 CrawlMind. Built with ❤️ for intelligent document processing.</p>
        </footer>
      </div>
    </div>
  );
}
