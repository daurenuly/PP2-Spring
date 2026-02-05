class Animal:
    def speak(self):
        return "Animal makes a sound"
    
    def move(self):
        return "Animal moves"

class Dog(Animal):
    def speak(self):
        return "Dog barks: Woof! Woof!"
    
    
animal = Animal()
dog = Dog()

print(animal.speak())  
print(dog.speak())     
print(dog.move())      