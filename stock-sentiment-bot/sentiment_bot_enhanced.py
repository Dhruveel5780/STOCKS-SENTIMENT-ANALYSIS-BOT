#!/usr/bin/env python3
"""
Enhanced Stock Sentiment Analysis Bot
Analyzes news sentiment for stock trading recommendations using Yahoo Finance
Now supports company name input with automatic ticker resolution
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import json
import re
from difflib import get_close_matches
import yfinance as yf

# Load environment variables
load_dotenv()

class StockSentimentBot:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        print("ℹ️  Using Yahoo Finance for news data - no API key required!")
        
        # Initialize company-to-ticker mapping
        self.company_ticker_map = self._load_company_ticker_mapping()
    
    def _load_company_ticker_mapping(self):
        """
        Load a comprehensive mapping of company names to stock tickers
        """
        return {
            # US Tech Giants
            'apple': 'AAPL',
            'apple inc': 'AAPL',
            'apple incorporated': 'AAPL',
            'microsoft': 'MSFT',
            'microsoft corporation': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'alphabet inc': 'GOOGL',
            'amazon': 'AMZN',
            'amazon.com': 'AMZN',
            'amazon inc': 'AMZN',
            'tesla': 'TSLA',
            'tesla inc': 'TSLA',
            'tesla motors': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'meta platforms': 'META',
            'nvidia': 'NVDA',
            'nvidia corporation': 'NVDA',
            'netflix': 'NFLX',
            'netflix inc': 'NFLX',
            'amd': 'AMD',
            'advanced micro devices': 'AMD',
            'intel': 'INTC',
            'intel corporation': 'INTC',
            'qualcomm': 'QCOM',
            'broadcom': 'AVGO',
            'oracle': 'ORCL',
            'salesforce': 'CRM',
            'adobe': 'ADBE',
            'adobe systems': 'ADBE',
            'zoom': 'ZM',
            'zoom video': 'ZM',
            'uber': 'UBER',
            'lyft': 'LYFT',
            'airbnb': 'ABNB',
            'palantir': 'PLTR',
            'snowflake': 'SNOW',
            'coinbase': 'COIN',
            'robinhood': 'HOOD',
            'square': 'SQ',
            'block': 'SQ',
            'paypal': 'PYPL',
            'shopify': 'SHOP',
            'spotify': 'SPOT',
            'twitter': 'TWTR',
            'snap': 'SNAP',
            'snapchat': 'SNAP',
            'pinterest': 'PINS',
            'roku': 'ROKU',
            'peloton': 'PTON',
            'zoom': 'ZM',
            'docusign': 'DOCU',
            'slack': 'WORK',
            'atlassian': 'TEAM',
            'servicenow': 'NOW',
            'workday': 'WDAY',
            'splunk': 'SPLK',
            'mongodb': 'MDB',
            'twilio': 'TWLO',
            'okta': 'OKTA',
            'crowdstrike': 'CRWD',
            'zscaler': 'ZS',
            'cloudflare': 'NET',
            'datadog': 'DDOG',
            'elastic': 'ESTC',
            'unity': 'U',
            'unity software': 'U',
            'roblox': 'RBLX',
            'electronic arts': 'EA',
            'ea': 'EA',
            'activision blizzard': 'ATVI',
            'activision': 'ATVI',
            'take-two': 'TTWO',
            'take two': 'TTWO',
            
            # Indian Companies
            'reliance': 'RELIANCE.NS',
            'reliance industries': 'RELIANCE.NS',
            'reliance industries limited': 'RELIANCE.NS',
            'ril': 'RELIANCE.NS',
            'tata consultancy services': 'TCS.NS',
            'tcs': 'TCS.NS',
            'infosys': 'INFY.NS',
            'infosys limited': 'INFY.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'housing development finance corporation': 'HDFC.NS',
            'hdfc': 'HDFC.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'state bank of india': 'SBIN.NS',
            'sbi': 'SBIN.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'itc limited': 'ITC.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'hul': 'HINDUNILVR.NS',
            'larsen and toubro': 'LT.NS',
            'l&t': 'LT.NS',
            'lt': 'LT.NS',
            'wipro': 'WIPRO.NS',
            'wipro limited': 'WIPRO.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'maruti suzuki': 'MARUTI.NS',
            'maruti': 'MARUTI.NS',
            'asian paints': 'ASIANPAINT.NS',
            'mahindra and mahindra': 'M&M.NS',
            'mahindra': 'M&M.NS',
            'm&m': 'M&M.NS',
            'tata motors': 'TATAMOTORS.NS',
            'sun pharmaceutical': 'SUNPHARMA.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'axis bank': 'AXISBANK.NS',
            'kotak mahindra bank': 'KOTAKBANK.NS',
            'kotak bank': 'KOTAKBANK.NS',
            'kotak': 'KOTAKBANK.NS',
            'ultratech cement': 'ULTRACEMCO.NS',
            'ultratech': 'ULTRACEMCO.NS',
            'nestle india': 'NESTLEIND.NS',
            'nestle': 'NESTLEIND.NS',
            'power grid corporation': 'POWERGRID.NS',
            'powergrid': 'POWERGRID.NS',
            'ntpc': 'NTPC.NS',
            'national thermal power corporation': 'NTPC.NS',
            'coal india': 'COALINDIA.NS',
            'ongc': 'ONGC.NS',
            'oil and natural gas corporation': 'ONGC.NS',
            'indian oil corporation': 'IOC.NS',
            'ioc': 'IOC.NS',
            'grasim industries': 'GRASIM.NS',
            'grasim': 'GRASIM.NS',
            'adani enterprises': 'ADANIENT.NS',
            'adani': 'ADANIENT.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'titan': 'TITAN.NS',
            'titan company': 'TITAN.NS',
            'dr reddy': 'DRREDDY.NS',
            'dr reddys laboratories': 'DRREDDY.NS',
            'dr reddy laboratories': 'DRREDDY.NS',
            'cipla': 'CIPLA.NS',
            'britannia industries': 'BRITANNIA.NS',
            'britannia': 'BRITANNIA.NS',
            'tech mahindra': 'TECHM.NS',
            'hero motocorp': 'HEROMOTOCO.NS',
            'hero': 'HEROMOTOCO.NS',
            'eicher motors': 'EICHERMOT.NS',
            'eicher': 'EICHERMOT.NS',
            'shree cement': 'SHREECEM.NS',
            'divis laboratories': 'DIVISLAB.NS',
            'divis lab': 'DIVISLAB.NS',
            'sbi life insurance': 'SBILIFE.NS',
            'sbi life': 'SBILIFE.NS',
            'hdfc life insurance': 'HDFCLIFE.NS',
            'hdfc life': 'HDFCLIFE.NS',
            'bajaj finserv': 'BAJAJFINSV.NS',
            'indusind bank': 'INDUSINDBK.NS',
            'indusind': 'INDUSINDBK.NS',
            'zee entertainment': 'ZEEL.NS',
            'zee': 'ZEEL.NS',
            'vedanta': 'VEDL.NS',
            'vedanta limited': 'VEDL.NS',
            'tata steel': 'TATASTEEL.NS',
            'jsw steel': 'JSWSTEEL.NS',
            'jsw': 'JSWSTEEL.NS',
            'hindalco': 'HINDALCO.NS',
            'hindalco industries': 'HINDALCO.NS',
            'upl': 'UPL.NS',
            'upl limited': 'UPL.NS',
            'hcl technologies': 'HCLTECH.NS',
            'hcl tech': 'HCLTECH.NS',
            'hcl': 'HCLTECH.NS',
            'godrej consumer products': 'GODREJCP.NS',
            'godrej': 'GODREJCP.NS',
            'dabur': 'DABUR.NS',
            'dabur india': 'DABUR.NS',
            'pidilite industries': 'PIDILITIND.NS',
            'pidilite': 'PIDILITIND.NS',
            'berger paints': 'BERGEPAINT.NS',
            'berger': 'BERGEPAINT.NS',
            'marico': 'MARICO.NS',
            'marico limited': 'MARICO.NS',
            'colgate palmolive': 'COLPAL.NS',
            'colgate': 'COLPAL.NS',
            'hindustan zinc': 'HINDZINC.NS',
            'hindzinc': 'HINDZINC.NS',
            'muthoot finance': 'MUTHOOTFIN.NS',
            'muthoot': 'MUTHOOTFIN.NS',
            'bajaj holdings': 'BAJAJHLDNG.NS',
            'avenue supermarts': 'DMART.NS',
            'dmart': 'DMART.NS',
            'info edge': 'NAUKRI.NS',
            'naukri': 'NAUKRI.NS',
            'zomato': 'ZOMATO.NS',
            'paytm': 'PAYTM.NS',
            'one97 communications': 'PAYTM.NS',
            'policybazaar': 'POLICYBZR.NS',
            'pb fintech': 'POLICYBZR.NS',
            'nykaa': 'NYKAA.NS',
            'fsl nykaa': 'NYKAA.NS',
            'byju': 'BYJUS.NS',
            'byjus': 'BYJUS.NS',
            'ola': 'OLA.NS',
            'ola electric': 'OLA.NS',
            'swiggy': 'SWIGGY.NS',
            'flipkart': 'FLIPKART.NS',
            'tata group': 'TATACONSUM.NS',
            'tata consumer': 'TATACONSUM.NS',
            'tata consumer products': 'TATACONSUM.NS',
            'tata power': 'TATAPOWER.NS',
            'tata chemicals': 'TATACHEM.NS',
            'tata communications': 'TATACOMM.NS',
            'tata elxsi': 'TATAELXSI.NS',
            'voltas': 'VOLTAS.NS',
            'indian hotels': 'INDHOTEL.NS',
            'taj hotels': 'INDHOTEL.NS',
            
            # US Financial
            'jpmorgan': 'JPM',
            'jpmorgan chase': 'JPM',
            'jp morgan': 'JPM',
            'bank of america': 'BAC',
            'wells fargo': 'WFC',
            'goldman sachs': 'GS',
            'morgan stanley': 'MS',
            'citigroup': 'C',
            'citi': 'C',
            'american express': 'AXP',
            'amex': 'AXP',
            'visa': 'V',
            'mastercard': 'MA',
            'berkshire hathaway': 'BRK.A',
            'berkshire': 'BRK.A',
            'blackrock': 'BLK',
            'charles schwab': 'SCHW',
            'schwab': 'SCHW',
            
            # US Healthcare
            'johnson and johnson': 'JNJ',
            'johnson & johnson': 'JNJ',
            'j&j': 'JNJ',
            'pfizer': 'PFE',
            'merck': 'MRK',
            'merck & co': 'MRK',
            'abbott': 'ABT',
            'abbott laboratories': 'ABT',
            'bristol myers squibb': 'BMY',
            'bms': 'BMY',
            'eli lilly': 'LLY',
            'lilly': 'LLY',
            'unitedhealth': 'UNH',
            'united health': 'UNH',
            'astrazeneca': 'AZN',
            'novartis': 'NVS',
            'roche': 'RHHBY',
            'glaxosmithkline': 'GSK',
            'gsk': 'GSK',
            'gilead sciences': 'GILD',
            'gilead': 'GILD',
            'amgen': 'AMGN',
            'biogen': 'BIIB',
            'regeneron': 'REGN',
            'moderna': 'MRNA',
            'biontech': 'BNTX',
            'vertex pharmaceuticals': 'VRTX',
            'vertex': 'VRTX',
            'illumina': 'ILMN',
            'danaher': 'DHR',
            'thermo fisher': 'TMO',
            'thermo fisher scientific': 'TMO',
            
            # US Consumer
            'walmart': 'WMT',
            'wal-mart': 'WMT',
            'target': 'TGT',
            'costco': 'COST',
            'home depot': 'HD',
            'lowes': 'LOW',
            'starbucks': 'SBUX',
            'mcdonalds': 'MCD',
            'mcdonald\'s': 'MCD',
            'coca cola': 'KO',
            'coca-cola': 'KO',
            'pepsi': 'PEP',
            'pepsico': 'PEP',
            'procter gamble': 'PG',
            'procter & gamble': 'PG',
            'p&g': 'PG',
            'nike': 'NKE',
            'adidas': 'ADDYY',
            'disney': 'DIS',
            'walt disney': 'DIS',
            'comcast': 'CMCSA',
            'at&t': 'T',
            'att': 'T',
            'verizon': 'VZ',
            't-mobile': 'TMUS',
            'tmobile': 'TMUS',
            'general motors': 'GM',
            'gm': 'GM',
            'ford': 'F',
            'ford motor': 'F',
            'tesla': 'TSLA',
            
            # US Industrial
            'boeing': 'BA',
            'caterpillar': 'CAT',
            'general electric': 'GE',
            'ge': 'GE',
            'honeywell': 'HON',
            '3m': 'MMM',
            'mmm': 'MMM',
            'lockheed martin': 'LMT',
            'lockheed': 'LMT',
            'raytheon': 'RTX',
            'raytheon technologies': 'RTX',
            'northrop grumman': 'NOC',
            'northrop': 'NOC',
            'union pacific': 'UNP',
            'csx': 'CSX',
            'norfolk southern': 'NSC',
            'fedex': 'FDX',
            'ups': 'UPS',
            'united parcel service': 'UPS',
            'deere': 'DE',
            'john deere': 'DE',
            'caterpillar': 'CAT',
            'emerson electric': 'EMR',
            'emerson': 'EMR',
            'parker hannifin': 'PH',
            'parker': 'PH',
            'stanley black decker': 'SWK',
            'stanley': 'SWK',
            'illinois tool works': 'ITW',
            'itw': 'ITW',
            'eaton': 'ETN',
            'eaton corporation': 'ETN',
            'fortive': 'FTV',
            'ingersoll rand': 'IR',
            'ingersoll': 'IR',
            'dover': 'DOV',
            'dover corporation': 'DOV',
            'waste management': 'WM',
            'wm': 'WM',
            'republic services': 'RSG',
            'republic': 'RSG',
            
            # Energy
            'chevron': 'CVX',
            'exxon mobil': 'XOM',
            'exxon': 'XOM',
            'conocophillips': 'COP',
            'schlumberger': 'SLB',
            'halliburton': 'HAL',
            'marathon petroleum': 'MPC',
            'marathon': 'MPC',
            'phillips 66': 'PSX',
            'valero': 'VLO',
            'valero energy': 'VLO',
            'kinder morgan': 'KMI',
            'kinder': 'KMI',
            'enterprise products': 'EPD',
            'enterprise': 'EPD',
            'enbridge': 'ENB',
            'tc energy': 'TRP',
            'eog resources': 'EOG',
            'eog': 'EOG',
            'pioneer natural resources': 'PXD',
            'pioneer': 'PXD',
            'devon energy': 'DVN',
            'devon': 'DVN',
            'hess': 'HES',
            'hess corporation': 'HES',
            'marathon oil': 'MRO',
            'apache': 'APA',
            'apache corporation': 'APA',
            'suncor energy': 'SU',
            'suncor': 'SU',
            'canadian natural resources': 'CNQ',
            'cnq': 'CNQ',
            'cenovus energy': 'CVE',
            'cenovus': 'CVE',
            'imperial oil': 'IMO',
            'imperial': 'IMO',
            'husky energy': 'HSE',
            'husky': 'HSE',
            'meg energy': 'MEG',
            'meg': 'MEG',
            'crescent point energy': 'CPG',
            'crescent point': 'CPG',
            'arc resources': 'ARX',
            'arc': 'ARX',
            'tourmaline oil': 'TOU',
            'tourmaline': 'TOU',
            'birchcliff energy': 'BIR',
            'birchcliff': 'BIR',
            'peyto exploration': 'PEY',
            'peyto': 'PEY',
            'nuvista energy': 'NVA',
            'nuvista': 'NVA',
            'paramount resources': 'POU',
            'paramount': 'POU',
            'advantage oil gas': 'AAV',
            'advantage': 'AAV',
            'cardinal energy': 'CJ',
            'cardinal': 'CJ',
            'baytex energy': 'BTE',
            'baytex': 'BTE',
            'gear energy': 'GXE',
            'gear': 'GXE',
            'tamarack valley energy': 'TVE',
            'tamarack valley': 'TVE',
            'tamarack': 'TVE',
            'journey energy': 'JOY',
            'journey': 'JOY',
            'surge energy': 'SGY',
            'surge': 'SGY',
            'bonterra energy': 'BNE',
            'bonterra': 'BNE',
            'pine cliff energy': 'PNE',
            'pine cliff': 'PNE',
            'obsidian energy': 'OBE',
            'obsidian': 'OBE',
            'storm resources': 'SRX',
            'storm': 'SRX',
            'yangarra resources': 'YGR',
            'yangarra': 'YGR',
            'crew energy': 'CR',
            'crew': 'CR',
            'kelt exploration': 'KEL',
            'kelt': 'KEL',
            'prairie provident resources': 'PPR',
            'prairie provident': 'PPR',
            'prairie': 'PPR',
            'pieridae energy': 'PEA',
            'pieridae': 'PEA',
            'questerre energy': 'QEC',
            'questerre': 'QEC',
            'northland power': 'NPI',
            'northland': 'NPI',
            'innergex renewable energy': 'INE',
            'innergex': 'INE',
            'boralex': 'BLX',
            'transalta': 'TA',
            'transalta renewables': 'RNW',
            'capital power': 'CPX',
            'capital': 'CPX',
            'algonquin power': 'AQN',
            'algonquin': 'AQN',
            'fortis': 'FTS',
            'emera': 'EMA',
            'hydro one': 'H',
            'hydro': 'H',
            'canadian utilities': 'CU',
            'canadian': 'CU',
            'atco': 'ACO.X',
            'pembina pipeline': 'PPL',
            'pembina': 'PPL',
            'tc energy': 'TRP',
            'tc': 'TRP',
            'inter pipeline': 'IPL',
            'inter': 'IPL',
            'keyera': 'KEY',
            'gibson energy': 'GEI',
            'gibson': 'GEI',
            'parkland': 'PKI',
            'parkland fuel': 'PKI',
            'superior plus': 'SPB',
            'superior': 'SPB',
            'altius minerals': 'ALS',
            'altius': 'ALS',
            'champion iron': 'CIA',
            'champion': 'CIA',
            'first quantum minerals': 'FM',
            'first quantum': 'FM',
            'hudbay minerals': 'HBM',
            'hudbay': 'HBM',
            'ivanhoe mines': 'IVN',
            'ivanhoe': 'IVN',
            'kinross gold': 'K',
            'kinross': 'K',
            'kirkland lake gold': 'KL',
            'kirkland lake': 'KL',
            'kirkland': 'KL',
            'newmont': 'NEM',
            'newmont goldcorp': 'NEM',
            'barrick gold': 'GOLD',
            'barrick': 'GOLD',
            'agnico eagle mines': 'AEM',
            'agnico eagle': 'AEM',
            'agnico': 'AEM',
            'yamana gold': 'YRI',
            'yamana': 'YRI',
            'eldorado gold': 'ELD',
            'eldorado': 'ELD',
            'iamgold': 'IAG',
            'torex gold': 'TXG',
            'torex': 'TXG',
            'b2gold': 'BTO',
            'centerra gold': 'CG',
            'centerra': 'CG',
            'endeavour silver': 'EDR',
            'endeavour': 'EDR',
            'first majestic silver': 'FR',
            'first majestic': 'FR',
            'hecla mining': 'HL',
            'hecla': 'HL',
            'pan american silver': 'PAAS',
            'pan american': 'PAAS',
            'silver wheaton': 'WPM',
            'wheaton precious metals': 'WPM',
            'wheaton': 'WPM',
            'franco nevada': 'FNV',
            'franco': 'FNV',
            'royal gold': 'RGLD',
            'royal': 'RGLD',
            'sandstorm gold': 'SAND',
            'sandstorm': 'SAND',
            'osisko gold royalties': 'OR',
            'osisko': 'OR',
            'alamos gold': 'AGI',
            'alamos': 'AGI',
            'new gold': 'NGD',
            'new': 'NGD',
            'pretium resources': 'PVG',
            'pretium': 'PVG',
            'kirkland lake gold': 'KL',
            'detour gold': 'DGC',
            'detour': 'DGC',
            'goldcorp': 'GG',
            'richmont mines': 'RIC',
            'richmont': 'RIC',
            'lake shore gold': 'LSG',
            'lake shore': 'LSG',
            'lake': 'LSG',
            'shore': 'LSG',
            'tahoe resources': 'TAHO',
            'tahoe': 'TAHO',
            'aurico gold': 'AUQ',
            'aurico': 'AUQ',
            'klondex mines': 'KDX',
            'klondex': 'KDX',
            'great panther mining': 'GPR',
            'great panther': 'GPR',
            'great': 'GPR',
            'panther': 'GPR',
            'mining': 'GPR',
            'fortuna silver mines': 'FSM',
            'fortuna silver': 'FSM',
            'fortuna': 'FSM',
            'silver': 'FSM',
            'mines': 'FSM',
            'coeur mining': 'CDE',
            'coeur': 'CDE',
            'silvercorp metals': 'SVM',
            'silvercorp': 'SVM',
            'metals': 'SVM',
            'mag silver': 'MAG',
            'mag': 'MAG',
            'impact silver': 'IPT',
            'impact': 'IPT',
            'silver tiger metals': 'SLVR',
            'silver tiger': 'SLVR',
            'tiger': 'SLVR',
            'silver elephant mining': 'ELEF',
            'silver elephant': 'ELEF',
            'elephant': 'ELEF',
            'silver one resources': 'SVE',
            'silver one': 'SVE',
            'one': 'SVE',
            'resources': 'SVE',
            'silver x mining': 'AGX',
            'silver x': 'AGX',
            'x': 'AGX',
            'silver range resources': 'SNG',
            'silver range': 'SNG',
            'range': 'SNG',
            'silver bull resources': 'SVB',
            'silver bull': 'SVB',
            'bull': 'SVB',
            'silver mountain resources': 'AGMR',
            'silver mountain': 'AGMR',
            'mountain': 'AGMR',
            'silver hammer mining': 'HAMR',
            'silver hammer': 'HAMR',
            'hammer': 'HAMR',
            'silver viper minerals': 'VIPR',
            'silver viper': 'VIPR',
            'viper': 'VIPR',
            'minerals': 'VIPR',
            'silver predator': 'SPD',
            'predator': 'SPD',
            'silver standard resources': 'SSRI',
            'silver standard': 'SSRI',
            'standard': 'SSRI',
            'silver crest metals': 'SILV',
            'silver crest': 'SILV',
            'crest': 'SILV',
            'silver lake resources': 'SLR',
            'silver lake': 'SLR',
            'lake': 'SLR',
            'silver mines': 'SVL',
            'silver city minerals': 'SCI',
            'silver city': 'SCI',
            'city': 'SCI',
            'silver consolidated': 'SLVC',
            'consolidated': 'SLVC',
            'silver grail resources': 'SIL',
            'silver grail': 'SIL',
            'grail': 'SIL',
            'silver penny resources': 'SPR',
            'silver penny': 'SPR',
            'penny': 'SPR',
            'silver wolf exploration': 'SWLF',
            'silver wolf': 'SWLF',
            'wolf': 'SWLF',
            'exploration': 'SWLF',
            'silver fox minerals': 'FOX',
            'silver fox': 'FOX',
            'fox': 'FOX',
            'silver bear resources': 'SBR',
            'silver bear': 'SBR',
            'bear': 'SBR',
            'silver eagle acquisition': 'EAGL',
            'silver eagle': 'EAGL',
            'eagle': 'EAGL',
            'acquisition': 'EAGL',
            'silver spike acquisition': 'SSPK',
            'silver spike': 'SSPK',
            'spike': 'SSPK',
            'silver rock resources': 'SRK',
            'silver rock': 'SRK',
            'rock': 'SRK',
            'silver storm mining': 'SVRS',
            'silver storm': 'SVRS',
            'storm': 'SVRS',
            'silver sands resources': 'SAND',
            'silver sands': 'SAND',
            'sands': 'SAND',
            'silver sea resources': 'SEA',
            'silver sea': 'SEA',
            'sea': 'SEA',
            'silver star mining': 'STAR',
            'silver star': 'STAR',
            'star': 'STAR',
            'silver sun mining': 'SUN',
            'silver sun': 'SUN',
            'sun': 'SUN',
            'silver sword resources': 'SWD',
            'silver sword': 'SWD',
            'sword': 'SWD',
            'silver shield resources': 'SHLD',
            'silver shield': 'SHLD',
            'shield': 'SHLD',
            'silver arrow minerals': 'SAM',
            'silver arrow': 'SAM',
            'arrow': 'SAM',
            'silver bullet mines': 'SBMI',
            'silver bullet': 'SBMI',
            'bullet': 'SBMI',
            'silver crown resources': 'SCR',
            'silver crown': 'SCR',
            'crown': 'SCR',
            'silver dragon resources': 'DGN',
            'silver dragon': 'DGN',
            'dragon': 'DGN',
            'silver falcon mining': 'SFMI',
            'silver falcon': 'SFMI',
            'falcon': 'SFMI',
            'silver giant mining': 'SGMI',
            'silver giant': 'SGMI',
            'giant': 'SGMI',
            'silver horse resources': 'SHR',
            'silver horse': 'SHR',
            'horse': 'SHR',
            'silver king resources': 'SKR',
            'silver king': 'SKR',
            'king': 'SKR',
            'silver lion resources': 'SLR',
            'silver lion': 'SLR',
            'lion': 'SLR',
            'silver moon mining': 'SMM',
            'silver moon': 'SMM',
            'moon': 'SMM',
            'silver phoenix resources': 'SPX',
            'silver phoenix': 'SPX',
            'phoenix': 'SPX',
            'silver quest resources': 'SQR',
            'silver quest': 'SQR',
            'quest': 'SQR',
            'silver ridge resources': 'SRR',
            'silver ridge': 'SRR',
            'ridge': 'SRR',
            'silver spirit resources': 'SSR',
            'silver spirit': 'SSR',
            'spirit': 'SSR',
            'silver thunder mining': 'STM',
            'silver thunder': 'STM',
            'thunder': 'STM',
            'silver unicorn resources': 'SUR',
            'silver unicorn': 'SUR',
            'unicorn': 'SUR',
            'silver warrior resources': 'SWR',
            'silver warrior': 'SWR',
            'warrior': 'SWR',
            'silver wing resources': 'SWG',
            'silver wing': 'SWG',
            'wing': 'SWG',
            'silver zone resources': 'SZR',
            'silver zone': 'SZR',
            'zone': 'SZR',
        }
    
    def find_stock_ticker(self, company_input):
        """
        Find stock ticker from company name or return as-is if it's already a ticker
        """
        # Clean the input
        cleaned_input = company_input.strip().lower()
        
        # Check if it's already a ticker (short alphanumeric string with optional suffix)
        if re.match(r'^[A-Z]{1,6}(\.[A-Z]{1,3})?$', company_input.upper()):
            return company_input.upper()
        
        # Direct match in our mapping
        if cleaned_input in self.company_ticker_map:
            return self.company_ticker_map[cleaned_input]
        
        # Try fuzzy matching for close matches
        close_matches = get_close_matches(cleaned_input, self.company_ticker_map.keys(), n=1, cutoff=0.8)
        if close_matches:
            return self.company_ticker_map[close_matches[0]]
        
        # Try partial matching (more aggressive)
        for company_name, ticker in self.company_ticker_map.items():
            if cleaned_input in company_name or company_name in cleaned_input:
                return ticker
        
        # Special handling for common patterns
        # Remove common suffixes and prefixes
        cleaned_for_search = re.sub(r'\b(inc|corp|corporation|ltd|limited|company|co|group|industries|technologies|tech|systems|solutions|services|international|global|holdings|enterprises|ventures|investments|capital|finance|financial|bank|insurance|motors|automotive|pharma|pharmaceutical|biotech|energy|oil|gas|mining|metals|steel|cement|paints|consumer|products|foods|beverages|retail|entertainment|media|communications|telecom|software|hardware|semiconductors|electronics|electrical|power|utilities|construction|engineering|real estate|reit|trust|fund|etf|index|acquisition|spac)\b', '', cleaned_input).strip()
        
        # Try matching with cleaned input
        if cleaned_for_search and cleaned_for_search in self.company_ticker_map:
            return self.company_ticker_map[cleaned_for_search]
        
        # Try partial matching with cleaned input
        for company_name, ticker in self.company_ticker_map.items():
            if cleaned_for_search in company_name or company_name in cleaned_for_search:
                return ticker
        
        # If no match found, try to extract potential ticker from input
        # Look for patterns like "AAPL" or "TSLA" in the input
        ticker_pattern = re.search(r'\b[A-Z]{2,6}\b', company_input.upper())
        if ticker_pattern:
            return ticker_pattern.group()
        
        # Return original input if no match found
        return company_input.upper()
    
    def get_company_suggestions(self, partial_name):
        """
        Get suggestions for partial company names
        """
        partial_name = partial_name.lower()
        suggestions = []
        
        # Direct matches first
        for company_name, ticker in self.company_ticker_map.items():
            if company_name.startswith(partial_name):
                suggestions.append(f"{company_name.title()} ({ticker})")
        
        # Then partial matches
        for company_name, ticker in self.company_ticker_map.items():
            if partial_name in company_name and f"{company_name.title()} ({ticker})" not in suggestions:
                suggestions.append(f"{company_name.title()} ({ticker})")
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def get_company_name_from_ticker(self, ticker):
        """
        Reverse lookup to get company name from ticker for consistent search
        """
        ticker_clean = ticker.replace('.NS', '').replace('.BO', '').replace('.A', '').replace('.B', '')
        
        # Reverse lookup in our mapping
        for company_name, mapped_ticker in self.company_ticker_map.items():
            if mapped_ticker == ticker or mapped_ticker.replace('.NS', '').replace('.BO', '') == ticker_clean:
                return company_name
        return None
    
    def fetch_news(self, stock_symbol):
        """
        Fetch news articles for a given stock symbol using yfinance
        """
        try:
            # Initialize yfinance ticker
            print(f"   Querying Yahoo Finance for {stock_symbol}...")
            ticker = yf.Ticker(stock_symbol)
            
            # Fetch news data using get_news() method
            news_data = ticker.get_news()
            
            if not news_data:
                return []
            
            # Parse and collect articles
            articles = []
            for item in news_data:
                # Extract content from the nested structure
                content = item.get('content', {})
                
                title = content.get('title', 'No Title')
                description = content.get('summary') or content.get('description', f"News about {stock_symbol}: {title}")
                source = content.get('provider', {}).get('displayName', 'Yahoo Finance')
                published = content.get('pubDate', '')
                url = content.get('canonicalUrl', {}).get('url', '') or content.get('clickThroughUrl', {}).get('url', '')
                
                # Only add articles with valid content
                if title and title != 'No Title' and description:
                    articles.append({
                        'title': title,
                        'description': description,
                        'source': source,
                        'publishedAt': published,
                        'url': url
                    })
            
            print(f"   Retrieved {len(articles)} valid articles")
            return articles
            
        except Exception as e:
            print(f"Error fetching news from Yahoo Finance: {e}")
            print("   Trying alternative ticker format...")
            
            # Try alternative ticker formats if the first attempt fails
            alternative_tickers = []
            
            # For Indian stocks, try without .NS
            if '.NS' in stock_symbol:
                alternative_tickers.append(stock_symbol.replace('.NS', ''))
            # For US stocks, try different formats
            elif not any(suffix in stock_symbol for suffix in ['.', '-']):
                alternative_tickers.extend([f"{stock_symbol}"])
            
            for alt_ticker in alternative_tickers:
                try:
                    print(f"   Trying alternative ticker: {alt_ticker}")
                    ticker_alt = yf.Ticker(alt_ticker)
                    news_data_alt = ticker_alt.get_news()
                    
                    if news_data_alt:
                        articles = []
                        for item in news_data_alt:
                            content = item.get('content', {})
                            
                            title = content.get('title', 'No Title')
                            description = content.get('summary') or content.get('description', f"News about {alt_ticker}: {title}")
                            source = content.get('provider', {}).get('displayName', 'Yahoo Finance')
                            published = content.get('pubDate', '')
                            url = content.get('canonicalUrl', {}).get('url', '') or content.get('clickThroughUrl', {}).get('url', '')
                            
                            if title and title != 'No Title' and description:
                                articles.append({
                                    'title': title,
                                    'description': description,
                                    'source': source,
                                    'publishedAt': published,
                                    'url': url
                                })
                        
                        if articles:
                            print(f"   Success with {alt_ticker}! Retrieved {len(articles)} articles")
                            return articles
                            
                except Exception as alt_error:
                    print(f"   Alternative ticker {alt_ticker} also failed: {alt_error}")
                    continue
            
            return []
    
    def clean_and_deduplicate(self, articles):
        """
        Clean and remove duplicate articles
        """
        if not articles:
            return []
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(articles)
        
        # Remove articles with null titles or descriptions
        df = df.dropna(subset=['title', 'description'])
        
        # Remove duplicates based on title similarity
        df = df.drop_duplicates(subset=['title'], keep='first')
        
        # Filter out articles that might not be relevant
        df = df[df['title'].str.len() > 10]  # Remove very short titles
        
        return df.to_dict('records')
    
    def analyze_sentiment_textblob(self, text):
        """
        Analyze sentiment using TextBlob
        Returns polarity (-1 to 1) and subjectivity (0 to 1)
        """
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except Exception as e:
            print(f"TextBlob error: {e}")
            return 0, 0
    
    def analyze_sentiment_vader(self, text):
        """
        Analyze sentiment using VADER
        Returns compound score (-1 to 1)
        """
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return scores['compound']
        except Exception as e:
            print(f"VADER error: {e}")
            return 0
    
    def calculate_sentiment_scores(self, articles):
        """
        Calculate sentiment scores for all articles
        """
        sentiment_data = []
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            # TextBlob analysis
            tb_polarity, tb_subjectivity = self.analyze_sentiment_textblob(text)
            
            # VADER analysis
            vader_score = self.analyze_sentiment_vader(text)
            
            # Average the two sentiment scores
            average_sentiment = (tb_polarity + vader_score) / 2
            
            sentiment_data.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', 'Unknown'),
                'publishedAt': article.get('publishedAt', ''),
                'url': article.get('url', ''),
                'textblob_polarity': tb_polarity,
                'textblob_subjectivity': tb_subjectivity,
                'vader_score': vader_score,
                'average_sentiment': average_sentiment
            })
        
        return sentiment_data
    
    def classify_sentiment(self, score):
        """
        Classify sentiment score into categories
        """
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def calculate_confidence_level(self, avg_sentiment, sentiment_distribution, total_articles):
        """
        Calculate a more meaningful confidence level based on multiple factors
        """
        # Factor 1: Sentiment strength (0-40 points)
        sentiment_strength = min(abs(avg_sentiment) * 100, 40)
        
        # Factor 2: Consensus level (0-30 points)
        max_category_ratio = max(sentiment_distribution.values()) if sentiment_distribution else 0
        consensus_score = max_category_ratio * 30
        
        # Factor 3: Sample size factor (0-20 points)
        if total_articles >= 20:
            sample_score = 20
        elif total_articles >= 10:
            sample_score = 15
        elif total_articles >= 5:
            sample_score = 10
        else:
            sample_score = 5
        
        # Factor 4: Distribution clarity (0-10 points)
        # Higher score if sentiment is not neutral
        neutral_ratio = sentiment_distribution.get('Neutral', 0)
        clarity_score = (1 - neutral_ratio) * 10
        
        # Total confidence (0-100)
        total_confidence = sentiment_strength + consensus_score + sample_score + clarity_score
        
        return min(total_confidence, 100)  # Cap at 100%
    
    def generate_trading_recommendation(self, avg_sentiment, sentiment_distribution):
        """
        Generate buy/sell/hold recommendation based on sentiment analysis
        """
        positive_ratio = sentiment_distribution.get('Positive', 0)
        negative_ratio = sentiment_distribution.get('Negative', 0)
        neutral_ratio = sentiment_distribution.get('Neutral', 0)
        
        # Decision logic with more nuanced thresholds
        if avg_sentiment >= 0.15 and positive_ratio >= 0.7:
            return "BUY", "Very strong positive sentiment indicates potential upward movement"
        elif avg_sentiment >= 0.1 and positive_ratio >= 0.6:
            return "BUY", "Strong positive sentiment indicates potential upward movement"
        elif avg_sentiment >= 0.05 and positive_ratio >= 0.5:
            return "HOLD", "Moderately positive sentiment suggests maintaining position"
        elif avg_sentiment <= -0.15 and negative_ratio >= 0.7:
            return "SELL", "Very strong negative sentiment indicates potential downward movement"
        elif avg_sentiment <= -0.1 and negative_ratio >= 0.6:
            return "SELL", "Strong negative sentiment indicates potential downward movement"
        elif avg_sentiment <= -0.05 and negative_ratio >= 0.5:
            return "HOLD", "Moderately negative sentiment suggests caution"
        else:
            return "HOLD", "Mixed or neutral sentiment suggests waiting for clearer signals"
    
    def analyze_stock_sentiment(self, company_input):
        """
        Main method to analyze stock sentiment and provide recommendation
        """
        # Convert company name to stock ticker
        print(f"\n🔍 Processing input: '{company_input}'")
        stock_symbol = self.find_stock_ticker(company_input)
        
        if stock_symbol != company_input.upper():
            print(f"📊 Found ticker: {stock_symbol} for '{company_input}'")
        else:
            print(f"📊 Using ticker: {stock_symbol}")
        
        print(f"\n🔍 Analyzing sentiment for {stock_symbol}...")
        print("=" * 50)
        
        # Fetch news
        print("📰 Fetching latest news from Yahoo Finance...")
        articles = self.fetch_news(stock_symbol)
        
        if not articles:
            print(f"❌ No news articles found for {stock_symbol} on Yahoo Finance.")
            print("   This could be due to:")
            print("   - Invalid ticker symbol")
            print("   - No recent news available")
            print("   - Connectivity issues with Yahoo Finance")
            return
        
        print(f"📊 Found {len(articles)} articles")
        
        # Clean and deduplicate
        print("🧹 Cleaning and deduplicating articles...")
        clean_articles = self.clean_and_deduplicate(articles)
        print(f"✅ {len(clean_articles)} articles after cleaning")
        
        if not clean_articles:
            print("❌ No valid articles found after cleaning.")
            return
        
        # Analyze sentiment
        print("🤖 Analyzing sentiment...")
        sentiment_data = self.calculate_sentiment_scores(clean_articles)
        
        # Calculate statistics
        sentiment_scores = [item['average_sentiment'] for item in sentiment_data]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Classify sentiments
        sentiment_labels = [self.classify_sentiment(score) for score in sentiment_scores]
        sentiment_counts = Counter(sentiment_labels)
        total_articles = len(sentiment_labels)
        
        sentiment_distribution = {
            label: count / total_articles 
            for label, count in sentiment_counts.items()
        }
        
        # Generate recommendation
        recommendation, reason = self.generate_trading_recommendation(avg_sentiment, sentiment_distribution)
        
        # Display results
        print("\n📈 SENTIMENT ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Company: {company_input}")
        print(f"Stock Symbol: {stock_symbol}")
        print(f"Analysis Period: Last 7 days")
        print(f"Articles Analyzed: {total_articles}")
        print(f"Average Sentiment Score: {avg_sentiment:.3f}")
        print(f"Sentiment Scale: -1 (Very Negative) to +1 (Very Positive)")
        
        print("\n📊 SENTIMENT DISTRIBUTION")
        print("-" * 30)
        for label, ratio in sentiment_distribution.items():
            percentage = ratio * 100
            print(f"{label}: {percentage:.1f}% ({sentiment_counts[label]} articles)")
        
        print(f"\n🎯 TRADING RECOMMENDATION: {recommendation}")
        print(f"Reasoning: {reason}")
        
        # Calculate and show improved confidence level
        confidence = self.calculate_confidence_level(avg_sentiment, sentiment_distribution, total_articles)
        print(f"Confidence Level: {confidence:.1f}%")
        
        # Add confidence explanation
        if confidence >= 80:
            confidence_desc = "Very High"
        elif confidence >= 60:
            confidence_desc = "High"
        elif confidence >= 40:
            confidence_desc = "Moderate"
        elif confidence >= 20:
            confidence_desc = "Low"
        else:
            confidence_desc = "Very Low"
        
        print(f"Confidence Description: {confidence_desc}")
        
        # Show recent headlines
        print("\n📰 RECENT HEADLINES ANALYZED")
        print("-" * 50)
        for i, item in enumerate(sentiment_data[:5], 1):
            sentiment_label = self.classify_sentiment(item['average_sentiment'])
            print(f"{i}. [{sentiment_label}] {item['title']}")
            print(f"   Source: {item['source']} | Score: {item['average_sentiment']:.3f}")
            print()
        
        return {
            'company_input': company_input,
            'stock_symbol': stock_symbol,
            'average_sentiment': avg_sentiment,
            'sentiment_distribution': sentiment_distribution,
            'recommendation': recommendation,
            'reason': reason,
            'confidence': confidence,
            'articles_analyzed': total_articles,
            'detailed_analysis': sentiment_data
        }

def main():
    """
    Main function to run the sentiment analysis bot
    """
    print("🚀 Welcome to the Enhanced Stock Sentiment Analysis Bot!")
    print("💡 You can now enter company names or stock symbols!")
    print("📝 Examples: 'Apple', 'AAPL', 'Reliance Industries', 'RELIANCE.NS'")
    print("=" * 60)
    
    try:
        # Initialize the bot
        bot = StockSentimentBot()
        
        # Get company name or stock symbol from user
        user_input = input("Enter company name or stock symbol: ").strip()
        
        if not user_input:
            print("❌ Please provide a valid company name or stock symbol.")
            return
        
        # Show suggestions if input seems partial and might need clarification
        if len(user_input) >= 3 and not re.match(r'^[A-Z]{2,6}(\.[A-Z]{1,3})?$', user_input.upper()):
            suggestions = bot.get_company_suggestions(user_input)
            if suggestions and len(suggestions) > 1:
                print(f"\n💡 Found {len(suggestions)} potential matches:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
                
                choice = input("\nEnter the number of your choice (or press Enter to continue with original input): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                    # Extract company name from suggestion
                    selected = suggestions[int(choice) - 1]
                    user_input = selected.split(' (')[0]  # Remove ticker from display
                    print(f"✅ Selected: {selected}")
        
        # Analyze sentiment
        result = bot.analyze_stock_sentiment(user_input)
        
        if result:
            print(f"\n✅ Analysis complete for {result['company_input']} ({result['stock_symbol']})")
            print("⚠️  Disclaimer: This is for educational purposes only. Not financial advice.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
