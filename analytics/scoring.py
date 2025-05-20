def calculate_score(stock):
    score = 0
    print(f"Scoring {stock['ticker']}")

    if stock['trailingPE'] and stock['trailingPE'] < 35:
        print("Adding 20 for trailingPE")
        score += 20

    # if stock['pegRatio'] and stock['pegRatio'] < 1.5:
    #     print("Adding 30 for pegRatio")
    #     score += 30

    if stock['priceToBook'] and stock['priceToBook'] < 10:
        print("Adding 15 for priceToBook")
        score += 15

    if stock['debtToEquity'] and stock['debtToEquity'] < 15:
        print("Adding 20 for debtToEquity")
        score += 20

    if stock['returnOnEquity'] and stock['returnOnEquity'] > 1:
        print("Adding 15 for returnOnEquity")
        score += 15

    return score
