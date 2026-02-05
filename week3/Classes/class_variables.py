class Employee:
    company = "TechCorp"  
    def __init__(self, name):
        self.name = name   
    @classmethod
    def change_company(cls, new_name):
        cls.company = new_name
emp1 = Employee("Alice")
emp2 = Employee("Bob")
print(emp1.company)  
Employee.change_company("NewCorp")
print(emp2.company)  