from task import Scheduler,SchedulResult


class RoundRobin(Scheduler):
    def __init__(self):
        super(RoundRobin, self).__init__()

    def work(self,time):
        assert time == 1
        remainedTime = time
        while remainedTime>0:
            for task in self.tasks:
                if remainedTime<=0:
                    break
                if not task.isCompleted():
                    duration = 1
                    task.work(1)
                    if len(self.results) == 0:
                        self.results.append(SchedulResult(task.pid, task.arrivalTime, duration))
                    else:
                        self.results.append(SchedulResult(task.pid, self.results[-1].endTime, duration))
            break