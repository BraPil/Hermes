import pandas as pd
import os

# Get the absolute path of the outputs directory
outputs_dir = os.path.dirname(os.path.abspath(__file__))

# Read the input files with full paths
fundamentals_df = pd.read_csv(os.path.join(outputs_dir, 'fundamentals_scored.csv'))
fear_greed_df = pd.read_csv(os.path.join(outputs_dir, 'fear_greed_log.csv'))

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

# Save only the ticker and weighted score to a new CSV
output_df = fundamentals_df[['ticker', 'weighted_score']]
output_df.to_csv(os.path.join(outputs_dir, 'weighted_score.csv'), index=False)

print(f"Latest Fear & Greed Index: {latest_fear_greed}")
print(f"Multiplier applied: {multiplier:.2f}")
print(f"Weighted scores saved to weighted_score.csv")

# Print the results
print("\nWeighted Scores:")
print(output_df.to_string(index=False)) 