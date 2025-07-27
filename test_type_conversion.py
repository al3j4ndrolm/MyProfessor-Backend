#!/usr/bin/env python3

from helpers.data import data_keys, data_creators

# Test data similar to what we saw in the logs
test_rmp_data = {
    'rating': '3.4',
    'reviewCount': '9',
    'difficulty': '2.9',
    'recommend': '40',
    'score': '0.842',
    'link': '/professor/1453512'
}

print("Original test data:")
print(test_rmp_data)
print()

# Test the type conversion
converted_data = data_creators.typed_rmp_data(test_rmp_data)

print("Converted data:")
print(converted_data)
print()

# Check types
print("Data types:")
for key, value in converted_data.items():
    print(f"{key}: {value} (type: {type(value).__name__})") 