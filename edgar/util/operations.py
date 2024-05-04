def contains_no_numbers(str):
    for char in str:
        if char.isdigit():
            return False
    return True