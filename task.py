from abc import ABC, abstractmethod


class ProvideNeedlessTime(Exception):
    pass

class Task(ABC):
    def __init__(self, arrivalTime, executeTime, deadline, priority=0):
        super(Task, self).__init__()
        self.arrivalTime = arrivalTime
        self.executeTime = executeTime
        self.deadline = deadline
        self.priority = priority
        self.needTime = executeTime

        self.haveDone = 0

    def isCompleted(self) -> bool:
        return self.executeTime == self.haveDone

    def work(self, getTime) -> None:
        if getTime > self.needTime:
            raise ProvideNeedlessTime

        self.haveDone = self.haveDone + getTime
        self.needTime = self.needTime - getTime
        if self.isCompleted():
            self.completeWork()

    @abstractmethod
    def completeWork(self):
        pass


class Scheduler(ABC):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks:[Task] = [Task]
        self.results:[SchedulResult] = [SchedulResult]

    def addTask(self,task:Task):
        self.tasks.append(task)
    @abstractmethod
    def work(self,time):
        pass

    # @abstractmethod
    # def getResults(self):
    #     pass

class SchedulResult:
    def __init__(self,startTime,duration):
        self.startTime = startTime
        self.duration = duration
        self.endTime = startTime + duration

class TestTask(Task):
    def completeWork(self):
        pass