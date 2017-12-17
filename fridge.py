class Fridge:
    isOpened = False
    foods = []

    def open(self):
        self.isOpened = True
        print('Opend fridge')

    def put(self, thing):
        if self.isOpened:
            self.foods.append(thing)
            print ('input food')
        else:
            print ('open the firdge')

    def close(self):
        self.isOpened = False
        print ('closed fridge')

class Food:
    pass
