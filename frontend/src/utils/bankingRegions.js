// Banking regions configuration for bank account linking
export const BANKING_REGIONS = {
  us: {
    name: 'United States',
    code: 'US',
    currency: 'USD',
    currencySymbol: '$',
    methods: ['plaid'] // Only Plaid for US
  },
  eu: {
    name: 'European Union',
    code: 'EU', 
    currency: 'EUR',
    currencySymbol: '€',
    methods: ['plaid_eu', 'manual'] // Plaid EU or manual entry
  }
};

// SEPA countries that use IBAN for the dropdown
export const SEPA_COUNTRIES = [
  { name: 'Andorra', code: 'AND' },
  { name: 'Austria', code: 'AUT' },
  { name: 'Belgium', code: 'BEL' },
  { name: 'Bulgaria', code: 'BGR' },
  { name: 'Croatia', code: 'HRV' },
  { name: 'Cyprus', code: 'CYP' },
  { name: 'Czech Republic', code: 'CZE' },
  { name: 'Denmark', code: 'DNK' },
  { name: 'Estonia', code: 'EST' },
  { name: 'Finland', code: 'FIN' },
  { name: 'France', code: 'FRA' },
  { name: 'Germany', code: 'DEU' },
  { name: 'Greece', code: 'GRC' },
  { name: 'Hungary', code: 'HUN' },
  { name: 'Iceland', code: 'ISL' },
  { name: 'Ireland', code: 'IRL' },
  { name: 'Italy', code: 'ITA' },
  { name: 'Latvia', code: 'LVA' },
  { name: 'Liechtenstein', code: 'LIE' },
  { name: 'Lithuania', code: 'LTU' },
  { name: 'Luxembourg', code: 'LUX' },
  { name: 'Malta', code: 'MLT' },
  { name: 'Monaco', code: 'MCO' },
  { name: 'Netherlands', code: 'NLD' },
  { name: 'Norway', code: 'NOR' },
  { name: 'Poland', code: 'POL' },
  { name: 'Portugal', code: 'PRT' },
  { name: 'Romania', code: 'ROU' },
  { name: 'San Marino', code: 'SMR' },
  { name: 'Slovakia', code: 'SVK' },
  { name: 'Slovenia', code: 'SVN' },
  { name: 'Spain', code: 'ESP' },
  { name: 'Sweden', code: 'SWE' },
  { name: 'Switzerland', code: 'CHE' },
  { name: 'Vatican City', code: 'VAT' }
];

// Method configurations
export const LINKING_METHODS = {
  plaid: {
    name: 'Connect with Plaid',
    description: 'Securely connect your US bank account',
    icon: 'link',
    requiresPlaidScript: true
  },
  plaid_eu: {
    name: 'Connect with Plaid',
    description: 'Securely connect your European bank account',
    icon: 'link', 
    requiresPlaidScript: true
  },
  manual: {
    name: 'Enter bank details manually',
    description: 'Manually enter your bank account information',
    icon: 'edit',
    requiresPlaidScript: false
  }
};

// Helper functions
export const getRegionConfig = (regionKey) => {
  return BANKING_REGIONS[regionKey] || BANKING_REGIONS.us;
};

export const getAvailableMethods = (regionKey) => {
  const region = getRegionConfig(regionKey);
  return region.methods.map(methodKey => ({
    key: methodKey,
    ...LINKING_METHODS[methodKey]
  }));
};

export const getCurrencySymbol = (currencyCode) => {
  switch (currencyCode?.toLowerCase()) {
    case 'usd': return '$';
    case 'eur': return '€';
    case 'gbp': return '£';
    case 'mxn': return '$';
    default: return '$';
  }
};

// Helper to get country code from country name
export const getCountryCodeFromName = (countryName) => {
  const country = SEPA_COUNTRIES.find(c => c.name === countryName);
  return country ? country.code : null;
}; 