import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle waitlist signup
    console.log('Email submitted:', email);
    // Reset form
    setEmail('');
    alert('Thanks for joining our waitlist!');
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Head>
        <title>Liquicity - Revolutionizing Cross-Border Payments</title>
        <meta name="description" content="Send money across borders faster, cheaper, and more securely than ever before." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Liquicity</h1>
            </div>
            <nav className="flex space-x-8">
              <Link href="/">
                <a className="text-white hover:text-gray-300 border-b-2 border-white">
                  Home
                </a>
              </Link>
              <Link href="/how-it-works">
                <a className="text-white hover:text-gray-300">
                  How it works
                </a>
              </Link>
              <Link href="/security">
                <a className="text-white hover:text-gray-300">
                  Security
                </a>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main>
        <section className="py-20 md:py-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-8">
              Revolutionizing Cross-Border Payments
            </h1>
            <p className="text-xl max-w-3xl mx-auto mb-12">
              Send money across borders faster, cheaper, and more securely than ever before.
            </p>
            
            <div className="flex flex-col items-center">
              <p className="mb-4">Join our waitlist to get early access</p>
              
              <form onSubmit={handleSubmit} className="flex w-full max-w-md mx-auto mb-8">
                <input
                  type="email"
                  placeholder="Enter your email address"
                  className="flex-grow px-4 py-2 bg-transparent border border-gray-600 rounded-l text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <button 
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-r font-medium flex items-center"
                >
                  Join
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </form>

              <Link href="/contact">
                <a className="flex items-center text-gray-400 hover:text-white">
                  Contact Us
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </a>
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
} 