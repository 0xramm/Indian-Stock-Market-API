# Indian Stock Market API - NSE & BSE Real-Time Data

Free REST API for real-time NSE (National Stock Exchange) and BSE (Bombay Stock Exchange) stock prices in India. No authentication or API key required. Built for automation tools like n8n, Zapier, Make, Node-RED, trading bots, portfolio trackers, and financial dashboards — plug it straight into a workflow and pull live Nifty 50 / Sensex stock data as JSON.

**Version:** 3.0 · **License:** MIT

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | API info: features, endpoints, exchange details |
| `GET /search?q={query}` | Search for a stock by company name or symbol (e.g. `?q=reliance`) |
| `GET /stock?symbol={SYMBOL}&res={num\|val}` | Get live price, change %, volume, market cap, P/E, dividend yield, sector, and more for one stock. `.NS` (NSE, default) or `.BO` (BSE) suffix picks the exchange |
| `GET /stock/list?symbols={SYM1,SYM2}&res={num\|val}` | Same as `/stock` but batched for multiple symbols in one call (mix NSE/BSE) |
| `GET /symbols` | List all pre-cached company-name → symbol mappings |

`res=num` returns plain numbers (best for automation/calculations); `res=val` (default) wraps values with units, e.g. `{"value": 28.45, "unit": "x"}` — best for display.

## Disclaimer

Data is for educational purposes only. Not for financial decisions. Verify from official sources before trading.
