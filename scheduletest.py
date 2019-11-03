from FIFO import FIFO
from task import TurnLeft

fifo = FIFO()
task = TurnLeft(10,10,40)
task2 = TurnLeft(20,30,100)
print(task2.isCompleted())
time = 0
fifo.addTask(task)
fifo.addTask(task2)
fifo.work(10)
fifo.work(1)
fifo.work(100)
for i in fifo.results:
    print(i)