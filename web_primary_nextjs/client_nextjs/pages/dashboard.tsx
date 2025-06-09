import React,{useState,useEffect} from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { apiFetch } from '../lib/api';
import NotificationCenter from '../components/NotificationCenter';

// Mock data for the dashboard
const transactions = [
  { id: 1, date: new Date(), amount: '1,240.50', status: 'completed', type: 'deposit', route: 'bank', recipient: 'Self' },
  { id: 2, date: new Date(Date.now() - 86400000), amount: '540.00', status: 'pending', type: 'withdrawal', route: 'wallet', recipient: 'Self' },
  { id: 3, date: new Date(Date.now() - 172800000), amount: '2,100.00', status: 'completed', type: 'payment', route: 'chain', recipient: 'John Doe' },
  { id: 4, date: new Date(Date.now() - 259200000), amount: '350.75', status: 'failed', type: 'payment', route: 'chain', recipient: 'Alice Smith' },
];

// Helper functions for formatting
const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

const getStatusBadge = (status: string) => {
  const statusClasses = {
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status] || ''}`}>
      {status}
    </span>
  );
};

const getTypeBadge = (type: string) => {
  const typeClasses = {
    deposit: 'bg-blue-100 text-blue-800',
    withdrawal: 'bg-purple-100 text-purple-800',
    payment: 'bg-indigo-100 text-indigo-800',
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeClasses[type] || ''}`}>
      {type}
    </span>
  );
};

export default function Dashboard() {
  const [balance,setBalance]=useState<{total:number,available:number,pending:number}>({total:0,available:0,pending:0});
  useEffect(()=>{async function load(){try{const data=await apiFetch('/wallet/overview');let total=0;data.wallets.forEach((w:any)=>{total+=w.local_balance});setBalance({total,available:total,pending:0});}catch(e){console.error(e);} }load();},[]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Dashboard | Liquicity</title>
        <meta name="description" content="Liquicity Dashboard - Manage your payments and transactions" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-primary">Liquicity</h1>
              </div>
              <nav className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link href="/">
                  <a className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Home
                  </a>
                </Link>
                <Link href="/dashboard">
                  <a className="border-primary text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Dashboard
                  </a>
                </Link>
                <Link href="/payments">
                  <a className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Payments
                  </a>
                </Link>
                <Link href="/settings">
                  <a className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Settings
                  </a>
                </Link>
              </nav>
            </div>
            <div className="flex items-center">
              <button className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                Profile
              </button>
              <button className="ml-4 text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="py-10">
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
          <h1 className="text-2xl font-semibold text-gray-900 px-4 sm:px-0">Dashboard</h1>
          
          {/* Wallet Summary */}
          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-primary rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Balance</dt>
                      <dd className="text-xl font-semibold text-gray-900">{balance.total}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Available Balance</dt>
                      <dd className="text-xl font-semibold text-gray-900">{balance.available}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                      <dd className="text-xl font-semibold text-gray-900">{balance.pending}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-8 px-4 sm:px-0">
            <h2 className="text-lg font-medium text-gray-900">Quick Actions</h2>
            <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Link href="/payments/send">
                <a className="bg-white p-4 rounded-lg shadow text-center hover:bg-gray-50">
                  <svg className="h-8 w-8 text-primary mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  <span className="mt-2 block text-sm font-medium text-gray-900">Send</span>
                </a>
              </Link>
              <Link href="/payments/request">
                <a className="bg-white p-4 rounded-lg shadow text-center hover:bg-gray-50">
                  <svg className="h-8 w-8 text-primary mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span className="mt-2 block text-sm font-medium text-gray-900">Request</span>
                </a>
              </Link>
              <Link href="/wallet/deposit">
                <a className="bg-white p-4 rounded-lg shadow text-center hover:bg-gray-50">
                  <svg className="h-8 w-8 text-primary mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="mt-2 block text-sm font-medium text-gray-900">Deposit</span>
                </a>
              </Link>
              <Link href="/wallet/withdraw">
                <a className="bg-white p-4 rounded-lg shadow text-center hover:bg-gray-50">
                  <svg className="h-8 w-8 text-primary mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="mt-2 block text-sm font-medium text-gray-900">Withdraw</span>
                </a>
              </Link>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="mt-8 px-4 sm:px-0">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Recent Transactions</h2>
              <Link href="/transactions">
                <a className="text-sm font-medium text-primary hover:text-primary-600">
                  View all
                </a>
              </Link>
            </div>

            <div className="mt-4 bg-white shadow overflow-hidden sm:rounded-md">
              <ul role="list" className="divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <li key={transaction.id}>
                    <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className={`h-10 w-10 rounded-full flex items-center justify-center ${transaction.type === 'deposit' ? 'bg-green-100' : transaction.type === 'withdrawal' ? 'bg-red-100' : 'bg-blue-100'}`}>
                              {transaction.type === 'deposit' ? '↓' : transaction.type === 'withdrawal' ? '↑' : '→'}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)} {transaction.route === 'chain' ? `to ${transaction.recipient}` : ''}
                            </div>
                            <div className="text-sm text-gray-500">
                              {formatDate(transaction.date)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900 mr-4">
                            ${transaction.amount}
                          </div>
                          <div>
                            {getStatusBadge(transaction.status)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <NotificationCenter />
        </div>
      </main>
    </div>
  );
} 