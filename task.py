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

    def setPid(self,pid):
        self.pid = pid

    def isCompleted(self):
        return self.executeTime == self.haveDone

    def work(self, getTime):
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
    pidIndex = 0
    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks = []
        self.results = []

    def addTask(self,task):
        task.setPid(self.pidIndex)
        self.pidIndex = self.pidIndex+1
        self.tasks.append(task)
    @abstractmethod
    def work(self,time):
        pass

    # @abstractmethod
    # def getResults(self):
    #     pass

class SchedulResult:
    def __init__(self,pid,startTime,duration):
        self.startTime = startTime
        self.duration = duration
        self.endTime = startTime + duration
        self.pid = pid
    def __str__(self):
        return "pid:%s  startTime:%s  duration:%s  endTime:%s"%(self.pid,self.startTime,self.duration,self.endTime)

class TurnLeft(Task):
    def __init__(self, arrivalTime, executeTime, deadline, priority=0):
        super(TurnLeft, self).__init__(arrivalTime,executeTime,deadline)

    def completeWork(self):
        print('完成了一个TurnLeft')