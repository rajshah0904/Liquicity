import React, { useState, useEffect } from 'react';

export default function ApiTestBasic() {
  const [data, setData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/health')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(json => {
        setData(JSON.stringify(json, null, 2));
      })
      .catch(err => {
        setError(err.message);
      });
  }, []);

  if (error) {
    return (
      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <h1>API Connection Error</h1>
        <div style={{ color: 'red', padding: '10px', border: '1px solid red' }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>API Connection Test</h1>
      {data ? (
        <div style={{ 
          backgroundColor: '#f0fff0', 
          padding: '10px', 
          border: '1px solid green',
          borderRadius: '5px'
        }}>
          <h2>Connection Successful</h2>
          <pre>{data}</pre>
        </div>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
} 