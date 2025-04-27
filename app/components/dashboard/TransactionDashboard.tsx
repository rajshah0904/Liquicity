import React, { useState, useEffect } from 'react';
import { Card, Tabs, Tab, Button, Badge, Pagination } from '../ui';
import TransactionTable from './TransactionTable';
import TransactionSummary from './TransactionSummary';
import TransactionFilters from './TransactionFilters';
import { useTransactions } from '@/app/hooks/useTransactions';

type TransactionStatus = 'all' | 'pending' | 'completed' | 'failed';
type TransactionType = 'all' | 'domestic' | 'international';
type SortOrder = 'newest' | 'oldest' | 'amount-high' | 'amount-low';

const TransactionDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState({
    status: 'all' as TransactionStatus,
    type: 'all' as TransactionType,
    dateFrom: '',
    dateTo: '',
    searchTerm: '',
    sortOrder: 'newest' as SortOrder
  });

  const { 
    transactions, 
    isLoading, 
    error, 
    summary, 
    refresh,
    totalPages
  } = useTransactions(activeTab, filters, currentPage);

  // Refresh data when filters or page changes
  useEffect(() => {
    refresh();
  }, [filters, currentPage, activeTab, refresh]);

  const handleTabChange = (tabKey: string) => {
    setActiveTab(tabKey);
    setCurrentPage(1);
  };

  const handleFilterChange = (newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleRefresh = () => {
    refresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      <TransactionSummary 
        totalTransactions={summary.total}
        pendingTransactions={summary.pending}
        completedTransactions={summary.completed}
        failedTransactions={summary.failed}
        totalVolume={summary.volume}
      />

      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={handleTabChange}
          className="px-4 pt-4"
        >
          <Tab key="all" title="All Transactions">
            <div className="p-4">
              <TransactionFilters
                filters={filters}
                onChange={handleFilterChange}
              />
              
              {error ? (
                <div className="text-center py-8">
                  <p className="text-red-500">{error}</p>
                  <Button onClick={handleRefresh} variant="outline" className="mt-4">
                    Try Again
                  </Button>
                </div>
              ) : (
                <>
                  <TransactionTable 
                    transactions={transactions}
                    isLoading={isLoading}
                  />
                  
                  {totalPages > 1 && (
                    <div className="mt-4 flex justify-center">
                      <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={handlePageChange}
                      />
                    </div>
                  )}
                </>
              )}
            </div>
          </Tab>
          
          <Tab key="domestic" title={<>Domestic <Badge variant="outline">{summary.domesticCount}</Badge></>}>
            <div className="p-4">
              <TransactionFilters
                filters={{...filters, type: 'domestic'}}
                onChange={handleFilterChange}
                disableTypeFilter
              />
              
              <TransactionTable 
                transactions={transactions}
                isLoading={isLoading}
              />
              
              {totalPages > 1 && (
                <div className="mt-4 flex justify-center">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              )}
            </div>
          </Tab>
          
          <Tab key="international" title={<>International <Badge variant="outline">{summary.internationalCount}</Badge></>}>
            <div className="p-4">
              <TransactionFilters
                filters={{...filters, type: 'international'}}
                onChange={handleFilterChange}
                disableTypeFilter
              />
              
              <TransactionTable 
                transactions={transactions}
                isLoading={isLoading}
              />
              
              {totalPages > 1 && (
                <div className="mt-4 flex justify-center">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              )}
            </div>
          </Tab>
        </Tabs>
      </Card>
    </div>
  );
};

export default TransactionDashboard; 