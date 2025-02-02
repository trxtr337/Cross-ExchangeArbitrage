for ticker in info_all_futures_tickers:
                    symbol = ticker['symbol']
                    lastPrice = float(ticker['lastPrice'])
                    fundingRate = 100 * float(ticker['fundingRate'])
                    symbols_dict[symbol] = {
                        'lastPrice': lastPrice,
                        'fundingRate': fundingRate,
                    }

                tasks = [
                    fetch_funding_rate(session, f"{base_url}/contract/funding_rate/{symbol}", semaphore, symbols_dict,
                                       symbol) for symbol in symbols_dict]

############################################

async def first_dict_async():
    symbols_list = await fetch_symbols_list()
    main_dict = {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_funding_rate(session, symbol["symbol"]) for symbol in symbols_list]
        results = await asyncio.gather(tasks)

        for i, symbol in enumerate(symbols_list):
            symbol_name = symbol["symbol"]
            symbol_price = symbol["indexPrice"]
            funding_rate, next_funding_time = results[i] if results[i] else (None, None)
            #print(symbol)

            # Записываем информацию в словарь
            if funding_rate is not None and next_funding_time is not None:
                fr = 100 funding_rate
                main_dict[symbol_name] = [
                     symbol_price,
                    fr,
                    next_funding_time,
                ]