import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function HowItWorks() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Head>
        <title>How Liquicity Works | Liquicity</title>
        <meta name="description" content="The digital wallet designed for everyone. Send money globally in minutes, not days, with better rates and lower fees." />
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
                <a className="text-white hover:text-gray-300 border-b-2 border-white">
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
        <section className="py-16 md:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-8">
              How Liquicity Works
            </h1>
            <p className="text-xl max-w-3xl mx-auto mb-16">
              The digital wallet designed for everyone. Send money globally in minutes, 
              not days, with better rates and lower fees.
            </p>
          </div>
        </section>

        <section className="py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold mb-16 text-center">
              Sending Money Globally in Four Simple Steps
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="bg-gray-900 rounded-lg p-6 text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
                <h3 className="text-xl font-semibold mb-4">Create an Account</h3>
                <p className="text-gray-400">Sign up in minutes with just your email and basic information. Our verification process is quick and painless.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6 text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
                <h3 className="text-xl font-semibold mb-4">Link Payment Method</h3>
                <p className="text-gray-400">Connect your bank account or debit card securely. We support multiple funding methods in various countries.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6 text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
                <h3 className="text-xl font-semibold mb-4">Enter Recipient Details</h3>
                <p className="text-gray-400">Provide your recipient's information. They'll get a notification when the funds are on the way.</p>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-6 text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">4</div>
                <h3 className="text-xl font-semibold mb-4">Send Money</h3>
                <p className="text-gray-400">Confirm the amount and exchange rate. Your recipient receives funds in as little as a few minutes.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-8">Ready to get started?</h2>
            <p className="text-xl max-w-2xl mx-auto mb-8">
              Join thousands of customers who are already using Liquicity to send money globally.
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