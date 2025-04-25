from .manager import *
import evdev
import evdev.events
import time


class GamePadConfig(EventManagerFixedInputList[evdev.events.InputEvent, int, int]):
    """
    Handler for a gamepad using the evdev package
    """
    # TODO: make a virtual gamepad handler
    # TODO: create an interface for the touchpad
    NULL = -1
    TRIANGLE = 0
    SQUARE = 1
    CIRCLE = 2
    CROSS = 3
    L1 = 4
    R1 = 5
    L2 = 6
    R2 = 7
    L3 = 8
    R3 = 9
    CREATE = 10
    OPTIONS = 11
    PS = 12
    TOUCHPAD = 13
    LH = 14
    LV = 15
    RH = 16
    RV = 17
    DIRH = 18
    DIRV = 19
    
    BUTTONS = {TRIANGLE: "triangle", SQUARE: "square", CIRCLE: "circle", CROSS: "cross", L1: "L1", R1: "R1", L3: "L3", R3: "R3", CREATE: "create", OPTIONS: "options", PS: "PS", TOUCHPAD: "touchpad"}
    ANALOG_TRIGGERS = {RH: "RH", RV: "RV", LH: "LH", LV: "LV", L2: "L2", R2: "R2", DIRH: "dirH", DIRV: "dirV"}
    INPUTS = BUTTONS | ANALOG_TRIGGERS
    DEFAULT_IDS = {L1: 310, R1: 311, L2: 2, R2: 5, PS: 316, LH: 0, LV: 1, RH: 3, RV: 4, DIRH: 16, DIRV: 17, TRIANGLE: 307, SQUARE: 308, CIRCLE: 305, CROSS: 304}

    KNOWN_DEVICES = {
        "Generic X-Box pad",
        "Wireless Controller",
        "Sony Interactive Entertainment Wireless Controller",
        "Xbox Wireless Controller",
        "SZMY-POWER CO.,LTD. PLAYSTATION(R)3 Controller"
    }

    def __init__(self, **kwargs):
        self.device = self.connect()
        kwargs |= self._get_additional_init_kwords()
        super().__init__(**kwargs)
        
    def valid_event(self, event: evdev.events.InputEvent) -> bool:
        """
        Overrides parent method
        """
        # ignore event type 0 (not sure what it corresponds to but results in weird behaviour)
        return event.type != 0 and event.type != 4
    
    def get_event_id(self, event: evdev.events.InputEvent) -> int:
        """
        Overrides parent method
        """
        return event.code
    
    def get_event_raw_value(self, event: evdev.events.InputEvent) -> float:
        """
        Overrides parent method
        """
        return event.value
    
    def make_input(self, input_like: str | int) -> int:
        if isinstance(input_like, int):
            return input_like
        if not isinstance(input_like, str):
            raise ValueError(f"Unable to interpret '{input_like}' as a gamepad input")
        try:
            return getattr(self, input_like.upper())
        except AttributeError as e:
            raise ValueError(f"Unable to interpret '{input_like}' as a gamepad input") from e
    
    def connect(self) -> evdev.InputDevice:
        print("connecting to gamepad...")
        while True:
            for device in map(evdev.InputDevice, evdev.list_devices()):
                if device.name.strip() not in self.KNOWN_DEVICES:
                    print(f"Found unknown gamepad device [{device}]")
                    continue
                print(f"Will connect to gamepad device [{device}]")
                return device
            time.sleep(1)

    def read_inputs(self) -> None:
        """
        Overrides parent method
        """
        try:
            for event in self.device.read_loop():
                self.handle_event(event)

        except (TypeError, IOError) as e:
            raise
    
    def _get_additional_init_kwords(self) -> Dict[str, int]:
        """
        Get custom parameters corresponding to the detected device (returns empty dict if the device name is not known)
        """
        if self.device.name == "Generic X-Box pad":
            return {
                "circle_id": 305,
                "triangle_id": 308,
                "square_id": 307,
                "cross_id": 304,
                "RH_amplitude": 2**15,
                "RV_amplitude": -2**15,
                "LH_amplitude": 2**15,
                "LV_amplitude": -2**15,
                "R2_amplitude": 2**8,
                "L2_amplitude": 2**8
            }
        elif self.device.name == "Wireless Controller":
            return {
                "circle_id": 305,
                "triangle_id": 307,
                "square_id": 308,
                "cross_id": 304,
                "RH_offset": 2**7,
                "RV_offset": 2**7,
                "LH_offset": 2**7,
                "LV_offset": 2**7,
                "RH_amplitude": 2**7,
                "RV_amplitude": -2**7,
                "LH_amplitude": 2**7,
                "LV_amplitude": -2**7,
                "R2_amplitude": 2**8,
                "L2_amplitude": 2**8
            }
        elif self.device.name == "Sony Interactive Entertainment Wireless Controller":
            return {
                "circle_id": 305,
                "triangle_id": 307,
                "square_id": 308,
                "cross_id": 304,
                "RH_offset": 2**7,
                "RV_offset": 2**7,
                "LH_offset": 2**7,
                "LV_offset": 2**7,
                "RH_amplitude": 2**7,
                "RV_amplitude": -2**7,
                "LH_amplitude": 2**7,
                "LV_amplitude": -2**7,
                "R2_amplitude": 2**8,
                "L2_amplitude": 2**8
            }
        elif self.device.name == "Xbox Wireless Controller":
            return {
                "circle_id": 305, #B
                "triangle_id": 308, #Y
                "square_id": 307, #X
                "cross_id": 304, #A

                "RH_id":2,
                "RV_id":5,
                "LH_id":0,
                "LV_id":1,
                "RH_offset": 2**15,
                "RV_offset": 2**15,
                "LH_offset": 2**15,
                "LV_offset": 2**15,
                "RH_amplitude": 2**15,
                "RV_amplitude": -2**15,
                "LH_amplitude": 2**15,
                "LV_amplitude": -2**15,

                "R2_id":9,
                "L2_id":10,
                "R2_amplitude": 2**10, #RT
                "L2_amplitude": 2**10, #LT
                "R2_offset": 0,
                "L2_offset":0,

                "PS_id":316,

                "R1_id": 311, #RB
                "L1_id": 310,#LB

                "R3_id":318,
                "L3_id":317, 

                "dirH_amplitude":-1,
                "dirV_amplitude":-1,
                
                "smoothing_epsilon": 0.1

            }
        
        elif self.device.name == "SZMY-POWER CO.,LTD. PLAYSTATION(R)3 Controller":
            return {
                "circle_id": 305, #B
                "triangle_id": 307, #Y
                "square_id": 308, #X
                "cross_id": 304, #A

                "RH_id": 3,
                "RV_id": 4,
                "LH_id": 0,
                "LV_id": 1,
                "RH_offset": 128,
                "RV_offset": 128,
                "LH_offset": 128,
                "LV_offset": 128,
                "RH_amplitude": 128,
                "RV_amplitude": -128,
                "LH_amplitude": 128,
                "LV_amplitude": -128,

                "R2_id": 5,
                "L2_id": 2,
                "R2_amplitude": 255,
                "L2_amplitude": 255,
                "R2_offset": 0,
                "L2_offset":0,

                "PS_id":316,

                "R1_id": 311,
                "L1_id": 310,

                "R3_id":318,
                "L3_id":317, 

                "dirH_amplitude":-1,
                "dirV_amplitude":-1,
                
                "smoothing_epsilon": 0.1
            }
