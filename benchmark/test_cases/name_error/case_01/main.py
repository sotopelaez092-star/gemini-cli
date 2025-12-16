# Case 01: Cross-file NameError - typo in function name
from utils import calculat_total  # typo: should be calculate_total

def process_data():
    data = [1, 2, 3, 4, 5]
    result = calculat_total(data)
    return result

if __name__ == "__main__":
    print(process_data())
