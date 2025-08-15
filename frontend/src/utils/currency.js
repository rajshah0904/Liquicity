export const CURRENCY_SYMBOLS = {
  USD: '$',    // United States
  EUR: '€',    // European Union
  MXN: 'MX$',  // Mexico
  COP: 'COP$', // Colombia
  BRL: 'R$',   // Brazil
  ARS: 'AR$',  // Argentina
  PEN: 'S/'    // Peru
};

export const getCurrencySymbol = (currencyCode) => {
  if (!currencyCode) return '$';
  const code = String(currencyCode).toUpperCase();
  return CURRENCY_SYMBOLS[code] || '$';
};

export const formatCurrency = (amount, currencyCode = 'USD', opts = {}) => {
  const { minimumFractionDigits = 2, maximumFractionDigits = 2, locale = 'en-US' } = opts;
  const symbol = getCurrencySymbol(currencyCode);
  const number = Number(amount || 0);
  const formatted = number.toLocaleString(locale, { minimumFractionDigits, maximumFractionDigits });
  return `${symbol}${formatted}`;
}; 