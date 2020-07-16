# def drink(empty, counter):
#     full = empty // 3
#     remain = empty % 3
#     total = full + remain
#     counter += full
#     if total == 2:
#         return counter + 1
#     elif total < 2:
#         return counter
#     else:
#         return drink(total, counter)
#
#
# l = []
# while True:
#     number = int(input())
#     if number != 0:
#         l.append(drink(number, 0))
#     else:
#         break
# for i in l:
#     print(i)
#
while True:
    try:
        line = int(input().split())
        l = []
        for i in range(line):
            content = int(input().split())
            l.append(content)
        print(sorted(list(set(l))))
    except:
        break
a = int("A")
# import sys
# num = sys.stdin.readline()
# print(num)
# num = input()
# print(num)
