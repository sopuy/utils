#!/usr/bin/env bash
# Usage       : sh condition.sh [ parameter ]
###############################################################################
:<<-'EOF'
__author__ = "Daning"

Description:

if condition:
单个中括号是 POSIX 标准的一部分，因此在所有符合 POSIX 标准的 Shell 中都可以使用。
支持基本的字符串比较、数字比较和文件测试。
在使用 < 和 > 进行字符串比较时，需要使用转义字符 \。
逻辑运算： 使用 -a 和 -o


双中括号是 Bash 和其他一些 Shell, 如 zsh 和 ksh 的扩展, 不是 POSIX 标准的一部分。
支持更多的操作符，如逻辑运算符 && 和 ||，正则表达式匹配 =~，以及不需要转义的字符串比较。
在处理复杂条件时，双中括号更安全，因为它们不会进行单词拆分和路径名扩展。
逻辑运算： 使用 && 和 ||

case statement:

EOF
ls -i:18000 | grep LISTEN | awk '{print $2}'
if [ $? -ne 0 ]; then echo "failed: ${command} execute failed."; else echo "succeed: ${command} execute succeed";

# 字符串比较
# single brackets  使用双等号 == 进行字符串比较也是可以的，但在 POSIX 标准中，单等号 = 更常用和推荐。
if [ "$command" = "start" ]; then
    echo "start process: [ ${command} ]"
fi
echo "--------------------------------------------------------------------------"
# double brackets  在双中括号中，= 和 == 都可以用于字符串比较。在双中括号中，双等号 == 是推荐的字符串比较方式。
if [[ "$command" == "start" ]]; then
    echo "start process: [ ${command} ]"
fi
echo "--------------------------------------------------------------------------"

# 单中括号需要转义 < 和 >
if [ "$a" \< "$b" ]; then
    echo "$a is less than $b"
fi

echo "--------------------------------------------------------------------------"
if [[ "$a" < "$b" ]]; then
    echo "$a is less than $b"
fi


# 逻辑运算
if [ "$a" -eq 1 -a "$b" -eq 2 ]; then
    echo "Both conditions are true"
fi
echo "--------------------------------------------------------------------------"
if [[ "$a" -eq 1 && "$b" -eq 2 ]]; then
    echo "Both conditions are true"
fi
echo "--------------------------------------------------------------------------"

# 正则表达式匹配（仅双中括号支持）
if [[ "$a" =~ ^[0-9]+$ ]]; then
    echo "The string contains only digits"
fi

echo "--------------------------------------------------------------------------"
echo "for test: 使用正则表达式匹配字符串"
input_string="Hello, World!"
# 正则表达式
pattern="^Hello"
# 使用if语句进行正则匹配
if [[ "$input_string" =~ $pattern ]]; then
    echo "字符串匹配成功"
else
    echo "字符串不匹配"
fi
echo "--------------------------------------------------------------------------"

#  文件/目录测试; -e：检查文件或目录是否存在，不区分类型。
if [ -e "${prog_path}" ]; then
    echo "The file or directory exists"
elif [ -f "${prog_path}" ]; then
    echo "The file exists"
elif [ -d "${prog_path}" ]; then
    echo "The directory exists"
else
    echo "The file or directory does not exist"
fi

# 检查变量是否为空
variable="hello"
if [[ -n "$variable" ]]; then
    echo "变量非空"
else
    echo "变量为空"
fi

echo "--------------------------------------------------------------------------"
# shift 是一个用于参数处理的命令。它会移除位置参数列表中的第一个参数，并使后续参数向前移动一个位置
echo "第一个参数: $1"
shift
echo "现在第一个参数: $1"

echo "--------------------------------------------------------------------------"
# case statement
case "$1" in
    start)
        echo "Starting the service..."
        ;;
    stop)
        echo "Stopping the service..."
        ;;
    restart)
        echo "Restarting the service..."
        ;;
    *)
        echo "Usage:  {start|stop|restart}"
        exit 1
        ;;
esac