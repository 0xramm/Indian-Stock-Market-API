import assert from 'node:assert';
import {
  determineExchange,
  formatCurrency,
  formatMarketCap,
  formatVolume,
  formatPercentage,
  formatRatio,
  searchInCache,
} from '../src/format.js';

// determineExchange
assert.deepStrictEqual(determineExchange('itc'), ['ITC', '.NS']);
assert.deepStrictEqual(determineExchange('itc.ns'), ['ITC', '.NS']);
assert.deepStrictEqual(determineExchange('itc.bo'), ['ITC', '.BO']);

// formatCurrency
assert.deepStrictEqual(formatCurrency(445.505, true), { value: 445.51, unit: 'INR' });
assert.strictEqual(formatCurrency(445.505, false), 445.51);
assert.deepStrictEqual(formatCurrency(null, true), { value: 'N/A', unit: 'INR' });

// formatMarketCap crore/lakh boundaries
assert.deepStrictEqual(formatMarketCap(5567894500000, true), { value: 556789.45, unit: 'Crores INR' });
assert.deepStrictEqual(formatMarketCap(250000, true), { value: 2.5, unit: 'Lakhs INR' });
assert.deepStrictEqual(formatMarketCap(5000, true), { value: 5000, unit: 'INR' });

// formatVolume
assert.deepStrictEqual(formatVolume(52345670, true), { value: 5.23, unit: 'Crores Shares' });
assert.strictEqual(formatVolume(52345670, false), 52345670);

// formatPercentage / formatRatio
assert.deepStrictEqual(formatPercentage(0.5199, true), { value: 0.52, unit: '%' });
assert.deepStrictEqual(formatRatio(0, true), { value: 'N/A', unit: 'x' });
assert.deepStrictEqual(formatRatio(28.451, true), { value: 28.45, unit: 'x' });

// searchInCache
assert.deepStrictEqual(
  searchInCache('reliance').map((r) => r.symbol),
  ['RELIANCE']
);
assert.ok(searchInCache('tata').some((r) => r.symbol === 'TCS'));

console.log('selfcheck: all assertions passed');
