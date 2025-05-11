import React,{useState} from 'react';
import { apiFetch } from '../../lib/api';
import { useRouter } from 'next/router';

export default function WithdrawPage(){
  const [amount,setAmount]=useState('');
  const [bankId,setBankId]=useState('');
  const [currency,setCurrency]=useState('usd');
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState<string|null>(null);
  const router=useRouter();
  async function submit(e:any){e.preventDefault();setLoading(true);setError(null);try{await apiFetch('/transfer/withdraw',{method:'POST',body:JSON.stringify({amount,external_account_id:bankId,currency})});alert('Withdrawal initiated');router.push('/dashboard');}catch(err:any){setError(err.message);}finally{setLoading(false);} }
  return(
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded-lg shadow">
      <h1 className="text-xl font-semibold mb-4">Withdraw Funds</h1>
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2 rounded" placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
        <select className="w-full border p-2 rounded" value={currency} onChange={e=>setCurrency(e.target.value)}>
          <option value="usd">USD</option><option value="eur">EUR</option><option value="mxn">MXN</option>
        </select>
        <input className="w-full border p-2 rounded" placeholder="External Account ID" value={bankId} onChange={e=>setBankId(e.target.value)} />
        <button disabled={loading} className="w-full bg-primary text-white p-2 rounded">{loading?'Processing...':'Withdraw'}</button>
      </form>
    </div>
  );
} 