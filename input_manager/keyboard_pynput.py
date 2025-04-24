from .manager import *
from typing import Any
import enum
import pynput
import pynput.keyboard._base as base
import pynput.keyboard._xorg as xorg
# import pynput.keyboard._win32 as win32
# import pynput.keyboard._darwin as darwin
# import pynput.keyboard._uinput as uinput


class Action(enum.Enum):
    PRESS = 0
    RELEASE = 1


class PynputKeyboardEvent:
    def __init__(self, key: base.KeyCode | xorg.Key, action: Action):
        if isinstance(key, pynput.keyboard._base.KeyCode):
            _key = key
        elif isinstance(key, enum.Enum):
            _key = key.value
        else:
            raise ValueError(f"Invalid key '{key}'")
        self.key = _key
        self.action = action



class KeyboardConfigMeta(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in xorg.Key.__members__.values():
            setattr(self, key.name, key.value)


class KeyboardConfig(EventManager[PynputKeyboardEvent, base.KeyCode, base.KeyCode], metaclass=KeyboardConfigMeta):
    """
    Handler for keyboard
    """
    
    SPECIAL_KEYS = xorg.Key

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listener = pynput.keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
    
    def _on_press(self, key: base.KeyCode | xorg.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, Action.PRESS)
        )
    
    def _on_release(self, key: base.KeyCode | xorg.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, Action.RELEASE)
        )
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            return name
        
    def is_input_valid(self, input: str) -> bool:
        return True
    
    def get_input_id(self, input: str) -> str:
        return input
    
    def get_input_offset(self, input: str) -> float:
        return 0.0
    
    def get_input_amplitude(self, input: str) -> float:
        return 1.0
    
    def find_input(self, id: str) -> str:
        """
        Determine the input that has the given id.
        :return: an input type
        """
        return id
    
    def get_event_id(self, event: PynputKeyboardEvent) -> str:
        """
        Overrides parent method
        """
        return event.key
    
    def get_event_raw_value(self, event: PynputKeyboardEvent) -> float:
        """
        Overrides parent method
        """
        return 1.0 if event.action is Action.PRESS else 0.0


SPECIAL_KEYS = KeyboardConfig.SPECIAL_KEYS


if __name__ == "__main__":
    config = KeyboardConfig()
    config.background_loop()
