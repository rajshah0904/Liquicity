import { useState, useEffect, useCallback } from 'react';

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

interface TransactionSummary {
  total: number;
  pending: number;
  completed: number;
  failed: number;
  domesticCount: number;
  internationalCount: number;
  volume: number;
}

interface FilterOptions {
  status: string;
  type: string;
  dateFrom: string;
  dateTo: string;
  searchTerm: string;
  sortOrder: string;
}

interface UseTrxnHookResult {
  transactions: Transaction[];
  isLoading: boolean;
  error: string | null;
  summary: TransactionSummary;
  totalPages: number;
  currentPage: number;
  refresh: () => Promise<void>;
}

export function useTransactions(
  tab: string = 'all',
  filters: FilterOptions,
  page: number = 1,
  pageSize: number = 10
): UseTrxnHookResult {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<TransactionSummary>({
    total: 0,
    pending: 0,
    completed: 0,
    failed: 0,
    domesticCount: 0,
    internationalCount: 0,
    volume: 0,
  });
  const [totalPages, setTotalPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(page);

  // Adjust filters based on active tab
  const getAdjustedFilters = useCallback(() => {
    let adjustedFilters = { ...filters };
    
    // Override type filter based on tab
    if (tab === 'domestic') {
      adjustedFilters.type = 'domestic';
    } else if (tab === 'international') {
      adjustedFilters.type = 'international';
    }
    
    return adjustedFilters;
  }, [tab, filters]);

  const fetchTransactions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const adjustedFilters = getAdjustedFilters();
      
      // Build query string
      const queryParams = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString(),
        status: adjustedFilters.status,
        type: adjustedFilters.type,
        sortOrder: adjustedFilters.sortOrder,
        ...(adjustedFilters.dateFrom && { dateFrom: adjustedFilters.dateFrom }),
        ...(adjustedFilters.dateTo && { dateTo: adjustedFilters.dateTo }),
        ...(adjustedFilters.searchTerm && { search: adjustedFilters.searchTerm }),
      });
      
      const response = await fetch(`/api/transactions?${queryParams.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch transactions: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      setTransactions(data.transactions);
      setSummary(data.summary);
      setTotalPages(data.pagination.totalPages);
      setCurrentPage(data.pagination.currentPage);
    } catch (err: any) {
      console.error('Error fetching transactions:', err);
      setError(err.message || 'Failed to load transactions');
      setTransactions([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, getAdjustedFilters]);

  // Initial fetch and on dependencies change
  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return {
    transactions,
    isLoading,
    error,
    summary,
    totalPages,
    currentPage,
    refresh: fetchTransactions,
  };
} 