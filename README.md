# text2bin

text2bin is a tool for encrypt or decrypt a regular file. 

The encrypted file can not be read directly， but can be easily read by text2bin api.

### install

```
pip install git+https://github.com/yodeng/text2bin.git
```

+ python >3.8 required

### usage

##### encrypt file:

```shell
$ cat a.txt
你好！
hello!

$ text2bin -i a.txt -o a.tb
```



##### decrypt  file

```shell
$ text2bin -i a.tb -o a.txt -d
$ cat a.txt
你好！
hello!
```



##### decrypt file in python code:

```python
import sys
from text2bin import Bopen
with Bopen("example/a.tb", text=False) as fi:
    for line in fi:
        sys.stdout.buffer.write(line)

# 你好！
# hello!
```
