import re

def clean_price(price_str):
    # Ensure the input is a string
    if isinstance(price_str, (int, float)):  # If the input is numeric, convert it to a string
        price_str = str(price_str)
    
    # Regex to capture only numbers with commas (e.g., "25,582" or "154") before the suffix "ポイント"
    match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?=ポイント)', price_str)
    
    if match:
        cleaned_price = match.group(0)  # Get the matched part, which is the number
        cleaned_price = cleaned_price.replace(',', '')  # Remove commas to get a pure numeric string
        
        try:
            return float(cleaned_price)  # Convert to float
        except ValueError:
            return 0.0  # Return 0 if conversion fails
    else:
        return 0.0  # Return 0 if no match is found

# Example usage
price_str_1 = "25,582ポイント(1倍)"
price_str_2 = "154ポイント(1倍)"
price_str_3 = "2,883ポイント(1倍)"

result_1 = clean_price(price_str_1)
result_2 = clean_price(price_str_2)
result_3 = clean_price(price_str_3)

print(result_1)  # Output will be 25582.0
print(result_2)  # Output will be 154.0
print(result_3)  # Output will be 2883.0
