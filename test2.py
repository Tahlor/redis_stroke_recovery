import redis
from redisworks import Root

my_redis = Root() # redis.Redis('localhost')

data = {"user":"Taylor", }

def check_for_user(user="Taylor"):
    f = my_redis.user
    if f:
        print("user exists", f)
        return True
    else:
        print(f"user {user} does not exist")
        return False

def add_user(data):
    if not check_for_user(data["user"]):
        my_redis. = data

#conn.hmset("pythonDict", {"Location": "Ahmedabad", "Company": ["A/C Prism", "ECW", "Musikaar"]})

my_redis.KL=({'tokens':[1,2,3]})

data = {"user" : "KL", "tokens" : "first_token", "password":""}
add_user(data)





# conn.hgetall("pythonDict")
# x = conn.hget("pythonDict", "user")
# print(x)
# conn.set('test',"value")