import sys
import re

def main():
    data = sys.stdin.read()
    
    parts = data.split('>', 2)
    if len(parts) < 3:
        clean_string = data
    else:
        record = parts[2]
        idx = record.find('\n')
        if idx == -1:
            sequence = ''
        else:
            sequence = record[idx+1:]
        clean_string = sequence.replace('\n', '').replace('\r', '').upper()
    
    original_length = len(data)
    clean_length = len(clean_string)
    
    patterns = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    current = clean_string
    for pattern, replacement in patterns:
        current = re.sub(pattern, replacement, current)
    
    final_length = len(current)
    
    print(original_length)
    print(clean_length)
    print(final_length)

if __name__ == '__main__':
    main()