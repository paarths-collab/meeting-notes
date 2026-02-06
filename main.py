import threading
from audio.recorder import start_recording
from audio.watcher import watch

t1 = threading.Thread(target=start_recording)
t2 = threading.Thread(target=watch)

t1.start()
t2.start()

t1.join()
t2.join()
