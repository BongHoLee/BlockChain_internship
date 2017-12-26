import threading

sleep = True
def thread_func() :
    while not sleep :
        print('hi')


if __name__=='__main__' :
    ab = threading.Thread(target=thread_func)
    ab.start()
    
