#!/usr/bin/env python
# coding=utf-8

#code 1:     & print
print 'code 1:   & print \n'

a = 10
b = 'strABC'
print (a + 100) / 10
print a + 10
print a, b, type(a), type(b)

print '--------------------------------------------'
print '\n\n'

#code 2: raw_input
print 'code 2:  raw_input \n'

name = raw_input('please input what you want to input:');
print name

c = 22
if c > 10:
    print c - 10
if c > 20:
    print c
if c > 1:
    print -c

print '--------------------------------------------'
print '\n\n'


#code 3:  
print 'code 3:   \n'

ord('A')
chr(97)

print ""
print ''
print u''
print 'hello %s %d, %c'%('rh_Jameson',100,'r')

print '--------------------------------------------'
print '\n\n'

#code 4:  list tuple
print 'code 4:   \n'

list = [123,'strlll',(222,333)]
"""
print list
print list[0]
print list[1]
"""
for e in list:
    print e

print '\n'

tuple = (000,'sdiofjois',11122)

"""
print tuple
print tuple[0]
print tuple[1]
"""
for t in tuple:
    print t

sum = 0
for r in range(101):
    sum = sum + r
print sum



print '--------------------------------------------'
print '\n\n'


#code 5:  
print 'code 5:   \n'

def PrintMax(x, y):
    if x > y:
        return x
    else:
        return y

def PrintMin(x, y):
    if x < y:
        return x
    else:
        return y


min = PrintMin(11,22)
max = PrintMax(99,22)

print min, max


print '--------------------------------------------'
print '\n\n'


