
import os

file_path = r'c:\Users\45128\Desktop\新建文件夹\flow-state\app\web\templates\index.html'

def fix_encoding():
    content = None
    
    # 尝试用 GBK 读取 (假设它被错误地保存为 GBK)
    try:
        with open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
        print("Successfully read as GBK")
    except Exception as e:
        print(f"Failed to read as GBK: {e}")
        
    # 如果 GBK 读取失败，尝试用 UTF-8 读取 (看看是不是本来就是坏的)
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("Successfully read as UTF-8 (Wait, why did it fail in Flask?)")
        except Exception as e:
            print(f"Failed to read as UTF-8: {e}")
            
    # 如果读取到了内容，将其强制保存为 UTF-8
    if content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully rewrote as UTF-8")
        except Exception as e:
            print(f"Failed to write as UTF-8: {e}")

if __name__ == '__main__':
    fix_encoding()
