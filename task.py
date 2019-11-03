from abc import abstractmethod


class ProvideNeedlessTime(Exception):
    pass

class Task():
    def __init__(self, arrivalTime, executeTime, deadline, priority=0):
        self.arrivalTime = arrivalTime
        self.executeTime = executeTime
        self.deadline = deadline
        self.priority = priority
        self.needTime = executeTime
        self.haveDone = 0
        self.isExtracted = False
        self.result = None

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
            self.result = self.completeWork()

    @abstractmethod
    def completeWork(self):
        pass


class Scheduler(object):
    pidIndex = 0
    def __init__(self):
        self.tasks = []
        self.results = []

    def addTask(self,task):
        task.setPid(self.pidIndex)
        self.pidIndex = self.pidIndex+1
        self.tasks.append(task)

    def completedTasks(self):
        completed_tasks = [t for t in self.tasks if t.isCompleted() and not t.isExtracted]
        for t in completed_tasks:
            t.isExtracted = True
        return completed_tasks

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
        pass