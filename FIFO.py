from task import Scheduler, SchedulResult


class FIFO(Scheduler):
    def __init__(self):
        super(FIFO, self).__init__()

    def work(self, time):
        remainedTime = time
        for task in self.tasks:
            if remainedTime == 0:
                break

            if not task.isCompleted():
                duration = 0
                if remainedTime > task.needTime:
                    duration = task.needTime
                else:
                    duration = remainedTime
                task.work(duration)
                remainedTime = remainedTime - duration

                if len(self.results) == 0:
                    self.results.append(SchedulResult(task.pid,task.arrivalTime, duration))
                else:
                    self.results.append(SchedulResult(task.pid,self.results[-1].endTime, duration))
