import chardet

if __name__ == '__main__':
    file = "utility.py"
    with open(file, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']
        data_str = data.decode(encoding)
        tp = 'LF'
        if '\r\n' in data_str:
            tp = 'CRLF'
            data_str = data_str.replace('\r\n', '\n')
        if encoding not in ['utf-8', 'ascii'] or tp == 'CRLF':
            with open(file, 'w', newline='\n', encoding='utf-8') as f:
                f.write(data_str)
