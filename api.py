from flask import Flask, request, jsonify
from datetime import datetime
import yfinance as yf
import requests
import json
import time


app = Flask(__name__)


# Cache for NSE symbols (you can expand this list)
NSE_SYMBOLS_CACHE = {
    'indian oil': 'IOC',
    'ioc': 'IOC',
    'reliance': 'RELIANCE',
    'reliance industries': 'RELIANCE',
    'tcs': 'TCS',
    'tata consultancy': 'TCS',
    'infosys': 'INFY',
    'infy': 'INFY',
    'hdfc bank': 'HDFCBANK',
    'hdfc': 'HDFCBANK',
    'icici bank': 'ICICIBANK',
    'icici': 'ICICIBANK',
    'itc': 'ITC',
    'bharti airtel': 'BHARTIARTL',
    'airtel': 'BHARTIARTL',
    'sbi': 'SBIN',
    'state bank': 'SBIN',
    'wipro': 'WIPRO',
    'hindustan unilever': 'HINDUNILVR',
    'hul': 'HINDUNILVR',
    'maruti': 'MARUTI',
    'maruti suzuki': 'MARUTI',
    'asian paints': 'ASIANPAINT',
    'bajaj finance': 'BAJFINANCE',
    'titan': 'TITAN',
    'larsen toubro': 'LT',
    'lt': 'LT',
    'ongc': 'ONGC',
    'ntpc': 'NTPC',
    'power grid': 'POWERGRID',
    'coal india': 'COALINDIA',
    'adani': 'ADANIENT',
    'adani enterprises': 'ADANIENT',
    'sun pharma': 'SUNPHARMA',
    'dr reddy': 'DRREDDY',
    'cipla': 'CIPLA',
    'mahindra': 'M&M',
    'm&m': 'M&M'
}


def determine_exchange(symbol):
    """
    Determine exchange from symbol suffix
    Returns: (clean_symbol, exchange_suffix)
    """
    symbol = symbol.upper().strip()
    
    # Check if symbol already has exchange suffix
    if symbol.endswith('.NS'):
        return symbol[:-3], '.NS'
    elif symbol.endswith('.BO'):
        return symbol[:-3], '.BO'
    else:
        # Default to NSE
        return symbol, '.NS'


def format_currency(value, with_unit=True):
    """Format currency values with optional units"""
    if value == 'N/A' or not value:
        return {"value": "N/A", "unit": "INR"} if with_unit else "N/A"
    
    value = float(value)
    
    if with_unit:
        return {
            "value": round(value, 2),
            "unit": "INR"
        }
    else:
        return round(value, 2)


def format_market_cap(value, with_unit=True):
    """Format market cap in Crores/Lakhs with optional units"""
    if value == 'N/A' or not value:
        return {"value": "N/A", "unit": "INR"} if with_unit else "N/A"
    
    value = float(value)
    
    if with_unit:
        if value >= 10000000:  # 1 crore
            return {
                "value": round(value / 10000000, 2),
                "unit": "Crores INR"
            }
        elif value >= 100000:  # 1 lakh
            return {
                "value": round(value / 100000, 2),
                "unit": "Lakhs INR"
            }
        else:
            return {
                "value": round(value, 2),
                "unit": "INR"
            }
    else:
        return round(value, 2)


def format_volume(value, with_unit=True):
    """Format volume with optional units"""
    if value == 'N/A' or not value:
        return {"value": "N/A", "unit": "Shares"} if with_unit else "N/A"
    
    value = int(value)
    
    if with_unit:
        if value >= 10000000:  # 1 crore
            return {
                "value": round(value / 10000000, 2),
                "unit": "Crores Shares"
            }
        elif value >= 100000:  # 1 lakh
            return {
                "value": round(value / 100000, 2),
                "unit": "Lakhs Shares"
            }
        else:
            return {
                "value": value,
                "unit": "Shares"
            }
    else:
        return value


def format_percentage(value, with_unit=True):
    """Format percentage values with optional units"""
    if value == 'N/A' or not value:
        return {"value": "N/A", "unit": "%"} if with_unit else "N/A"
    
    if with_unit:
        return {
            "value": round(float(value), 2),
            "unit": "%"
        }
    else:
        return round(float(value), 2)


def format_ratio(value, with_unit=True):
    """Format ratio values (like P/E) with optional units"""
    if value == 'N/A' or not value or value == 0:
        return {"value": "N/A", "unit": "x"} if with_unit else "N/A"
    
    if with_unit:
        return {
            "value": round(float(value), 2),
            "unit": "x"
        }
    else:
        return round(float(value), 2)


def search_with_yfinance(query):
    """Search stocks using yfinance as fallback"""
    try:
        # Try to get stock info directly
        query_upper = query.upper()
        ticker = yf.Ticker(f"{query_upper}.NS")
        info = ticker.info
        
        if info and info.get('symbol'):
            return [{
                'symbol': query_upper,
                'company_name': info.get('longName', info.get('shortName', query_upper)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }]
    except:
        pass
    
    return []


def search_in_cache(query):
    """Search in local cache"""
    query_lower = query.lower().strip()
    results = []
    
    # Exact match
    if query_lower in NSE_SYMBOLS_CACHE:
        symbol = NSE_SYMBOLS_CACHE[query_lower]
        results.append({
            'symbol': symbol,
            'company_name': query,
            'match_type': 'exact',
            'source': 'cache'
        })
    else:
        # Partial match
        for key, symbol in NSE_SYMBOLS_CACHE.items():
            if query_lower in key or key in query_lower:
                results.append({
                    'symbol': symbol,
                    'company_name': key.title(),
                    'match_type': 'partial',
                    'source': 'cache'
                })
    
    return results


def try_nse_autocomplete(query):
    """Try to fetch from NSE with proper handling"""
    try:
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        session.headers.update(headers)
        
        # Visit homepage first
        session.get('https://www.nseindia.com', timeout=5)
        time.sleep(1)
        
        # Try autocomplete
        url = f'https://www.nseindia.com/api/search/autocomplete?q={query}'
        response = session.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            symbols = data.get('symbols', [])
            
            equity_results = []
            for item in symbols:
                if item.get('result_sub_type') == 'equity':
                    equity_results.append({
                        'symbol': item.get('symbol'),
                        'company_name': item.get('symbol_info'),
                        'listing_date': item.get('listing_date'),
                        'source': 'nse_api'
                    })
            
            return equity_results
    except Exception as e:
        print(f"NSE API Error: {e}")
    
    return []


@app.route('/search', methods=['GET'])
def search_stock():
    """
    Search for stocks with multiple fallback methods
    Usage: /search?q=indian oil
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Please provide a search query using ?q=SEARCH_TERM',
                'example': '/search?q=indian oil'
            }), 400
        
        all_results = []
        
        # Method 1: Try NSE API first
        nse_results = try_nse_autocomplete(query)
        if nse_results:
            all_results.extend(nse_results)
        
        # Method 2: Search in local cache
        cache_results = search_in_cache(query)
        if cache_results:
            all_results.extend(cache_results)
        
        # Method 3: Try with yfinance
        yf_results = search_with_yfinance(query)
        if yf_results:
            all_results.extend(yf_results)
        
        # Remove duplicates
        seen_symbols = set()
        unique_results = []
        for result in all_results:
            symbol = result.get('symbol')
            if symbol and symbol not in seen_symbols:
                seen_symbols.add(symbol)
                unique_results.append(result)
        
        if not unique_results:
            return jsonify({
                'status': 'error',
                'message': f'No results found for: {query}',
                'hint': 'Try searching with stock symbol (e.g., TCS, INFY, RELIANCE) or common company names',
                'suggestions': [
                    'For Indian Oil, try: IOC',
                    'For Reliance, try: RELIANCE',
                    'For TCS, try: TCS',
                    'For Infosys, try: INFY'
                ]
            }), 404
        
        # Enhance results with stock data
        for result in unique_results:
            result['api_url'] = f'/stock?symbol={result["symbol"]}'
            result['nse_url'] = f'/stock?symbol={result["symbol"]}.NS'
            result['bse_url'] = f'/stock?symbol={result["symbol"]}.BO'
        
        return jsonify({
            'status': 'success',
            'query': query,
            'total_results': len(unique_results),
            'results': unique_results,
            'note': 'Add .NS for NSE or .BO for BSE to the symbol. Default is NSE.',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/stock', methods=['GET'])
def get_stock_price():
    """
    Get current stock price and details
    Usage: 
        - NSE: /stock?symbol=ITC or /stock?symbol=ITC.NS
        - BSE: /stock?symbol=ITC.BO
        - Simple values: /stock?symbol=ITC&res=num
        - With units: /stock?symbol=ITC&res=val (default)
    """
    try:
        symbol_input = request.args.get('symbol', '').upper()
        response_type = request.args.get('res', 'val').lower()  # 'num' or 'val'
        
        if not symbol_input:
            return jsonify({
                'status': 'error',
                'message': 'Please provide a stock symbol using ?symbol=STOCKNAME',
                'hint': 'Use /search?q=company_name to find the correct symbol',
                'examples': [
                    '/stock?symbol=ITC (NSE - default)',
                    '/stock?symbol=ITC.NS (NSE - explicit)',
                    '/stock?symbol=ITC.BO (BSE)'
                ]
            }), 400
        
        # Validate response type
        if response_type not in ['num', 'val']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid response type. Use res=num for numbers only or res=val for values with units',
                'examples': [
                    '/stock?symbol=ITC&res=num',
                    '/stock?symbol=ITC&res=val'
                ]
            }), 400
        
        with_units = (response_type == 'val')
        
        # Determine exchange from symbol
        clean_symbol, exchange_suffix = determine_exchange(symbol_input)
        ticker_symbol = f"{clean_symbol}{exchange_suffix}"
        
        # Determine exchange name
        exchange_name = "NSE" if exchange_suffix == ".NS" else "BSE"
        
        stock = yf.Ticker(ticker_symbol)
        
        # Get current data
        info = stock.info
        history = stock.history(period='5d')  # Get 5 days for better data
        
        if history.empty:
            return jsonify({
                'status': 'error',
                'message': f'No data found for symbol: {clean_symbol} on {exchange_name}. Stock may not exist or market is closed.',
                'hint': f'Try the other exchange: {clean_symbol}.BO' if exchange_name == 'NSE' else f'Try the other exchange: {clean_symbol}.NS',
                'note': 'Markets are closed on weekends and holidays'
            }), 404
        
        # Get latest available data
        latest_data = history.iloc[-1]
        current_price = latest_data['Close']
        open_price = latest_data['Open']
        high_price = latest_data['High']
        low_price = latest_data['Low']
        volume = int(latest_data['Volume'])
        
        previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', current_price))
        change = current_price - previous_close
        percent_change = (change / previous_close) * 100 if previous_close else 0
        
        response = {
            'status': 'success',
            'symbol': clean_symbol,
            'exchange': exchange_name,
            'ticker': ticker_symbol,
            'response_format': 'values_with_units' if with_units else 'numeric_only',
            'data': {
                'company_name': info.get('longName', info.get('shortName', clean_symbol)),
                
                # Price information
                'last_price': format_currency(current_price, with_units),
                'change': format_currency(change, with_units),
                'percent_change': format_percentage(percent_change, with_units),
                'previous_close': format_currency(previous_close, with_units),
                'open': format_currency(open_price, with_units),
                'day_high': format_currency(high_price, with_units),
                'day_low': format_currency(low_price, with_units),
                'year_high': format_currency(info.get('fiftyTwoWeekHigh', 0), with_units),
                'year_low': format_currency(info.get('fiftyTwoWeekLow', 0), with_units),
                
                # Volume and market data
                'volume': format_volume(volume, with_units),
                'market_cap': format_market_cap(info.get('marketCap', 'N/A'), with_units),
                'pe_ratio': format_ratio(info.get('trailingPE'), with_units),
                
                # Additional metrics
                'dividend_yield': format_percentage(info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 'N/A', with_units),
                'book_value': format_currency(info.get('bookValue', 'N/A'), with_units),
                'earnings_per_share': format_currency(info.get('trailingEps', 'N/A'), with_units),
                
                # Company information
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'currency': info.get('currency', 'INR'),
                'last_update': history.index[-1].strftime('%Y-%m-%d'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'alternate_exchange': {
                'exchange': 'BSE' if exchange_name == 'NSE' else 'NSE',
                'ticker': f"{clean_symbol}.BO" if exchange_name == 'NSE' else f"{clean_symbol}.NS",
                'api_url': f"/stock?symbol={clean_symbol}.BO" if exchange_name == 'NSE' else f"/stock?symbol={clean_symbol}.NS"
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching stock data: {str(e)}',
            'symbol': symbol_input if 'symbol_input' in locals() else 'N/A',
            'hint': 'Make sure the stock symbol is valid. Use /search?q=company_name to find the correct symbol'
        }), 500


@app.route('/stock/list', methods=['GET'])
def list_stocks():
    """
    Get details for multiple stocks
    Usage: 
        - NSE: /stock/list?symbols=ITC,TCS,INFY
        - Mixed: /stock/list?symbols=ITC.NS,TCS.BO,INFY
        - Simple values: /stock/list?symbols=ITC,TCS&res=num
        - With units: /stock/list?symbols=ITC,TCS&res=val (default)
    """
    try:
        symbols_param = request.args.get('symbols', '')
        response_type = request.args.get('res', 'val').lower()  # 'num' or 'val'
        
        if not symbols_param:
            return jsonify({
                'status': 'error',
                'message': 'Please provide stock symbols using ?symbols=STOCK1,STOCK2',
                'examples': [
                    '/stock/list?symbols=ITC,TCS,INFY (default NSE)',
                    '/stock/list?symbols=ITC.NS,TCS.BO,INFY (mixed exchanges)'
                ]
            }), 400
        
        # Validate response type
        if response_type not in ['num', 'val']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid response type. Use res=num for numbers only or res=val for values with units'
            }), 400
        
        with_units = (response_type == 'val')
        
        symbols = [s.strip().upper() for s in symbols_param.split(',')]
        results = []
        
        for symbol_input in symbols:
            try:
                # Determine exchange from symbol
                clean_symbol, exchange_suffix = determine_exchange(symbol_input)
                ticker_symbol = f"{clean_symbol}{exchange_suffix}"
                exchange_name = "NSE" if exchange_suffix == ".NS" else "BSE"
                
                stock = yf.Ticker(ticker_symbol)
                history = stock.history(period='5d')
                info = stock.info
                
                if not history.empty:
                    latest_data = history.iloc[-1]
                    current_price = latest_data['Close']
                    previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', current_price))
                    change = current_price - previous_close
                    percent_change = (change / previous_close) * 100 if previous_close else 0
                    
                    results.append({
                        'symbol': clean_symbol,
                        'exchange': exchange_name,
                        'ticker': ticker_symbol,
                        'company_name': info.get('longName', info.get('shortName', clean_symbol)),
                        'last_price': format_currency(current_price, with_units),
                        'change': format_currency(change, with_units),
                        'percent_change': format_percentage(percent_change, with_units),
                        'volume': format_volume(latest_data['Volume'], with_units),
                        'market_cap': format_market_cap(info.get('marketCap', 'N/A'), with_units),
                        'pe_ratio': format_ratio(info.get('trailingPE'), with_units),
                        'sector': info.get('sector', 'N/A')
                    })
                else:
                    results.append({
                        'symbol': clean_symbol,
                        'exchange': exchange_name,
                        'ticker': ticker_symbol,
                        'error': 'No data available'
                    })
            except Exception as e:
                results.append({
                    'symbol': symbol_input,
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'response_format': 'values_with_units' if with_units else 'numeric_only',
            'count': len(results),
            'stocks': results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing request: {str(e)}'
        }), 500


@app.route('/symbols', methods=['GET'])
def list_available_symbols():
    """
    List all cached symbols
    Usage: /symbols
    """
    symbols_list = []
    for company, symbol in NSE_SYMBOLS_CACHE.items():
        symbols_list.append({
            'search_term': company,
            'symbol': symbol,
            'nse_ticker': f'{symbol}.NS',
            'bse_ticker': f'{symbol}.BO',
            'api_url_nse': f'/stock?symbol={symbol}.NS',
            'api_url_bse': f'/stock?symbol={symbol}.BO'
        })
    
    return jsonify({
        'status': 'success',
        'total_symbols': len(symbols_list),
        'symbols': symbols_list,
        'note': 'Most stocks are available on both NSE (.NS) and BSE (.BO). Default is NSE.'
    }), 200


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'message': 'NSE/BSE Stock Price API with Smart Search & Flexible Output',
        'version': '2.4',
        'status': 'operational',
        'features': [
            'Support for both NSE and BSE exchanges',
            'Automatic exchange detection from symbol suffix',
            'Multi-source search (NSE API + Local Cache + Yahoo Finance)',
            'Real-time stock prices via Yahoo Finance',
            '30+ pre-cached popular stock symbols',
            'Flexible output: Simple numbers OR Values with units',
            'Smart number formatting for readability'
        ],
        'exchanges': {
            'NSE': {
                'description': 'National Stock Exchange',
                'suffix': '.NS',
                'example': 'ITC.NS, RELIANCE.NS',
                'default': True
            },
            'BSE': {
                'description': 'Bombay Stock Exchange',
                'suffix': '.BO',
                'example': 'ITC.BO, RELIANCE.BO',
                'default': False
            }
        },
        'endpoints': {
            '/search': {
                'description': 'Search for stocks by company name',
                'method': 'GET',
                'parameters': 'q=SEARCH_TERM',
                'examples': [
                    '/search?q=indian oil',
                    '/search?q=reliance'
                ]
            },
            '/stock': {
                'description': 'Get single stock details',
                'method': 'GET',
                'parameters': 'symbol=STOCK_SYMBOL, res=num|val (optional)',
                'examples': [
                    '/stock?symbol=ITC (default NSE)',
                    '/stock?symbol=ITC.NS (NSE explicit)',
                    '/stock?symbol=ITC.BO (BSE)',
                    '/stock?symbol=RELIANCE.NS&res=num',
                    '/stock?symbol=TCS.BO&res=val'
                ]
            },
            '/stock/list': {
                'description': 'Get multiple stock details',
                'method': 'GET',
                'parameters': 'symbols=STOCK1,STOCK2, res=num|val (optional)',
                'examples': [
                    '/stock/list?symbols=ITC,TCS,INFY (default NSE)',
                    '/stock/list?symbols=ITC.NS,TCS.BO,INFY.NS (mixed)',
                    '/stock/list?symbols=RELIANCE.BO,HDFCBANK.NS&res=num'
                ]
            },
            '/symbols': {
                'description': 'List all available cached symbols with both NSE and BSE tickers',
                'method': 'GET',
                'example': '/symbols'
            }
        },
        'usage_guide': {
            'default_behavior': 'If no exchange suffix is provided, NSE (.NS) is used by default',
            'nse_examples': ['ITC', 'ITC.NS', 'RELIANCE', 'RELIANCE.NS'],
            'bse_examples': ['ITC.BO', 'RELIANCE.BO', 'TCS.BO'],
            'mixed_request': 'You can mix NSE and BSE symbols in /stock/list endpoint'
        },
        'response_formats': {
            'res=num': 'Simple numeric values (e.g., "pe_ratio": 21.65)',
            'res=val': 'Values with units (e.g., "pe_ratio": {"value": 21.65, "unit": "x"})'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
