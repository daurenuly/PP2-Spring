class Father:
    def __init__(self):
        self.father_name = "John"
        print("Father constructor")
    
    def father_method(self):
        return "Method from Father"
    
    def common_method(self):
        return "Common from Father"

class Mother:
    def __init__(self):
        self.mother_name = "Mary"
        print("Mother constructor")
    
    def mother_method(self):
        return "Method from Mother"
    
    def common_method(self):
        return "Common from Mother"

class Child(Father, Mother):
    def __init__(self):
        Father.__init__(self)
        Mother.__init__(self)
        self.child_name = "Tom"
        print("Child constructor")
    
    def show_names(self):
        return f"Father: {self.father_name}, Mother: {self.mother_name}, Child: {self.child_name}"

# Create instance
child = Child()
print(child.show_names())
print(child.father_method())  
print(child.mother_method())  
print(child.common_method())