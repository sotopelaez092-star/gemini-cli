# Case 02: Similar symbol names confusion
# Difficulty: Hard
# Multiple similar function names exist, easy to confuse

from data_handlers import DataProcessor

def main():
    processor = DataProcessor()
    raw_data = {"date": "2024-01-15", "values": [10, 20, 30]}

    # Error: Called 'process_date' but should be 'process_data'
    # There's also a 'parse_date' function which adds to confusion
    result = processor.process_date(raw_data)
    print(result)

if __name__ == "__main__":
    main()
