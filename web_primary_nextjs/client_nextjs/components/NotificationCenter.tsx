import React, { useEffect, useState } from 'react';
import { apiFetch } from '../lib/api';

interface Notification {
  id: string;
  type: 'send' | 'request';
  message: string;
  created_at: string;
}

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await apiFetch('/notifications');
        setNotifications(data.notifications || []);
      } catch (err) {
        console.error(err);
      }
    }
    fetchData();
  }, []);

  if (!notifications.length) return null;

  return (
    <div className="mt-6 bg-white shadow rounded-lg p-4 max-h-80 overflow-y-auto">
      <h2 className="text-lg font-medium text-gray-900 mb-2">Notifications</h2>
      <ul className="divide-y divide-gray-200">
        {notifications.map(n => (
          <li key={n.id} className="py-2 text-sm text-gray-700">
            <span className="font-semibold capitalize mr-1">{n.type}</span>
            {n.message}
            <span className="block text-xs text-gray-400">{new Date(n.created_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
} 