# _*_ coding:utf-8 _*_
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import boto.ec2
import scanf
import json
import re
import time


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def getIP():
    return [l for l in open('hosts', 'r').read().split('\n') if l]


def sort_key(s):
    # 排序关键字匹配
    # 匹配开头数字序号
    if s:
        try:
            c = re.findall('^\d+', s)[0]
        except:
            c = -1
        return int(c)


def strsort(alist):
    alist.sort(key=sort_key)
    return alist



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    n = 16
    date = ''
    fileter = True
    throughputArr = dict()
    for ID in range(0, n):
        if date == '':
            filename = "var/log/" + str(ID) + "/" + time.strftime("%Y%m%d", time.localtime()) + "_Eva.log"
        else:
            filename = "var/log/" + str(ID) + "/" + date + "_Eva.log"
        with open(filename, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    break
                item = line.strip().split(' ')
                if int(item[3]) not in throughputArr:
                    throughputArr[int(item[3])] = list()
                historyThroughput = throughputArr[int(item[3])]
                if int(item[5]) > 0:
                    historyThroughput.append(int(item[5]))
                    throughputArr[int(item[3])] = historyThroughput
            file.close()

    throughputDict = dict()
    with open("data.txt", 'w') as dfile:
        for key in sorted(throughputArr.keys()):
            Sum = 0
            numLen = len(throughputArr[key])
            if key == 15000:
                throughputArr[key].sort()
                print(throughputArr[key])
                print(len(throughputArr[key]))
            if fileter:
                if numLen > n:
                    throughputArr[key].sort()
                    throughputArr[key] = throughputArr[key][0: int(numLen / 2)]
                    numLen = len(throughputArr[key])
            if key == 15000:
                print(throughputArr[key])
                print(len(throughputArr[key]))
            for i in throughputArr[key]:
                Sum = Sum + i
            avg = int(Sum / numLen)
            p = "(" + str(key) + "," + str(float(avg) / 1000) + ") "
            dfile.write(p)
            throughputDict[key] = avg
    dfile.close()
