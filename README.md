# text2bin

text2bin is a simple tool to convert text file into binary file. The binary file can not be read directly and can be easily read by text2bin api. So, this can be simplely used for text file protection when you don't want the contents of the text to be seen by others.

*Warning: The filesize of output binary file will be 2~3 fold then the original text file, so it's more suitable for small files.*

### install

```
pip install git+https://github.com/yodeng/text2bin.git
```

+ python >3.8 required

### usage

##### convert text file to binary:

```shell
$ cat a.txt
你好！
hello!

$ text2bin -i a.txt -o a.tb
```

##### read binary file contents by python code:

```python
import text2bin 
with text2bin.Bopen("example/a.tb") as fi:
    for line in fi:
        print(line.decode().strip())

## this will output:
# 你好！
# hello!
```

*text2bin also can be used for binary binary file, but this is not for recommend.*
