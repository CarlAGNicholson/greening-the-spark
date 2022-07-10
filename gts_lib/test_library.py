class model:
    class_name = "model"

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.describe("ill")
        

    def describe(self, status):
        print(self.name, self.value, status)        


    def another(self):
        pass
        

John = model("John", 24)
James = model("James", 25)
John.describe("healthy")







'''class clown:

    class_name = "clown"
    
    def __init__(self, name, age):
        self.name = name
        self.age = age       

    def runClown(self):
        if self.name == "John":
            self.age += 1
        else:
            self.age -= 1
            
        return self.age


        appellation = "Hi"
        if length == "short":
            print(appellation, self.class_name, self.name, self.age)
        else:
            print(f'{appellation}, role {self.class_name}, name {self.name}, age {self.age}')
     

def increment():
    globals()["lib_variable"] += 1
    #print("increment lib var = ", globals()["lib_variable"])
        

lib_variable = 0

#print(globals())

           
John = clown("John", 25)
James = clown("James", 35)

#John.description("long")
#John.description("short")

'''


