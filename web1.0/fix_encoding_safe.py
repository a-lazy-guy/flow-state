
import os

file_path = r'c:\Users\45128\Desktop\新建文件夹\flow-state\app\web\templates\index.html'

def fix_encoding():
    content = None
    
    # Try reading as GBK (assuming it was wrongly saved as GBK)
    try:
        with open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
        print("Successfully read as GBK")
    except Exception as e:
        print(f"Failed to read as GBK: {e}")
        
    # If GBK fails, try UTF-8 with error ignore to see what happens
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print("Read as UTF-8 (with errors ignored)")
        except Exception as e:
            print(f"Failed to read as UTF-8: {e}")
            
    # Write back as strict UTF-8
    if content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully rewrote as UTF-8")
        except Exception as e:
            print(f"Failed to write as UTF-8: {e}")

if __name__ == '__main__':
    fix_encoding()
