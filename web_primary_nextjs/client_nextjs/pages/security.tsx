import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Security() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Head>
        <title>Security | Liquicity</title>
        <meta name="description" content="We've built Liquicity with bank-grade security to protect your money and personal information at all times." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <Link href="/">
                <a>
                  <h1 className="text-2xl font-bold">Liquicity</h1>
                </a>
              </Link>
            </div>
            <nav className="flex space-x-8">
              <Link href="/">
                <a className="text-white hover:text-gray-300">
                  Home
                </a>
              </Link>
              <Link href="/how-it-works">
                <a className="text-white hover:text-gray-300">
                  How it works
                </a>
              </Link>
              <Link href="/security">
                <a className="text-white hover:text-gray-300 border-b-2 border-white">
                  Security
                </a>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main>
        <section className="py-16 md:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="flex justify-center mb-8">
              <svg className="w-24 h-24 text-blue-500" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
              </svg>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-8">
              Your Money, Protected
            </h1>
            <p className="text-xl max-w-3xl mx-auto">
              We've built Liquicity with bank-grade security to protect your money and
              personal information at all times.
            </p>
          </div>
        </section>

        <section className="py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">End-to-End Encryption</h3>
                <p className="text-gray-400">All your personal and financial information is encrypted using state-of-the-art encryption standards. Your data is never stored in plain text.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">Fraud Protection</h3>
                <p className="text-gray-400">Our advanced systems monitor transactions 24/7 to detect and prevent fraudulent activity before it affects your account.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">Biometric Authentication</h3>
                <p className="text-gray-400">Access your account using fingerprint or facial recognition for an extra layer of security beyond traditional passwords.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">Regulatory Compliance</h3>
                <p className="text-gray-400">We adhere to global financial regulations and standards, including KYC and AML requirements, to ensure safe and legal transactions.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">Secure Mobile App</h3>
                <p className="text-gray-400">Our mobile application is built with security-first principles, including local data encryption and secure communication channels.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-4">Real-time Alerts</h3>
                <p className="text-gray-400">Get instant notifications about account activity, so you're always informed about transactions and can quickly respond to unauthorized actions.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-8">Your trust is our priority</h2>
            <p className="text-xl max-w-2xl mx-auto mb-8">
              We invest heavily in security infrastructure so you can send money with confidence.
            </p>
            <Link href="/">
              <a className="inline-block bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-md font-medium text-lg">
                Join the waitlist
              </a>
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
} 