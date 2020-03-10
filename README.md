# sqlii
这是一个学习sqlmap注入检测逻辑时的产物!


## Overview
+ sqlii对四类注入(time, bool, union, error)是否存在的测试的逻辑 与sqlmap是基本一致的。

+ payload模板在sqlii中的格式 与sqlmap的基本一致，sqlmap的payload和boundary作修改后是通用的。(\<payload>等标签内容的渲染方式不同，一些关键字的写法不同)

+ sqlii将逻辑中需要判断页面(常是用于payload是否有效的判断)的部分单独提出，以方便根据实际测试环境定制：

    + 查询正常有返回结果
    + 查询正常无返回结果
    + 查询执行异常


## Usage
    python3 sqlii.py -u <URL> --method=<METHOD> -p <PARAM> --technique=<TECH>

#### e.g.  
`python3 sqlii.py -u "http://xxx?name=1&nn=3&id=2" --method="GET" -p "id" --technique="T"`
![image](https://github.com/Zzzaw/sqlii/blob/master/images/test.png)

## Options
    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -u URL, --url=URL     Target URL (e.g.
                            "http://www.site.com/search.php?id=1")
      --method=METHOD       Method
      --data=DATA           POST data
      -p TESTPARAM          One parameter for tests
      --technique=TECHNIQUE
                            SQL injection techniques to use (T/E/U/B)


## 四类注入的检测流程
#### check_boolean_blind()
![image](https://github.com/Zzzaw/sqlii/blob/master/images/boolean.jpg)

#### check_union_based()
![image](https://github.com/Zzzaw/sqlii/blob/master/images/union.jpg)

#### check_error_based()
![image](https://github.com/Zzzaw/sqlii/blob/master/images/error.jpg)

#### check_time_blind()
![image](https://github.com/Zzzaw/sqlii/blob/master/images/time.jpg)
