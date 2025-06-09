import React, { useState } from 'react';
import { apiFetch } from '../../lib/api';
import { useRouter } from 'next/router';

export default function DepositPage(){
  const [amount,setAmount]=useState('');
  const [bankId,setBankId]=useState('');
  const [currency,setCurrency]=useState('usd');
  const [instant,setInstant]=useState(false);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState<string|null>(null);
  const router=useRouter();
  async function submit(e:any){e.preventDefault();setLoading(true);setError(null);try{await apiFetch('/transfer/deposit',{method:'POST',body:JSON.stringify({amount,currency,external_account_id:bankId,instant})});alert('Deposit initiated');router.push('/dashboard');}catch(err:any){setError(err.message);}finally{setLoading(false);} }
  return(
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded-lg shadow">
      <h1 className="text-xl font-semibold mb-4">Deposit Funds</h1>
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2 rounded" placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
        <select className="w-full border p-2 rounded" value={currency} onChange={e=>setCurrency(e.target.value)}>
          <option value="usd">USD</option><option value="eur">EUR</option><option value="mxn">MXN</option>
        </select>
        <input className="w-full border p-2 rounded" placeholder="External Account ID" value={bankId} onChange={e=>setBankId(e.target.value)} />
        <label className="flex items-center space-x-2"><input type="checkbox" checked={instant} onChange={e=>setInstant(e.target.checked)} /><span>Instant (1% fee)</span></label>
        <button disabled={loading} className="w-full bg-primary text-white p-2 rounded">{loading?'Processing...':'Deposit'}</button>
      </form>
    </div>
  );
} 