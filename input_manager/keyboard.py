from .manager import *
import keyboard
import keyboard._keyboard_event
import copy
from typing import Tuple


class KeyboardConfig(EventManagerFixedInputList[keyboard._keyboard_event.KeyboardEvent, str, int]):
    """
    Handler for keyboard
    """
    
    def __init__(self, **kwargs):
        keyboard._os_keyboard.init()

        os_keyboard_inputs = copy.deepcopy(keyboard._os_keyboard.from_name)
        for inp in ("A", "D", "M", "N", "O", "P"): os_keyboard_inputs[inp] = []
        KeyboardConfig._set_inputs_as_class_attributes(os_keyboard_inputs)

        keyboard.hook(self.handle_event)
        super().__init__(**kwargs)
    
    @classmethod
    def _set_inputs_as_class_attributes(cls, os_keyboard_inputs: Dict[str, List[Tuple[int, Tuple[str, ...]]]]) -> None:
        cls.INPUTS = {}
        for ind, key in enumerate(os_keyboard_inputs):
            if key.isalpha():
                name = key
            elif key.isnumeric():
                name = "_" + key
            else:
                continue
            setattr(cls, name, ind)
            cls.INPUTS[ind] = key
        cls.DEFAULT_IDS = {inp: keyboard._canonical_names.normalize_name(key) for inp, key in cls.INPUTS.items()}
    
    def get_event_id(self, event: keyboard._keyboard_event.KeyboardEvent) -> str:
        """
        Overrides parent method
        """
        return event.name
    
    def get_event_raw_value(self, event: keyboard._keyboard_event.KeyboardEvent) -> float:
        """
        Overrides parent method
        """
        return 1.0 if event.event_type == keyboard.KEY_DOWN else 0.0


if __name__ == "__main__":
    config = KeyboardConfig()
    config.background_loop()
