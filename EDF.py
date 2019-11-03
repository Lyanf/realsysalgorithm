from task import Scheduler, SchedulResult


class EDF(Scheduler):
    def __init__(self, preemption):
        super(EDF, self).__init__()
        self.preemption = preemption

    def work(self, time):
        remainedTime = time
        if self.preemption:
            self.tasks.sort(key=lambda x: x.deadline)
            for task in self.tasks:
                if remainedTime == 0:
                    break
                if task.isCompleted():
                    continue
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


        else:
            for task in self.tasks:
                if remainedTime == 0:
                    break
                if task.haveDone > 0 and task.isCompleted() is False:
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
                    break

            self.tasks.sort(key=lambda x: x.deadline)
            for task in self.tasks:
                if remainedTime == 0:
                    break
                if task.isCompleted():
                    continue
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
