import re

def regex_redux(input_str, rules):
    """
    input_str: initial string
    rules: list of tuples (pattern, replacement)
    """
    # Pre-compile all regexes
    compiled = [(re.compile(p), r) for p, r in rules]

    while True:
        original = input_str
        # Apply each rule in sequence
        for pattern, replacement in compiled:
            input_str = pattern.sub(replacement, input_str)
        # Stop if no changes
        if input_str == original:
            break

    return input_str

# Example usage
rules = [
    (r'AB', 'C'),
    (r'CB', 'A'),
    (r'AC', 'B'),
    (r'BA', 'C'),
    (r'BC', 'A'),
    (r'CA', 'B'),
]
result = regex_redux("ABCBAC", rules)
print(result)
