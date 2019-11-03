from task import Scheduler, SchedulResult


class EDF(Scheduler):
    def __init__(self, preemption: bool):
        super(EDF, self).__init__()
        self.preemption = preemption

    def work(self, time):
        remainedTime = time
        if self.preemption:
            self.tasks.sort(key=lambda x: x.deadline)
            for task in self.tasks:
                if remainedTime == 0:
                    break
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
            # 非抢占式
            for task in self.tasks:
                if remainedTime == 0:
                    break
                # 首先应该把正在执行的任务给搞完，这种任务必然只有一个的，所以找到这个任务并且操作完毕后就可以break
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

            # 如果还有时间的话，再让最先截止时间的程序先上
            self.tasks.sort(key=lambda x: x.deadline)
            for task in self.tasks:
                if remainedTime == 0:
                    break
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
