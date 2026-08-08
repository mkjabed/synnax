x = 10
y = 0
pi = 3.14
flag = true
L1:
t1 = x > 0
ifFalse t1 goto L2
t2 = y + x
y = t2
t3 = x - 1
x = t3
goto L1
L2:
t4 = flag == true
ifFalse t4 goto L3
t5 = y % 3
inner = t5
print inner
goto L4
L3:
print x
L4:
t6 = !flag
ifFalse t6 goto L5
print pi
goto L6
L5:
t7 = y > 0
t8 = x == 0
t9 = t7 && t8
ifFalse t9 goto L7
print y
L7:
L6:
