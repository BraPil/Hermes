from tabulate import tabulate

def generate_report(df):
    """
    Generate a clean CLI report showing stock scores.

    Args:
        df (pd.DataFrame): DataFrame containing stock data + scores.
    """

    # Sort by score descending (highest first)
    df = df.sort_values(by='score', ascending=False)

    # Define the columns to show in the report
    table = df[['ticker', 'longName', 'sector', 'score']]

    # Print the table using tabulate
    print(tabulate(table, headers='keys', tablefmt='fancy_grid'))