import React,{useState} from 'react';
import { apiFetch } from '../../lib/api';
import { useRouter } from 'next/router';

export default function RequestPage(){
  const [amount,setAmount]=useState('');
  const [note,setNote]=useState('');
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState<string|null>(null);
  const router=useRouter();
  async function submit(e:any){e.preventDefault();setLoading(true);setError(null);try{await apiFetch('/requests',{method:'POST',body:JSON.stringify({amount,note})});alert('Request sent');router.push('/dashboard');}catch(err:any){setError(err.message);}finally{setLoading(false);} }
  return(
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded-lg shadow">
      <h1 className="text-xl font-semibold mb-4">Request Money</h1>
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2 rounded" placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
        <textarea className="w-full border p-2 rounded" placeholder="Note (optional)" value={note} onChange={e=>setNote(e.target.value)} />
        <button disabled={loading} className="w-full bg-primary text-white p-2 rounded">{loading?'Sending...':'Send Request'}</button>
      </form>
    </div>
  );
} 