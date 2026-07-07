import pickle
import collections

class User:
    def __init__(self, username):
        self.user = username
        self.email = f"{username}@gmail.com"
        self.__password = "s3cr3tP@55word!"


def serialize_safely(object):
    object_name = type(object).__name__
    prefix = f"_{object_name}__"
    resultdict = {}
    for attr, value in object.__dict__.items():
        # exclude private attributes
        if not attr.startswith(prefix):
            resultdict[attr] = value
    
    return resultdict

myuser = User("bob")
resultdict = serialize_safely(myuser)
print(resultdict)

# serialize the data with file output
with open("result.pkl", "wb") as file:
    pickle.dump(resultdict, file)

