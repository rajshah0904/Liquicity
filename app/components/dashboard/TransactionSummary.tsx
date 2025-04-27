import React from 'react';
import { Card } from '../ui';
import { formatCurrency } from '@/app/lib/utils';

interface TransactionSummaryProps {
  totalTransactions: number;
  pendingTransactions: number;
  completedTransactions: number;
  failedTransactions: number;
  totalVolume: number;
  currency?: string;
}

const TransactionSummary: React.FC<TransactionSummaryProps> = ({
  totalTransactions,
  pendingTransactions,
  completedTransactions,
  failedTransactions,
  totalVolume,
  currency = 'USD'
}) => {
  // Calculate completion rate
  const completionRate = totalTransactions > 0 
    ? Math.round((completedTransactions / totalTransactions) * 100) 
    : 0;
    
  // Calculate failure rate
  const failureRate = totalTransactions > 0 
    ? Math.round((failedTransactions / totalTransactions) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="p-4">
        <div className="flex flex-col">
          <span className="text-sm text-gray-500 font-medium">Total Volume</span>
          <span className="text-2xl font-bold mt-1">
            {formatCurrency(totalVolume, currency)}
          </span>
          <span className="text-xs text-gray-400 mt-1">
            Across {totalTransactions} transaction{totalTransactions !== 1 ? 's' : ''}
          </span>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex flex-col">
          <span className="text-sm text-gray-500 font-medium">Completed</span>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold mt-1 text-green-600">
              {completedTransactions}
            </span>
            <span className="text-sm text-green-600 mb-1">
              ({completionRate}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              className="bg-green-600 h-2 rounded-full" 
              style={{ width: `${completionRate}%` }}
            />
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex flex-col">
          <span className="text-sm text-gray-500 font-medium">Pending</span>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold mt-1 text-amber-500">
              {pendingTransactions}
            </span>
            {pendingTransactions > 0 && (
              <span className="text-sm text-amber-500 mb-1">
                ({Math.round((pendingTransactions / totalTransactions) * 100)}%)
              </span>
            )}
          </div>
          <span className="text-xs text-gray-400 mt-1">
            {pendingTransactions > 0 ? 'Awaiting settlement' : 'No pending transactions'}
          </span>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex flex-col">
          <span className="text-sm text-gray-500 font-medium">Failed</span>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold mt-1 text-red-600">
              {failedTransactions}
            </span>
            {failedTransactions > 0 && (
              <span className="text-sm text-red-600 mb-1">
                ({failureRate}%)
              </span>
            )}
          </div>
          {failureRate > 10 && (
            <span className="text-xs text-red-500 mt-1">
              High failure rate - review transactions
            </span>
          )}
          {failureRate <= 10 && failureRate > 0 && (
            <span className="text-xs text-gray-400 mt-1">
              Within acceptable range
            </span>
          )}
          {failureRate === 0 && (
            <span className="text-xs text-gray-400 mt-1">
              No failed transactions
            </span>
          )}
        </div>
      </Card>
    </div>
  );
};

export default TransactionSummary; 