import base64
import sys

img_path = sys.argv[1]

with open(img_path, 'rb') as img_fp:
    data = base64.b64encode(img_fp.read()).decode()
    print(f'<img src="data:image/png;base64,{data}">')

