from vehicle import Driver
from controller import Keyboard
import math
import sys
sys.path.append("../../realsysalgorithm")
from FIFO import FIFO
from EDF import EDF
from Priority import Priority
from RoundRobin import RoundRobin

from task import Task



display = None
collision_avoidance = None
gps = None
camera = None
speedometer_image = None
autodrive = True
driver = Driver()
basicTimeStep = int(driver.getBasicTimeStep())
TIME_STEP = 100

UNKNOWN = 99999.9
FILTER_SIZE = 3
steering_angle = 0.0
KP = 0.25
KI = 0.00
KD = 2
gps_coords = [0.0 for i in range(3)]
gps_speed = 0.0
speed = 0
sick_fov = -1.0

keyboard = Keyboard()


def setSpeed(kmh):
    global speed
    speed = 250.0 if kmh > 250.0 else kmh
    print("setting speed to {} km/h".format(speed))
    driver.setCruisingSpeed(speed)

def set_autodrive(onoff):
    global autodrive
    if autodrive == onoff:
        return
    autodrive = onoff
    if autodrive == False:
        print("switching to manual drive...\n")
        print("hit [A] to return to auto-drive.\n")
    else:
        if camera:
            print("switching to auto-drive...\n")
        else:
            print("impossible to switch auto-drive on without camera...\n")

manual_steering = 0
def change_manual_steer_angle(inc):
    global manual_steering
    set_autodrive(False)
    new_manual_steering = manual_steering + inc
    if new_manual_steering <= 25.0 and new_manual_steering >= -25.0:
        manual_steering = new_manual_steering
        set_steering_angle(manual_steering * 0.02)
    if manual_steering == 0.0:
        print("going straight\n")
    else:
        print("turning %.2f rad (%s)\n"%(steering_angle, "left" if steering_angle < 0 else "right"))


def check_keyboard():
    key = keyboard.getKey()
    if key == keyboard.UP:
        setSpeed(speed + 5.0)
    elif key == keyboard.DOWN:
        setSpeed(speed - 5.0)
    elif key == keyboard.RIGHT:
        change_manual_steer_angle(+1)
    elif key == keyboard.LEFT:
        change_manual_steer_angle(-1)
    elif key == "A":
        set_autodrive(True)
    pass

def color_diff(a, b):
    diff = 0
    for i in range(3):
        d = ord(a[i]) - b[i]
        diff += d if d > 0 else -d
    return diff


def process_camera_image(image):
    num_pixels = camera.getWidth()  * camera.getHeight()
    REF = [95, 187, 203]
    sumx = 0
    pixel_count = 0
    pixel = 0
    for x in range(num_pixels):
        if color_diff(image[pixel:pixel+4], REF) < 30:
            sumx += x % camera.getWidth()
            pixel_count += 1
        pixel += 4

    if pixel_count == 0:
        return UNKNOWN

    return (sumx * 1.0 / pixel_count / camera.getWidth() - 0.5) * camera.getFov()

first_call = True
old_value = [0.0 for i in range(FILTER_SIZE)]

def filter_angle(new_value):
    global first_call
    global old_value
    if first_call or new_value == UNKNOWN:
        first_call = False
        old_value = [0.0 for i in range(FILTER_SIZE)]
    else:
        for i in range(FILTER_SIZE - 1):
            old_value[i] = old_value[i + 1]
    if new_value == UNKNOWN:
        return UNKNOWN
    else:
        old_value[FILTER_SIZE - 1] = new_value
        sum = 0.0
        for i in range(FILTER_SIZE):
            sum += old_value[i]
        return sum / FILTER_SIZE


def process_sick_data(sick_data):
    # print("sick_data: ", sick_data)
    HALF_AREA = 20
    sumx = 0
    collision_count = 0
    obstacle_dist = 0.0

    sick_width = collision_avoidance.getHorizontalResolution()
    x = int(sick_width/ 2 - HALF_AREA)

    while x < int(sick_width / 2 + HALF_AREA):
        r = sick_data[x]
        if r < 20.0:
            sumx += x
            collision_count += 1
            obstacle_dist += r
        x += 1
    print("collision_count in the function: ", collision_count)

    if collision_count == 0 or obstacle_dist == 0.0:
        return UNKNOWN, obstacle_dist

    obstacle_dist = obstacle_dist / collision_count

    return (1.0*sumx/collision_count/sick_width-0.5) * collision_avoidance.getFov(), obstacle_dist


PID_need_reset = False
oldValue = 0.0
integral = 0.0

sche = None
preemption = False
scheMethod = 'Priority'

if scheMethod == 'EDF':
    sche = EDF(preemption)
elif scheMethod == 'FIFO':
    sche = FIFO()
elif scheMethod == 'Priority':
    sche = Priority(preemption)
elif scheMethod == 'RoundRobin':
    sche = RoundRobin()




def applyPID(yellow_line_angle):
    global PID_need_reset
    global oldValue
    global integral
    if PID_need_reset:
        oldValue = yellow_line_angle
        integral = 0.0
        PID_need_reset = False

    sign = lambda x: math.copysign(1, x)
    if sign(yellow_line_angle) != sign(oldValue):
        integral = 0.0

    diff = yellow_line_angle - oldValue
    if integral < 30 and integral > -30:
        integral += yellow_line_angle
    oldValue = yellow_line_angle
    return KP * yellow_line_angle + KI * integral + KD * diff


def set_steering_angle(wheel_angle):
    global steering_angle
    if wheel_angle - steering_angle > 0.1:
        wheel_angle = steering_angle + 0.1
    if wheel_angle - steering_angle < -0.1:
        wheel_angle = steering_angle - 0.1
    steering_angle = wheel_angle
    if wheel_angle > 0.5:
        wheel_angle = 0.5
    elif wheel_angle < -0.5:
        wheel_angle = -0.5
    # print("wheel_angle: ", wheel_angle)
    driver.setSteeringAngle(wheel_angle)

def compute_gps_speed():
    global gps_coords
    global gps_speed
    coords = gps.getValues()
    speed_ms = gps.getSpeed()
    gps_speed = speed_ms * 3.6
    gps_coords = coords


def update_display():
    NEEDLE_LENGTH = 50.0
    display.imagePaste(speedometer_image, 0, 0, False)
    current_speed = driver.getCurrentSpeed()
    if math.isnan(current_speed):
        current_speed = 0.0

    alpha = current_speed / 260.0 * 3.72 - 0.27
    x = -NEEDLE_LENGTH * math.cos(alpha)
    y = -NEEDLE_LENGTH * math.sin(alpha)
    display.drawLine(100, 95, int(100 + x), int(95 + y))
    txt = "GPS coords: %.1f %.1f" %(gps_coords[0], gps_coords[2])
    display.drawText(txt, 10, 130)
    txt = "GPS speed:  %.1f" %(gps_speed)
    display.drawText(txt, 10, 140)

ep = 0.00001

class  UpdateDisplayTask(Task):
    def completeWork(self):
        update_display()
        return None

class ComputeGPSSpeedTask(Task):
    def completeWork(self):
        compute_gps_speed()
        return None

class SetSteeringAngleTask(Task):
    def setSteer(self, steer):
        self.steer = steer
    def completeWork(self):
        set_steering_angle(self.steer)
        return None

class CameraTask(Task):
    def completeWork(self):
        return camera.getImage()

class LidarTask(Task):
    def completeWork(self):
        return collision_avoidance.getRangeImage()

class ComputeTask(Task):
    def completeWork(self):
        print("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", self.pid)
        global PID_need_reset
        yellow_line_angle = filter_angle(process_camera_image(self.camera_image))
        obstacle_angle = UNKNOWN
        obstacle_dist = UNKNOWN

        if collision_avoidance:
            obstacle_angle, obstacle_dist = process_sick_data(self.sick_data)
        print("obstacle_angle: ", obstacle_angle)
        print("obstacle_dist: ", obstacle_dist)
        # print("yellow_line_angle: ", yellow_line_angle)

        if collision_avoidance and math.fabs(obstacle_angle - UNKNOWN) > ep:
            driver.setBrakeIntensity(0.0)
            obstacle_steering = steering_angle
            if obstacle_angle > 0.0 and obstacle_angle < 0.4:
                obstacle_steering = steering_angle + (obstacle_angle - 0.40) / obstacle_dist
            elif obstacle_angle > -0.4:
                obstacle_steering = steering_angle + (obstacle_angle + 0.40) / obstacle_dist
            print("obstacle_steering: ", obstacle_steering)

            steer = steering_angle
            if math.fabs(yellow_line_angle - UNKNOWN) > ep:
                line_following_steering = applyPID(yellow_line_angle)
                print("line_following_steering: ", line_following_steering)
                if obstacle_steering > 0 and line_following_steering > 0:
                    steer = obstacle_steering if obstacle_steering > line_following_steering else line_following_steering
                elif obstacle_steering < 0 and line_following_steering < 0:
                    steer = obstacle_steering if obstacle_steering < line_following_steering else line_following_steering
                else:
                    # steer = obstacle_steering
                    steer = obstacle_steering * 0.85 + line_following_steering * 0.15

            else:
                print("PID_need_reset")
                PID_need_reset = True
            print("steer :", steer)

            t = SetSteeringAngleTask(self.st, 1, 8, 1)
            t.steer = steer
            sche.addTask(t)

        elif math.fabs(yellow_line_angle - UNKNOWN) > ep:
            driver.setBrakeIntensity(0.0)
            t = SetSteeringAngleTask(self.st, 1, 8, 1)
            t.steer = applyPID(yellow_line_angle)
            sche.addTask(t)
        else:
            driver.setBrakeIntensity(0.4)
            PID_need_reset = True
        return None

if __name__ == '__main__':

    assert sche

    print(driver.getNumberOfDevices())
    for i in range(driver.getNumberOfDevices()):
        print(driver.getDeviceByIndex(i).getName())
        dev = driver.getDeviceByIndex(i)
        name = dev.getName()
        if name == "Sick LMS 291":
            collision_avoidance = dev
            collision_avoidance.enable(TIME_STEP)
        elif name == "display":
            display = dev
        elif name == "gps":
            gps = dev
            gps.enable(TIME_STEP)
        elif name == "camera":
            camera = dev
            camera.enable(TIME_STEP)

    speedometer_image = display.imageLoad("speedometer.png")

    if camera:
        setSpeed(30.0)

    driver.setHazardFlashers(True)
    # driver.setThrottle(True)
    driver.setAntifogLights(True)
    driver.setWiperMode(driver.SLOW)

    keyboard.enable(TIME_STEP)

    i = 0
    camera_image = None
    sick_data = None

    while driver.step() != -1:
        check_keyboard()
        if i % int(TIME_STEP / basicTimeStep) == 0:

            print("-----------------------------------", i)
            sche.addTask(CameraTask(i, 2, 10, 1))
            sche.addTask(LidarTask(i, 2, 10, 1))
            completedTask = sche.completedTasks()
            print("completedTask: ", len(completedTask))
            for t in completedTask:
                if isinstance(t, CameraTask):
                    print("camera")
                    camera_image = t.result
                if isinstance(t, LidarTask):
                    print("sick_data")
                    sick_data = t.result
            # camera_image = camera.getImage()
            # sick_data = collision_avoidance.getRangeImage()

            if camera_image and sick_data:
                print("################################    ComputeTask")
                t = ComputeTask(i, 1, 5, 0)
                t.camera_image = camera_image
                t.sick_data = sick_data
                t.st = i
                sche.addTask(t)

            if i % (int(TIME_STEP / basicTimeStep) * 2) == 0:
                if gps:
                    sche.addTask(ComputeGPSSpeedTask(i, 3, 20, 3))
                if display:
                    sche.addTask(UpdateDisplayTask(i, 3, 20, 4))

        i += 1
        sche.work(1)
