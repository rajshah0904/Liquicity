"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.useTransactions = useTransactions;
const react_1 = require("react");
function useTransactions(tab = 'all', filters, page = 1, pageSize = 10) {
    const [transactions, setTransactions] = (0, react_1.useState)([]);
    const [isLoading, setIsLoading] = (0, react_1.useState)(true);
    const [error, setError] = (0, react_1.useState)(null);
    const [summary, setSummary] = (0, react_1.useState)({
        total: 0,
        pending: 0,
        completed: 0,
        failed: 0,
        domesticCount: 0,
        internationalCount: 0,
        volume: 0,
    });
    const [totalPages, setTotalPages] = (0, react_1.useState)(1);
    const [currentPage, setCurrentPage] = (0, react_1.useState)(page);
    // Adjust filters based on active tab
    const getAdjustedFilters = (0, react_1.useCallback)(() => {
        let adjustedFilters = Object.assign({}, filters);
        // Override type filter based on tab
        if (tab === 'domestic') {
            adjustedFilters.type = 'domestic';
        }
        else if (tab === 'international') {
            adjustedFilters.type = 'international';
        }
        return adjustedFilters;
    }, [tab, filters]);
    const fetchTransactions = (0, react_1.useCallback)(() => __awaiter(this, void 0, void 0, function* () {
        setIsLoading(true);
        setError(null);
        try {
            const adjustedFilters = getAdjustedFilters();
            // Build query string
            const queryParams = new URLSearchParams(Object.assign(Object.assign(Object.assign({ page: page.toString(), pageSize: pageSize.toString(), status: adjustedFilters.status, type: adjustedFilters.type, sortOrder: adjustedFilters.sortOrder }, (adjustedFilters.dateFrom && { dateFrom: adjustedFilters.dateFrom })), (adjustedFilters.dateTo && { dateTo: adjustedFilters.dateTo })), (adjustedFilters.searchTerm && { search: adjustedFilters.searchTerm })));
            const response = yield fetch(`/api/transactions?${queryParams.toString()}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch transactions: ${response.statusText}`);
            }
            const data = yield response.json();
            setTransactions(data.transactions);
            setSummary(data.summary);
            setTotalPages(data.pagination.totalPages);
            setCurrentPage(data.pagination.currentPage);
        }
        catch (err) {
            console.error('Error fetching transactions:', err);
            setError(err.message || 'Failed to load transactions');
            setTransactions([]);
        }
        finally {
            setIsLoading(false);
        }
    }), [page, pageSize, getAdjustedFilters]);
    // Initial fetch and on dependencies change
    (0, react_1.useEffect)(() => {
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
