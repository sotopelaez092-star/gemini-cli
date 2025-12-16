# Case 02: NameError - using undefined variable from another module
from data_processor import process_records

def main():
    records = [{"id": 1, "value": 100}, {"id": 2, "value": 200}]
    # Error: using 'DEFUALT_MULTIPLIER' which is typo of 'DEFAULT_MULTIPLIER'
    result = process_records(records, multiplier=DEFUALT_MULTIPLIER)
    print(result)

if __name__ == "__main__":
    main()
