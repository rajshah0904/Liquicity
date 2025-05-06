"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importDefault(require("react"));
const ui_1 = require("../ui");
const utils_1 = require("@/app/lib/utils");
const TransactionTable = ({ transactions, isLoading, onViewDetails }) => {
    // Status badge variants
    const getStatusBadge = (status) => {
        switch (status) {
            case 'completed':
                return <ui_1.Badge variant="success">Completed</ui_1.Badge>;
            case 'pending':
                return <ui_1.Badge variant="warning">Pending</ui_1.Badge>;
            case 'failed':
                return <ui_1.Badge variant="error">Failed</ui_1.Badge>;
            default:
                return <ui_1.Badge variant="default">{status}</ui_1.Badge>;
        }
    };
    // Type badge variants
    const getTypeBadge = (type) => {
        switch (type) {
            case 'domestic':
                return <ui_1.Badge variant="outline">Domestic</ui_1.Badge>;
            case 'international':
                return <ui_1.Badge variant="outline" color="blue">International</ui_1.Badge>;
            default:
                return <ui_1.Badge variant="outline">{type}</ui_1.Badge>;
        }
    };
    // Loading skeleton
    if (isLoading) {
        return (<div className="w-full">
        <ui_1.Skeleton className="h-10 w-full mb-4"/>
        {[...Array(5)].map((_, i) => (<ui_1.Skeleton key={i} className="h-16 w-full mb-2"/>))}
      </div>);
    }
    // Empty state
    if (transactions.length === 0) {
        return (<div className="text-center py-10">
        <p className="text-gray-500 mb-4">No transactions found</p>
        <p className="text-sm text-gray-400">
          Try changing your filters or create a new transaction
        </p>
      </div>);
    }
    return (<ui_1.Table>
      <ui_1.Table.Header>
        <ui_1.Table.Row>
          <ui_1.Table.HeaderCell>Date</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Amount</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Status</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Type</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Route</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Recipient</ui_1.Table.HeaderCell>
          <ui_1.Table.HeaderCell>Actions</ui_1.Table.HeaderCell>
        </ui_1.Table.Row>
      </ui_1.Table.Header>
      <ui_1.Table.Body>
        {transactions.map((transaction) => (<ui_1.Table.Row key={transaction.id}>
            <ui_1.Table.Cell>{(0, utils_1.formatDate)(transaction.date)}</ui_1.Table.Cell>
            <ui_1.Table.Cell>
              {(0, utils_1.formatCurrency)(transaction.amount, transaction.currency)}
            </ui_1.Table.Cell>
            <ui_1.Table.Cell>{getStatusBadge(transaction.status)}</ui_1.Table.Cell>
            <ui_1.Table.Cell>{getTypeBadge(transaction.type)}</ui_1.Table.Cell>
            <ui_1.Table.Cell>
              {transaction.sourceCountry} → {transaction.destinationCountry}
            </ui_1.Table.Cell>
            <ui_1.Table.Cell>{transaction.recipient}</ui_1.Table.Cell>
            <ui_1.Table.Cell>
              {onViewDetails && (<ui_1.Button variant="ghost" size="sm" onClick={() => onViewDetails(transaction.id)}>
                  View
                </ui_1.Button>)}
            </ui_1.Table.Cell>
          </ui_1.Table.Row>))}
      </ui_1.Table.Body>
    </ui_1.Table>);
};
exports.default = TransactionTable;
