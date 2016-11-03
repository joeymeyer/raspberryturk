from raspberryturk import is_running_on_raspberryturk, RaspberryTurkError

if not is_running_on_raspberryturk():
    raise RaspberryTurkError("Must be running on Raspberry Turk to use {} module.".format(__name__))
