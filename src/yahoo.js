// Talks to Yahoo Finance's public JSON endpoints via fetch — no extra dependencies.
// Confirmed against a live curl: /v8/finance/chart and /v1/finance/search need no
// auth; /v10/finance/quoteSummary and /v7/finance/quote need a crumb obtained from
// a short cookie handshake (same trick yfinance uses).

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';

// ponytail: module-scope cache, shared only within one running instance.
// Good enough since crumbs are cheap to refetch on a miss; move to a shared
// store if that churn makes the 401-retry path noisy under real traffic.
let crumbCache = { crumb: null, cookie: null, expiresAt: 0 };

async function getCrumb(forceRefresh = false) {
  if (!forceRefresh && crumbCache.crumb && Date.now() < crumbCache.expiresAt) {
    return crumbCache;
  }
  const cookieRes = await fetch('https://fc.yahoo.com', { headers: { 'User-Agent': UA } });
  const setCookie = cookieRes.headers.get('set-cookie') || '';
  const cookie = setCookie.split(';')[0] || '';
  const crumbRes = await fetch('https://query1.finance.yahoo.com/v1/test/getcrumb', {
    headers: { 'User-Agent': UA, Cookie: cookie },
  });
  const crumb = (await crumbRes.text()).trim();
  crumbCache = { crumb, cookie, expiresAt: Date.now() + 50 * 60 * 1000 };
  return crumbCache;
}

async function yahooFetchAuthed(buildUrl) {
  let { crumb, cookie } = await getCrumb();
  let res = await fetch(buildUrl(crumb), { headers: { 'User-Agent': UA, Cookie: cookie } });
  if (res.status === 401) {
    ({ crumb, cookie } = await getCrumb(true));
    res = await fetch(buildUrl(crumb), { headers: { 'User-Agent': UA, Cookie: cookie } });
  }
  return res;
}

const raw = (field) => (field && typeof field === 'object' ? field.raw ?? null : field ?? null);

// ponytail: best-effort. nseindia.com fronts everything with Akamai and 403s
// datacenter IPs (confirmed by curl from this sandbox) — it may simply never
// return results depending on where this is hosted. Wrapped so a failure here
// never breaks /search; the cache + Yahoo sources below still cover the request.
export async function tryNseAutocomplete(query) {
  try {
    const headers = {
      'User-Agent': UA,
      Accept: '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      Referer: 'https://www.nseindia.com/',
      'X-Requested-With': 'XMLHttpRequest',
    };
    const homeRes = await fetch('https://www.nseindia.com', { headers, signal: AbortSignal.timeout(5000) });
    const cookie = (homeRes.headers.get('set-cookie') || '').split(';')[0];
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const res = await fetch(`https://www.nseindia.com/api/search/autocomplete?q=${encodeURIComponent(query)}`, {
      headers: { ...headers, Cookie: cookie },
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.symbols || [])
      .filter((item) => item.result_sub_type === 'equity')
      .map((item) => ({
        symbol: item.symbol,
        company_name: item.symbol_info,
        listing_date: item.listing_date,
        source: 'nse_api',
      }));
  } catch {
    return [];
  }
}

// Mirrors the old Flask app's yfinance fallback: treat the query itself as a
// ticker and see if Yahoo resolves it directly (catches exact symbols the
// search index misses, e.g. lesser-known tickers).
export async function searchYahooDirect(query) {
  const symbol = query.toUpperCase().replace(/\s+/g, '');
  if (!symbol) return [];
  const detail = await getStockDetail(`${symbol}.NS`);
  if (!detail) return [];
  return [
    {
      symbol,
      company_name: detail.companyName,
      sector: detail.sector,
      industry: detail.industry,
      source: 'yahoo_direct',
    },
  ];
}

export async function searchYahoo(query) {
  const url = `https://query1.finance.yahoo.com/v1/finance/search?q=${encodeURIComponent(query)}&quotesCount=15`;
  const res = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!res.ok) return [];
  const data = await res.json();
  return (data.quotes || [])
    .filter((q) => q.symbol && (q.symbol.endsWith('.NS') || q.symbol.endsWith('.BO')))
    .map((q) => ({
      symbol: q.symbol.replace(/\.(NS|BO)$/, ''),
      company_name: q.longname || q.shortname || q.symbol,
      sector: q.sector || 'N/A',
      industry: q.industry || 'N/A',
      source: 'yahoo',
    }));
}

// Full detail for one ticker: price + fundamentals + sector/industry in a single call.
export async function getStockDetail(tickerSymbol) {
  const modules = 'price,summaryDetail,defaultKeyStatistics,assetProfile';
  const res = await yahooFetchAuthed(
    (crumb) =>
      `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${encodeURIComponent(tickerSymbol)}?modules=${modules}&crumb=${encodeURIComponent(crumb)}`
  );
  if (!res.ok) return null;
  const data = await res.json();
  const result = data?.quoteSummary?.result?.[0];
  if (!result) return null;

  const { price = {}, summaryDetail = {}, defaultKeyStatistics = {}, assetProfile = {} } = result;
  if (raw(price.regularMarketPrice) === null) return null;

  return {
    companyName: price.longName || price.shortName || tickerSymbol,
    currency: price.currency || 'INR',
    lastPrice: raw(price.regularMarketPrice),
    change: raw(price.regularMarketChange),
    percentChange: raw(price.regularMarketChangePercent) !== null ? raw(price.regularMarketChangePercent) * 100 : null,
    previousClose: raw(price.regularMarketPreviousClose),
    open: raw(price.regularMarketOpen) ?? raw(summaryDetail.open),
    dayHigh: raw(price.regularMarketDayHigh),
    dayLow: raw(price.regularMarketDayLow),
    yearHigh: raw(summaryDetail.fiftyTwoWeekHigh),
    yearLow: raw(summaryDetail.fiftyTwoWeekLow),
    volume: raw(price.regularMarketVolume),
    marketCap: raw(price.marketCap) ?? raw(summaryDetail.marketCap),
    peRatio: raw(summaryDetail.trailingPE),
    dividendYield: raw(summaryDetail.dividendYield) !== null ? raw(summaryDetail.dividendYield) * 100 : null,
    bookValue: raw(defaultKeyStatistics.bookValue),
    eps: raw(defaultKeyStatistics.trailingEps),
    sector: assetProfile.sector || 'N/A',
    industry: assetProfile.industry || 'N/A',
    lastUpdateEpoch: raw(price.regularMarketTime),
  };
}

// Batch quote for /stock/list — one HTTP call for every symbol. No sector/industry
// here (Yahoo's batch quote endpoint doesn't carry it); use /stock for that.
export async function getQuoteBatch(tickerSymbols) {
  const res = await yahooFetchAuthed(
    (crumb) =>
      `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(tickerSymbols.join(','))}&crumb=${encodeURIComponent(crumb)}`
  );
  if (!res.ok) return {};
  const data = await res.json();
  const byTicker = {};
  for (const q of data?.quoteResponse?.result || []) {
    byTicker[q.symbol] = {
      companyName: q.longName || q.shortName || q.symbol,
      lastPrice: q.regularMarketPrice ?? null,
      change: q.regularMarketChange ?? null,
      percentChange: q.regularMarketChangePercent ?? null,
      volume: q.regularMarketVolume ?? null,
      marketCap: q.marketCap ?? null,
      peRatio: q.trailingPE ?? null,
    };
  }
  return byTicker;
}
