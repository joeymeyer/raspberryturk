from raspberryturk import is_running_on_raspberryturk, RaspberryTurkError

if is_running_on_raspberryturk():
    raise RaspberryTurkError("Must not be running on Raspberry Turk to use {} module.".format(__name__))
