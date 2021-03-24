
class DEVICE:

    def __init__(self, cymepy, device, memory_valiables):
        self.cymepy = cymepy
        self.device = device
        self.memory_valiables = memory_valiables
        return

    def save_state(self):
        self.states = {}

        for param in self.memory_valiables:
            self.states[param] = self.cymepy.study.QueryInfoDevice(param, self.device.DeviceNumber, self.device.DeviceType)

        print(self.states)
        return

    def restore_state(self):
        if hasattr(self, 'states'):
            for param, val in self.states.keys():
                self.cymepy.study.SetValueDevice(
                    val,
                    param,
                    self.device.DeviceNumber,
                    self.device.DeviceType
                )
        return