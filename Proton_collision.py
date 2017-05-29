#coding=utf-8
import threading, time, httplib
import pp
import sys

HOST = "10.55.91.107";  # 主机地址 例如192.168.1.101
PORT = 80  # 端口
URI = "/?335" # 相对地址,加参数防止缓存，否则可能会返回304
TOTAL = 0  # 总数
SUCC = 0  # 响应成功数
FAIL = 0  # 响应失败数
EXCEPT = 0  # 响应异常数
MAXTIME = 0  # 最大响应时间
MINTIME = 30  # 最小响应时间，初始值为100秒
GT3 = 0  # 统计3秒内响应的
LT3 = 0  # 统计大于3秒响应的

THREAD_NUMBER = 300 # 并发的线程数

class RequestThread(threading.Thread):
    def __init__(self, thread_name):
        threading.Thread.__init__(self)
        self.test_count = 0


    def maxtime(self, ts):
        global MAXTIME
        print ts
        if ts > MAXTIME:
            MAXTIME = ts

    def mintime(self, ts):
        global MINTIME
        if ts < MINTIME:
            MINTIME = ts

    def test_performace(self):
        global TOTAL
        global SUCC
        global FAIL
        global EXCEPT
        global GT3
        global LT3
        try:
            st = time.time()
            conn = httplib.HTTPConnection(HOST, PORT, False)
            conn.request('GET', URI)
            res = conn.getresponse()
            # print 'version:', res.version
            # print 'reason:', res.reason
            # print 'status:', res.status
            # print 'msg:', res.msg
            # print 'headers:', res.getheaders()
            if res.status == 200:
                TOTAL += 1
                SUCC += 1
            else:
                TOTAL += 1
                FAIL += 1
            time_span = time.time() - st
            print '%s:%f\n' % (self.name, time_span)
            self.maxtime(time_span)
            self.mintime(time_span)
            if time_span > 3:
                GT3 += 1
            else:
                LT3 += 1
        except Exception, e:
            print e
            TOTAL += 1
            EXCEPT += 1
        conn.close()
    def run(self):
        self.test_performace()

def collision(thread_number):
    for i in range(0, thread_number,1):
        t = RequestThread("Thread" + str(time.strftime('%H%M%S')))
        t.start()

print "=======================================INITIALIZATION========================================"
print "Trying to use all cpu"
ppservers = ()
if len(sys.argv) > 1:
    ncpus = int(sys.argv[1])
    # Creates jobserver with ncpus workers
    job_server = pp.Server(ncpus, ppservers=ppservers)
else:
    # Creates jobserver with automatically detected number of workers
    job_server = pp.Server(ppservers=ppservers)
print "Starting pp with", job_server.get_ncpus(), "workers"
inputs = ()
for i in range(int(job_server.get_ncpus())):
    global THREAD_NUMBER
    # inputs.append(THREAD_NUMBER/int(job_server.get_ncpus()))
    inputs = inputs + THREAD_NUMBER/int(job_server.get_ncpus())



print "===========================================START============================================="
jobs = [(input,job_server.submit(collision,(inputs) ))for input in inputs]
for input,job in jobs:
    print "Start job! Thread Number:" ,input ,"And",job()









print '=============================================END============================================='
print "total:%d,succ:%d,fail:%d,except:%d" % (TOTAL, SUCC, FAIL, EXCEPT)
print 'response maxtime:', MAXTIME
print 'response mintime', MINTIME
print 'great than 3 seconds:%d,percent:%0.2f' % (GT3, float(GT3) / TOTAL)
print 'less than 3 seconds:%d,percent:%0.2f' % (LT3, float(LT3) / TOTAL)