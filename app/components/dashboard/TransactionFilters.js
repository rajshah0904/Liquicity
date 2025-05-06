"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importDefault(require("react"));
const ui_1 = require("../ui");
const TransactionFilters = ({ filters, onChange, disableTypeFilter = false }) => {
    const handleChange = (key, value) => {
        onChange({ [key]: value });
    };
    const handleReset = () => {
        onChange({
            status: 'all',
            type: disableTypeFilter ? filters.type : 'all',
            dateFrom: '',
            dateTo: '',
            searchTerm: '',
            sortOrder: 'newest'
        });
    };
    return (<div className="bg-gray-50 p-4 rounded-lg mb-6">
      <div className="mb-4">
        <ui_1.TextField placeholder="Search transactions..." value={filters.searchTerm} onChange={(e) => handleChange('searchTerm', e.target.value)} className="w-full" icon="search" clearable onClear={() => handleChange('searchTerm', '')}/>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <ui_1.Select label="Status" value={filters.status} onChange={(e) => handleChange('status', e.target.value)}>
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </ui_1.Select>
        
        {!disableTypeFilter && (<ui_1.Select label="Type" value={filters.type} onChange={(e) => handleChange('type', e.target.value)}>
            <option value="all">All Types</option>
            <option value="domestic">Domestic</option>
            <option value="international">International</option>
          </ui_1.Select>)}
        
        <ui_1.Select label="Sort By" value={filters.sortOrder} onChange={(e) => handleChange('sortOrder', e.target.value)}>
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="amount-high">Amount (High to Low)</option>
          <option value="amount-low">Amount (Low to High)</option>
        </ui_1.Select>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ui_1.DatePicker label="From Date" value={filters.dateFrom} onChange={(date) => handleChange('dateFrom', date)} placeholder="Start date" maxDate={filters.dateTo ? new Date(filters.dateTo) : undefined}/>
        
        <ui_1.DatePicker label="To Date" value={filters.dateTo} onChange={(date) => handleChange('dateTo', date)} placeholder="End date" minDate={filters.dateFrom ? new Date(filters.dateFrom) : undefined} maxDate={new Date()}/>
      </div>
      
      <div className="flex justify-end">
        <ui_1.Button variant="outline" size="sm" onClick={handleReset}>
          Reset Filters
        </ui_1.Button>
      </div>
    </div>);
};
exports.default = TransactionFilters;
