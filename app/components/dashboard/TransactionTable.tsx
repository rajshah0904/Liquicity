import React from 'react';
import { Table, Badge, Button, Skeleton } from '../ui';
import { formatCurrency, formatDate } from '@/app/lib/utils';

interface Transaction {
  id: string;
  date: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  type: 'domestic' | 'international';
  sourceCountry: string;
  destinationCountry: string;
  paymentMethod: string;
  recipient: string;
}

interface TransactionTableProps {
  transactions: Transaction[];
  isLoading: boolean;
  onViewDetails?: (id: string) => void;
}

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  isLoading,
  onViewDetails
}) => {
  // Status badge variants
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">Completed</Badge>;
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'failed':
        return <Badge variant="error">Failed</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  // Type badge variants
  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'domestic':
        return <Badge variant="outline">Domestic</Badge>;
      case 'international':
        return <Badge variant="outline" color="blue">International</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="w-full">
        <Skeleton className="h-10 w-full mb-4" />
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full mb-2" />
        ))}
      </div>
    );
  }

  // Empty state
  if (transactions.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500 mb-4">No transactions found</p>
        <p className="text-sm text-gray-400">
          Try changing your filters or create a new transaction
        </p>
      </div>
    );
  }

  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Date</Table.HeaderCell>
          <Table.HeaderCell>Amount</Table.HeaderCell>
          <Table.HeaderCell>Status</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Route</Table.HeaderCell>
          <Table.HeaderCell>Recipient</Table.HeaderCell>
          <Table.HeaderCell>Actions</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {transactions.map((transaction) => (
          <Table.Row key={transaction.id}>
            <Table.Cell>{formatDate(transaction.date)}</Table.Cell>
            <Table.Cell>
              {formatCurrency(transaction.amount, transaction.currency)}
            </Table.Cell>
            <Table.Cell>{getStatusBadge(transaction.status)}</Table.Cell>
            <Table.Cell>{getTypeBadge(transaction.type)}</Table.Cell>
            <Table.Cell>
              {transaction.sourceCountry} → {transaction.destinationCountry}
            </Table.Cell>
            <Table.Cell>{transaction.recipient}</Table.Cell>
            <Table.Cell>
              {onViewDetails && (
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => onViewDetails(transaction.id)}
                >
                  View
                </Button>
              )}
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  );
};

export default TransactionTable; 