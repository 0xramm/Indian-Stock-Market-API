# Indian Stock Market API - NSE & BSE Real-Time Data

Free REST API for fetching real-time stock prices from both NSE (National Stock Exchange) and BSE (Bombay Stock Exchange) of India. Perfect for automation tools like n8n, Make, Zapier, Node-RED, trading bots, and financial applications.

**Base URL:** `https://nse-api-ruby.vercel.app/`

**Version:** 2.4

**License:** MIT

## Features

- Free and open-source Indian stock market API
- Support for both NSE and BSE exchanges
- Real-time stock market data
- No authentication or API key required
- RESTful JSON API
- Flexible response formats (numeric or with units)
- Smart search with company name
- Automatic exchange detection
- Batch stock queries
- Indian number formatting (Crores/Lakhs)

## Exchange Support

### NSE (National Stock Exchange)

- **Suffix:** `.NS`
- **Default:** Yes (used when no suffix provided)
- **Examples:** `ITC.NS`, `RELIANCE.NS`, `TCS.NS`

### BSE (Bombay Stock Exchange)

- **Suffix:** `.BO`
- **Default:** No (must specify suffix)
- **Examples:** `ITC.BO`, `RELIANCE.BO`, `TCS.BO`

### Usage Pattern

```
ITC        → Fetches from NSE (default)
ITC.NS     → Fetches from NSE (explicit)
ITC.BO     → Fetches from BSE
```

## API Endpoints

### 1. Search for Stocks

Find stock symbols by searching with company names.

**Endpoint:** `GET /search?q={query}`

**Parameters:**

- `q` (required): Search query (company name or symbol)

**Examples:**

```bash
GET /search?q=reliance
GET /search?q=tata
GET /search?q=hdfc bank
GET /search?q=indian oil
```

**Sample Response:**

```json
{
  "status": "success",
  "query": "reliance",
  "total_results": 1,
  "results": [
    {
      "symbol": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "match_type": "exact",
      "source": "cache",
      "api_url": "/stock?symbol=RELIANCE",
      "nse_url": "/stock?symbol=RELIANCE.NS",
      "bse_url": "/stock?symbol=RELIANCE.BO"
    }
  ],
  "note": "Add .NS for NSE or .BO for BSE to the symbol. Default is NSE.",
  "timestamp": "2025-10-18 18:29:00"
}
```

---

### 2. Get Single Stock Details

Retrieve detailed information for a specific stock.

**Endpoint:** `GET /stock?symbol={SYMBOL}&res={num|val}`

**Parameters:**

- `symbol` (required): Stock symbol with optional exchange suffix
- `res` (optional): Response format - `num` (numbers only) or `val` (with units). Default: `val`

#### Example 1: NSE Stock - Default (No Suffix)

```bash
GET /stock?symbol=ITC&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "symbol": "ITC",
  "exchange": "NSE",
  "ticker": "ITC.NS",
  "response_format": "numeric_only",
  "data": {
    "company_name": "ITC Limited",
    "last_price": 445.5,
    "change": 2.3,
    "percent_change": 0.52,
    "previous_close": 443.2,
    "open": 444.0,
    "day_high": 447.8,
    "day_low": 442.5,
    "year_high": 490.0,
    "year_low": 380.25,
    "volume": 52345670,
    "market_cap": 5567894500000.0,
    "pe_ratio": 28.45,
    "dividend_yield": 3.45,
    "book_value": 156.5,
    "earnings_per_share": 15.65,
    "sector": "Consumer Defensive",
    "industry": "Tobacco",
    "currency": "INR",
    "last_update": "2025-10-18",
    "timestamp": "2025-10-18 18:29:00"
  },
  "alternate_exchange": {
    "exchange": "BSE",
    "ticker": "ITC.BO",
    "api_url": "/stock?symbol=ITC.BO"
  }
}
```

#### Example 2: NSE Stock - Explicit Suffix

```bash
GET /stock?symbol=RELIANCE.NS&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "ticker": "RELIANCE.NS",
  "response_format": "numeric_only",
  "data": {
    "company_name": "Reliance Industries Limited",
    "last_price": 2456.75,
    "change": 12.3,
    "percent_change": 0.5,
    "previous_close": 2444.45,
    "open": 2450.0,
    "day_high": 2468.9,
    "day_low": 2445.2,
    "year_high": 2856.0,
    "year_low": 2220.3,
    "volume": 8234567,
    "market_cap": 16645678900000.0,
    "pe_ratio": 27.35,
    "dividend_yield": 0.35,
    "book_value": 892.4,
    "earnings_per_share": 89.75,
    "sector": "Energy",
    "industry": "Oil & Gas Integrated",
    "currency": "INR",
    "last_update": "2025-10-18",
    "timestamp": "2025-10-18 18:29:00"
  },
  "alternate_exchange": {
    "exchange": "BSE",
    "ticker": "RELIANCE.BO",
    "api_url": "/stock?symbol=RELIANCE.BO"
  }
}
```

#### Example 3: BSE Stock

```bash
GET /stock?symbol=TCS.BO&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "symbol": "TCS",
  "exchange": "BSE",
  "ticker": "TCS.BO",
  "response_format": "numeric_only",
  "data": {
    "company_name": "Tata Consultancy Services Limited",
    "last_price": 3456.75,
    "change": -12.5,
    "percent_change": -0.36,
    "previous_close": 3469.25,
    "open": 3465.0,
    "day_high": 3478.9,
    "day_low": 3445.2,
    "year_high": 4078.0,
    "year_low": 3011.3,
    "volume": 1234567,
    "market_cap": 12678945000000.0,
    "pe_ratio": 29.35,
    "dividend_yield": 1.45,
    "book_value": 245.8,
    "earnings_per_share": 117.65,
    "sector": "Technology",
    "industry": "Information Technology Services",
    "currency": "INR",
    "last_update": "2025-10-18",
    "timestamp": "2025-10-18 18:29:00"
  },
  "alternate_exchange": {
    "exchange": "NSE",
    "ticker": "TCS.NS",
    "api_url": "/stock?symbol=TCS.NS"
  }
}
```

#### Example 4: With Units (res=val)

```bash
GET /stock?symbol=INFY.NS&res=val
```

**Sample Response:**

```json
{
  "status": "success",
  "symbol": "INFY",
  "exchange": "NSE",
  "ticker": "INFY.NS",
  "response_format": "values_with_units",
  "data": {
    "company_name": "Infosys Limited",
    "last_price": {
      "value": 1567.8,
      "unit": "INR"
    },
    "change": {
      "value": 8.9,
      "unit": "INR"
    },
    "percent_change": {
      "value": 0.57,
      "unit": "%"
    },
    "previous_close": {
      "value": 1558.9,
      "unit": "INR"
    },
    "open": {
      "value": 1560.0,
      "unit": "INR"
    },
    "day_high": {
      "value": 1572.5,
      "unit": "INR"
    },
    "day_low": {
      "value": 1556.3,
      "unit": "INR"
    },
    "year_high": {
      "value": 1953.9,
      "unit": "INR"
    },
    "year_low": {
      "value": 1351.65,
      "unit": "INR"
    },
    "volume": {
      "value": 3.46,
      "unit": "Crores Shares"
    },
    "market_cap": {
      "value": 654321.0,
      "unit": "Crores INR"
    },
    "pe_ratio": {
      "value": 24.56,
      "unit": "x"
    },
    "dividend_yield": {
      "value": 2.15,
      "unit": "%"
    },
    "book_value": {
      "value": 312.45,
      "unit": "INR"
    },
    "earnings_per_share": {
      "value": 63.85,
      "unit": "INR"
    },
    "sector": "Technology",
    "industry": "Information Technology Services",
    "currency": "INR",
    "last_update": "2025-10-18",
    "timestamp": "2025-10-18 18:29:00"
  },
  "alternate_exchange": {
    "exchange": "BSE",
    "ticker": "INFY.BO",
    "api_url": "/stock?symbol=INFY.BO"
  }
}
```

---

### 3. Get Multiple Stocks

Retrieve information for multiple stocks in one request. Mix NSE and BSE symbols.

**Endpoint:** `GET /stock/list?symbols={SYMBOL1,SYMBOL2}&res={num|val}`

**Parameters:**

- `symbols` (required): Comma-separated stock symbols
- `res` (optional): Response format - `num` or `val`. Default: `val`

#### Example 1: Multiple NSE Stocks (Default)

```bash
GET /stock/list?symbols=ITC,TCS,INFY&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "response_format": "numeric_only",
  "count": 3,
  "stocks": [
    {
      "symbol": "ITC",
      "exchange": "NSE",
      "ticker": "ITC.NS",
      "company_name": "ITC Limited",
      "last_price": 445.5,
      "change": 2.3,
      "percent_change": 0.52,
      "volume": 52345670,
      "market_cap": 5567894500000.0,
      "pe_ratio": 28.45,
      "sector": "Consumer Defensive"
    },
    {
      "symbol": "TCS",
      "exchange": "NSE",
      "ticker": "TCS.NS",
      "company_name": "Tata Consultancy Services Limited",
      "last_price": 3456.75,
      "change": -12.5,
      "percent_change": -0.36,
      "volume": 1234567,
      "market_cap": 12678945000000.0,
      "pe_ratio": 29.35,
      "sector": "Technology"
    },
    {
      "symbol": "INFY",
      "exchange": "NSE",
      "ticker": "INFY.NS",
      "company_name": "Infosys Limited",
      "last_price": 1567.8,
      "change": 8.9,
      "percent_change": 0.57,
      "volume": 34567890,
      "market_cap": 6543210000000.0,
      "pe_ratio": 24.56,
      "sector": "Technology"
    }
  ],
  "timestamp": "2025-10-18 18:29:00"
}
```

#### Example 2: Multiple BSE Stocks

```bash
GET /stock/list?symbols=ITC.BO,RELIANCE.BO,HDFCBANK.BO&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "response_format": "numeric_only",
  "count": 3,
  "stocks": [
    {
      "symbol": "ITC",
      "exchange": "BSE",
      "ticker": "ITC.BO",
      "company_name": "ITC Limited",
      "last_price": 445.35,
      "change": 2.15,
      "percent_change": 0.49,
      "volume": 48234560,
      "market_cap": 5565678900000.0,
      "pe_ratio": 28.42,
      "sector": "Consumer Defensive"
    },
    {
      "symbol": "RELIANCE",
      "exchange": "BSE",
      "ticker": "RELIANCE.BO",
      "company_name": "Reliance Industries Limited",
      "last_price": 2456.5,
      "change": 12.05,
      "percent_change": 0.49,
      "volume": 7834567,
      "market_cap": 16642345600000.0,
      "pe_ratio": 27.33,
      "sector": "Energy"
    },
    {
      "symbol": "HDFCBANK",
      "exchange": "BSE",
      "ticker": "HDFCBANK.BO",
      "company_name": "HDFC Bank Limited",
      "last_price": 1645.75,
      "change": -5.25,
      "percent_change": -0.32,
      "volume": 5678901,
      "market_cap": 12456789000000.0,
      "pe_ratio": 19.85,
      "sector": "Financial Services"
    }
  ],
  "timestamp": "2025-10-18 18:29:00"
}
```

#### Example 3: Mixed NSE and BSE Stocks

```bash
GET /stock/list?symbols=ITC.NS,RELIANCE.BO,TCS.NS,INFY.BO&res=num
```

**Sample Response:**

```json
{
  "status": "success",
  "response_format": "numeric_only",
  "count": 4,
  "stocks": [
    {
      "symbol": "ITC",
      "exchange": "NSE",
      "ticker": "ITC.NS",
      "company_name": "ITC Limited",
      "last_price": 445.5,
      "change": 2.3,
      "percent_change": 0.52,
      "volume": 52345670,
      "market_cap": 5567894500000.0,
      "pe_ratio": 28.45,
      "sector": "Consumer Defensive"
    },
    {
      "symbol": "RELIANCE",
      "exchange": "BSE",
      "ticker": "RELIANCE.BO",
      "company_name": "Reliance Industries Limited",
      "last_price": 2456.5,
      "change": 12.05,
      "percent_change": 0.49,
      "volume": 7834567,
      "market_cap": 16642345600000.0,
      "pe_ratio": 27.33,
      "sector": "Energy"
    },
    {
      "symbol": "TCS",
      "exchange": "NSE",
      "ticker": "TCS.NS",
      "company_name": "Tata Consultancy Services Limited",
      "last_price": 3456.75,
      "change": -12.5,
      "percent_change": -0.36,
      "volume": 1234567,
      "market_cap": 12678945000000.0,
      "pe_ratio": 29.35,
      "sector": "Technology"
    },
    {
      "symbol": "INFY",
      "exchange": "BSE",
      "ticker": "INFY.BO",
      "company_name": "Infosys Limited",
      "last_price": 1567.65,
      "change": 8.75,
      "percent_change": 0.56,
      "volume": 33456789,
      "market_cap": 6541234500000.0,
      "pe_ratio": 24.54,
      "sector": "Technology"
    }
  ],
  "timestamp": "2025-10-18 18:29:00"
}
```

---

### 4. List Available Symbols

Get list of pre-cached stock symbols with both NSE and BSE tickers.

**Endpoint:** `GET /symbols`

**Parameters:** None

**Example:**

```bash
GET /symbols
```

**Sample Response:**

```json
{
  "status": "success",
  "total_symbols": 30,
  "symbols": [
    {
      "search_term": "indian oil",
      "symbol": "IOC",
      "nse_ticker": "IOC.NS",
      "bse_ticker": "IOC.BO",
      "api_url_nse": "/stock?symbol=IOC.NS",
      "api_url_bse": "/stock?symbol=IOC.BO"
    },
    {
      "search_term": "reliance",
      "symbol": "RELIANCE",
      "nse_ticker": "RELIANCE.NS",
      "bse_ticker": "RELIANCE.BO",
      "api_url_nse": "/stock?symbol=RELIANCE.NS",
      "api_url_bse": "/stock?symbol=RELIANCE.BO"
    },
    {
      "search_term": "tcs",
      "symbol": "TCS",
      "nse_ticker": "TCS.NS",
      "bse_ticker": "TCS.BO",
      "api_url_nse": "/stock?symbol=TCS.NS",
      "api_url_bse": "/stock?symbol=TCS.BO"
    },
    {
      "search_term": "infosys",
      "symbol": "INFY",
      "nse_ticker": "INFY.NS",
      "bse_ticker": "INFY.BO",
      "api_url_nse": "/stock?symbol=INFY.NS",
      "api_url_bse": "/stock?symbol=INFY.BO"
    },
    {
      "search_term": "hdfc bank",
      "symbol": "HDFCBANK",
      "nse_ticker": "HDFCBANK.NS",
      "bse_ticker": "HDFCBANK.BO",
      "api_url_nse": "/stock?symbol=HDFCBANK.NS",
      "api_url_bse": "/stock?symbol=HDFCBANK.BO"
    }
  ],
  "note": "Most stocks are available on both NSE (.NS) and BSE (.BO). Default is NSE."
}
```

---

### 5. API Information

Get API information, features, and documentation.

**Endpoint:** `GET /`

**Parameters:** None

**Example:**

```bash
GET /
```

**Sample Response:**

```json
{
  "message": "NSE/BSE Stock Price API with Smart Search & Flexible Output",
  "version": "2.4",
  "status": "operational",
  "features": [
    "Support for both NSE and BSE exchanges",
    "Automatic exchange detection from symbol suffix",
    "Multi-source search (NSE API + Local Cache + Yahoo Finance)",
    "Real-time stock prices via Yahoo Finance",
    "30+ pre-cached popular stock symbols",
    "Flexible output: Simple numbers OR Values with units",
    "Smart number formatting for readability"
  ],
  "exchanges": {
    "NSE": {
      "description": "National Stock Exchange",
      "suffix": ".NS",
      "example": "ITC.NS, RELIANCE.NS",
      "default": true
    },
    "BSE": {
      "description": "Bombay Stock Exchange",
      "suffix": ".BO",
      "example": "ITC.BO, RELIANCE.BO",
      "default": false
    }
  },
  "endpoints": {
    "/search": {
      "description": "Search for stocks by company name",
      "method": "GET",
      "parameters": "q=SEARCH_TERM",
      "examples": ["/search?q=indian oil", "/search?q=reliance"]
    },
    "/stock": {
      "description": "Get single stock details",
      "method": "GET",
      "parameters": "symbol=STOCK_SYMBOL, res=num|val (optional)",
      "examples": [
        "/stock?symbol=ITC (default NSE)",
        "/stock?symbol=ITC.NS (NSE explicit)",
        "/stock?symbol=ITC.BO (BSE)",
        "/stock?symbol=RELIANCE.NS&res=num",
        "/stock?symbol=TCS.BO&res=val"
      ]
    },
    "/stock/list": {
      "description": "Get multiple stock details",
      "method": "GET",
      "parameters": "symbols=STOCK1,STOCK2, res=num|val (optional)",
      "examples": [
        "/stock/list?symbols=ITC,TCS,INFY (default NSE)",
        "/stock/list?symbols=ITC.NS,TCS.BO,INFY.NS (mixed)",
        "/stock/list?symbols=RELIANCE.BO,HDFCBANK.NS&res=num"
      ]
    },
    "/symbols": {
      "description": "List all available cached symbols with both NSE and BSE tickers",
      "method": "GET",
      "example": "/symbols"
    }
  },
  "usage_guide": {
    "default_behavior": "If no exchange suffix is provided, NSE (.NS) is used by default",
    "nse_examples": ["ITC", "ITC.NS", "RELIANCE", "RELIANCE.NS"],
    "bse_examples": ["ITC.BO", "RELIANCE.BO", "TCS.BO"],
    "mixed_request": "You can mix NSE and BSE symbols in /stock/list endpoint"
  },
  "response_formats": {
    "res=num": "Simple numeric values (e.g., \"pe_ratio\": 21.65)",
    "res=val": "Values with units (e.g., \"pe_ratio\": {\"value\": 21.65, \"unit\": \"x\"})"
  }
}
```

---

## Error Responses

### Error 1: Invalid Symbol

**Request:**

```bash
GET /stock?symbol=INVALID&res=num
```

**Sample Response:**

```json
{
  "status": "error",
  "message": "No data found for symbol: INVALID on NSE. Stock may not exist or market is closed.",
  "hint": "Try the other exchange: INVALID.BO",
  "note": "Markets are closed on weekends and holidays"
}
```

### Error 2: Missing Parameters

**Request:**

```bash
GET /stock
```

**Sample Response:**

```json
{
  "status": "error",
  "message": "Please provide a stock symbol using ?symbol=STOCKNAME",
  "hint": "Use /search?q=company_name to find the correct symbol",
  "examples": [
    "/stock?symbol=ITC (NSE - default)",
    "/stock?symbol=ITC.NS (NSE - explicit)",
    "/stock?symbol=ITC.BO (BSE)"
  ]
}
```

### Error 3: Invalid Response Format

**Request:**

```bash
GET /stock?symbol=ITC&res=invalid
```

**Sample Response:**

```json
{
  "status": "error",
  "message": "Invalid response type. Use res=num for numbers only or res=val for values with units",
  "examples": ["/stock?symbol=ITC&res=num", "/stock?symbol=ITC&res=val"]
}
```

### Error 4: No Search Results

**Request:**

```bash
GET /search?q=xyz123
```

**Sample Response:**

```json
{
  "status": "error",
  "message": "No results found for: xyz123",
  "hint": "Try searching with stock symbol (e.g., TCS, INFY, RELIANCE) or common company names",
  "suggestions": [
    "For Indian Oil, try: IOC",
    "For Reliance, try: RELIANCE",
    "For TCS, try: TCS",
    "For Infosys, try: INFY"
  ]
}
```

---

## Response Format Comparison

### res=num (Numbers Only)

Best for automation, calculations, and dashboards.

```json
{
  "last_price": 445.5,
  "percent_change": 0.52,
  "volume": 52345670,
  "market_cap": 5567894500000.0,
  "pe_ratio": 28.45
}
```

### res=val (Values with Units)

Best for reports, displays, and human-readable output.

```json
{
  "last_price": { "value": 445.5, "unit": "INR" },
  "percent_change": { "value": 0.52, "unit": "%" },
  "volume": { "value": 5.23, "unit": "Crores Shares" },
  "market_cap": { "value": 556789.45, "unit": "Crores INR" },
  "pe_ratio": { "value": 28.45, "unit": "x" }
}
```

---

## Popular Stock Symbols

| Company                   | Symbol     | NSE           | BSE           |
| ------------------------- | ---------- | ------------- | ------------- |
| Reliance Industries       | RELIANCE   | RELIANCE.NS   | RELIANCE.BO   |
| Tata Consultancy Services | TCS        | TCS.NS        | TCS.BO        |
| HDFC Bank                 | HDFCBANK   | HDFCBANK.NS   | HDFCBANK.BO   |
| Infosys                   | INFY       | INFY.NS       | INFY.BO       |
| ICICI Bank                | ICICIBANK  | ICICIBANK.NS  | ICICIBANK.BO  |
| Bharti Airtel             | BHARTIARTL | BHARTIARTL.NS | BHARTIARTL.BO |
| State Bank of India       | SBIN       | SBIN.NS       | SBIN.BO       |
| ITC Limited               | ITC        | ITC.NS        | ITC.BO        |
| Hindustan Unilever        | HINDUNILVR | HINDUNILVR.NS | HINDUNILVR.BO |
| Indian Oil Corporation    | IOC        | IOC.NS        | IOC.BO        |
| Larsen & Toubro           | LT         | LT.NS         | LT.BO         |
| Asian Paints              | ASIANPAINT | ASIANPAINT.NS | ASIANPAINT.BO |
| Maruti Suzuki             | MARUTI     | MARUTI.NS     | MARUTI.BO     |
| Bajaj Finance             | BAJFINANCE | BAJFINANCE.NS | BAJFINANCE.BO |
| Titan Company             | TITAN      | TITAN.NS      | TITAN.BO      |

---

## Common Use Cases

### Use Case 1: Search and Fetch from NSE

**Step 1:** Search for company

```bash
GET /search?q=indian oil
```

**Step 2:** Use symbol from results (NSE by default)

```bash
GET /stock?symbol=IOC&res=num
```

### Use Case 2: Compare NSE vs BSE Prices

**NSE Price:**

```bash
GET /stock?symbol=RELIANCE.NS&res=num
```

**BSE Price:**

```bash
GET /stock?symbol=RELIANCE.BO&res=num
```

### Use Case 3: Monitor Portfolio (Mixed Exchanges)

```bash
GET /stock/list?symbols=ITC.NS,RELIANCE.BO,TCS.NS,INFY.BO&res=num
```

### Use Case 4: Get Data with Indian Formatting

```bash
GET /stock?symbol=RELIANCE&res=val
```

Returns values in Crores/Lakhs for better readability.

---

## Market Hours

**NSE Trading Hours:**

- Pre-opening: 9:00 AM - 9:15 AM IST
- Normal Trading: 9:15 AM - 3:30 PM IST
- Closed: Weekends and public holidays

**BSE Trading Hours:**

- Pre-opening: 9:00 AM - 9:15 AM IST
- Normal Trading: 9:15 AM - 3:30 PM IST
- Closed: Weekends and public holidays

**Note:** API returns last available data when markets are closed.

---

## Best Practices

1. **Use Search First:** Always search for correct symbol before fetching data
2. **Choose Format:** Use `res=num` for automation, `res=val` for display
3. **Batch Requests:** Use `/stock/list` for multiple stocks
4. **Default Exchange:** NSE is default, specify `.BO` for BSE
5. **Rate Limiting:** Limit to 60 requests per minute
6. **Cache Results:** Cache responses for at least 30 seconds

---

## Keywords

Free Indian stock API, NSE API, BSE API, Indian stock market API, National Stock Exchange API, Bombay Stock Exchange API, real-time stock data India, stock price API free, trading bot API India, automation stock API, n8n stock integration, Zapier Indian stocks, portfolio tracker API, Indian equity market data, Nifty 50 API, Sensex API, Yahoo Finance India, stock monitoring API, REST API Indian stocks, JSON stock data

---

## License

MIT License - Free for personal and commercial use

## Disclaimer

Data is for educational purposes only. Not for financial decisions. Verify from official sources before trading.
