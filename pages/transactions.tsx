import React,{useEffect,useState} from 'react';
import { apiFetch } from '../lib/api';
import Link from 'next/link';

interface Txn {transaction_id:string;amount:string;currency:string;description:string;date:string}

export default function TransactionsPage(){
  const [txns,setTxns]=useState<Txn[]>([]);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{async function load(){try{const data=await apiFetch('/wallet/transactions');setTxns(data.transactions);}catch(e){console.error(e);}finally{setLoading(false);} }load();},[]);
  return(
    <div className="max-w-4xl mx-auto mt-10">
      <h1 className="text-2xl font-semibold mb-4">Transaction History</h1>
      {loading? <p>Loading...</p> : (
        <table className="min-w-full divide-y divide-gray-200 bg-white shadow rounded">
          <thead className="bg-gray-50"><tr><th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th><th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th></tr></thead>
          <tbody className="divide-y divide-gray-200">
            {txns.map(t=>(<tr key={t.transaction_id}><td className="px-4 py-2 text-sm text-gray-600">{new Date(t.date).toLocaleString()}</td><td className="px-4 py-2 text-sm text-gray-600">{t.description}</td><td className="px-4 py-2 text-sm text-gray-900 text-right">{t.amount} {t.currency.toUpperCase()}</td></tr>))}
          </tbody>
        </table>
      )}
      <Link href="/dashboard"><a className="mt-4 inline-block text-primary">← Back to Dashboard</a></Link>
    </div>
  );
} 