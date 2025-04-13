import pandas as pd
import os

def calculate_weighted_score():
    # Read the input files
    fundamentals_df = pd.read_csv('fundamentals_scored.csv')
    fear_greed_df = pd.read_csv('fear_greed_log.csv')
    
    # Get the most recent Fear & Greed score
    latest_fear_greed = fear_greed_df['fear_greed_score'].iloc[-1]
    
    # Calculate the multiplier
    if latest_fear_greed > 50:
        multiplier = 1 + ((latest_fear_greed - 50) * 0.02)
    elif latest_fear_greed < 50:
        multiplier = 1 + ((latest_fear_greed - 50) * 0.02)
    else:
        multiplier = 1.0
    
    # Calculate weighted scores
    fundamentals_df['weighted_score'] = fundamentals_df['score'] * multiplier
    
    # Round the weighted scores to 2 decimal places
    fundamentals_df['weighted_score'] = fundamentals_df['weighted_score'].round(2)
    
    # Save the results
    output_file = 'weighted_scores.csv'
    fundamentals_df.to_csv(output_file, index=False)
    
    print(f"Latest Fear & Greed Index: {latest_fear_greed}")
    print(f"Multiplier applied: {multiplier:.2f}")
    print(f"Weighted scores saved to {output_file}")
    
    # Print the results
    print("\nWeighted Scores:")
    print(fundamentals_df[['ticker', 'score', 'weighted_score']].to_string(index=False))

if __name__ == "__main__":
    # Change to the outputs directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    calculate_weighted_score() 