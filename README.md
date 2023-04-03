# text2bin

text2bin is a tool to encrypt `text` file. The encrypted file can not be read directly but can be easily read by text2bin api. So, this can be simplely used for `text` file protection when you don't want the contents of the text to be seen by others.

*Warning: This is  only work for TEXT files*

### install

```
pip install git+https://github.com/yodeng/text2bin.git
```

+ python >3.8 required

### usage

##### encrypt text file:

```shell
$ cat a.txt
你好！
hello!

$ text2bin -i a.txt -o a.tb
```

##### decrypt file by python code:

```python
from text2bin import Bopen
with Bopen("example/a.tb") as fi:
    for line in fi:
        print(line.strip())

## this will output:
# 你好！
# hello!
```
