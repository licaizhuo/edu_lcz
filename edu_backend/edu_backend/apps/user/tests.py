from django.test import TestCase

# Create your tests here.
from redis import Redis

red = Redis(host='192.168.217.129', port=7000)

# red.set("age", 18)
# print(red.get("age"))
# red.delete('age')
red.decr('age')
print(red.get("age"))
if red.get("age"):
    print(123)
else:
    print(21)
