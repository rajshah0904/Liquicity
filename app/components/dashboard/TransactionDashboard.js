"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
const ui_1 = require("../ui");
const TransactionTable_1 = __importDefault(require("./TransactionTable"));
const TransactionSummary_1 = __importDefault(require("./TransactionSummary"));
const TransactionFilters_1 = __importDefault(require("./TransactionFilters"));
const useTransactions_1 = require("@/app/hooks/useTransactions");
const TransactionDashboard = () => {
    const [activeTab, setActiveTab] = (0, react_1.useState)('all');
    const [currentPage, setCurrentPage] = (0, react_1.useState)(1);
    const [filters, setFilters] = (0, react_1.useState)({
        status: 'all',
        type: 'all',
        dateFrom: '',
        dateTo: '',
        searchTerm: '',
        sortOrder: 'newest'
    });
    const { transactions, isLoading, error, summary, refresh, totalPages } = (0, useTransactions_1.useTransactions)(activeTab, filters, currentPage);
    // Refresh data when filters or page changes
    (0, react_1.useEffect)(() => {
        refresh();
    }, [filters, currentPage, activeTab, refresh]);
    const handleTabChange = (tabKey) => {
        setActiveTab(tabKey);
        setCurrentPage(1);
    };
    const handleFilterChange = (newFilters) => {
        setFilters(prev => (Object.assign(Object.assign({}, prev), newFilters)));
        setCurrentPage(1);
    };
    const handlePageChange = (page) => {
        setCurrentPage(page);
    };
    const handleRefresh = () => {
        refresh();
    };
    return (<div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <ui_1.Button onClick={handleRefresh} variant="outline" size="sm">
          Refresh
        </ui_1.Button>
      </div>

      <TransactionSummary_1.default totalTransactions={summary.total} pendingTransactions={summary.pending} completedTransactions={summary.completed} failedTransactions={summary.failed} totalVolume={summary.volume}/>

      <ui_1.Card>
        <ui_1.Tabs activeKey={activeTab} onChange={handleTabChange} className="px-4 pt-4">
          <ui_1.Tab key="all" title="All Transactions">
            <div className="p-4">
              <TransactionFilters_1.default filters={filters} onChange={handleFilterChange}/>
              
              {error ? (<div className="text-center py-8">
                  <p className="text-red-500">{error}</p>
                  <ui_1.Button onClick={handleRefresh} variant="outline" className="mt-4">
                    Try Again
                  </ui_1.Button>
                </div>) : (<>
                  <TransactionTable_1.default transactions={transactions} isLoading={isLoading}/>
                  
                  {totalPages > 1 && (<div className="mt-4 flex justify-center">
                      <ui_1.Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange}/>
                    </div>)}
                </>)}
            </div>
          </ui_1.Tab>
          
          <ui_1.Tab key="domestic" title={<>Domestic <ui_1.Badge variant="outline">{summary.domesticCount}</ui_1.Badge></>}>
            <div className="p-4">
              <TransactionFilters_1.default filters={Object.assign(Object.assign({}, filters), { type: 'domestic' })} onChange={handleFilterChange} disableTypeFilter/>
              
              <TransactionTable_1.default transactions={transactions} isLoading={isLoading}/>
              
              {totalPages > 1 && (<div className="mt-4 flex justify-center">
                  <ui_1.Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange}/>
                </div>)}
            </div>
          </ui_1.Tab>
          
          <ui_1.Tab key="international" title={<>International <ui_1.Badge variant="outline">{summary.internationalCount}</ui_1.Badge></>}>
            <div className="p-4">
              <TransactionFilters_1.default filters={Object.assign(Object.assign({}, filters), { type: 'international' })} onChange={handleFilterChange} disableTypeFilter/>
              
              <TransactionTable_1.default transactions={transactions} isLoading={isLoading}/>
              
              {totalPages > 1 && (<div className="mt-4 flex justify-center">
                  <ui_1.Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange}/>
                </div>)}
            </div>
          </ui_1.Tab>
        </ui_1.Tabs>
      </ui_1.Card>
    </div>);
};
exports.default = TransactionDashboard;
