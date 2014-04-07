import threading
import time

def doafter():
    threads = threading.enumerate()
    main_thread = None
    for thread in threads:
        if type(thread) is threading._MainThread:
            main_thread = thread
    main_thread.join()
    print 'did after'

th = threading.Thread(target=doafter)
th.start()

print 'test1'
time.sleep(2)
print 'test2'
time.sleep(1)