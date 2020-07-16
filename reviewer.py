import sqlite3
import json

conn = sqlite3.connect("world_bank.db", check_same_thread=False)
c = conn.cursor()

print("indicator")
content = c.execute("SELECT * FROM INDICATOR")

for i in content:
    print(i)




print("\n\nentity")
content2 = c.execute("SELECT * FROM ENTITY")
for i in content2:
    print(i)

print("\n\nrecorder")
content3 = c.execute("SELECT * FROM ID_RECORDER")
for i in content3:
    print(i)

economic_entity_cursor = c.execute("SELECT * FROM ENTITY WHERE ID == ? AND YEAR == ? AND COUNTRY == ?",
                                   (3, 2014, "Peru"))
for i in economic_entity_cursor:
    print(i)
if len(list(economic_entity_cursor)) == 0:
    print(11111111111)
print(economic_entity_cursor.fetchone())
print(list(economic_entity_cursor))
print(len(list(economic_entity_cursor)))


indicator_cursor = c.execute("SELECT * FROM INDICATOR WHERE ID == {}".format(3))
conn.commit()

print(len(list(indicator_cursor)))

for i in indicator_cursor:
    print(i, "123")
# order_by = "+id, -creation_time"
# order_by = order_by.replace(" ", "")
# order_list = order_by.split(",")
# print(order_by)
# print(order_list)
# for i in order_list:
#     if i[1:] == "id":
#         print(1)
# print(order_list[0][0], order_list[0][1:])
# x = 1
# s=[
# {"no":28,"score":90},
# {"no":25,"score":90},
# {"no":1,"score":100},
# {"no":2,"score":20},
# ]
#
# print(conn.total_changes, "asdfsadf")
# s.sort(key=lambda item:item["no"], reverse=True)
# # s = json.loads(str(s))
# print(s)
l2 = [
    {
        "uri": "/collection/4",
        "id": 4,
        "creation_time": "2020-04-03 00:20:38",
        "indicator": "2.0.cov.Math.pl_3.prv"
    },
    {
        "uri": "/collection/3",
        "id": 2,
        "creation_time": "2020-04-03 00:20:02",
        "indicator": "1.0.HCount.Vul4to10"
    },
    {
        "uri": "/collection/3",
        "id": 3,
        "creation_time": "2020-04-03 00:20:02",
        "indicator": "1.0.HCount.Vul4to10"
    }
]
l2.sort(key=lambda i: i["indicator"], reverse=True)
print(l2)
l1 = [1, 2, 3, 4]
l1.reverse()
for i in l1:
    print(i)

