from .manager import *
from typing import Any
import enum
import pynput
import pynput.keyboard._base as base
import pynput.keyboard._xorg as xorg


class KeyAction(enum.Enum):
    PRESS = 0
    RELEASE = 1


class PynputKeyboardEvent:
    def __init__(self, key: base.KeyCode | xorg.Key, action: KeyAction):
        if isinstance(key, pynput.keyboard._base.KeyCode):
            _key = key
        elif isinstance(key, enum.Enum):
            _key = key.value
        else:
            raise ValueError(f"Invalid key '{key}'")
        self.key = _key
        self.action = action


def str_to_keycode(name: str) -> base.KeyCode:
    try:
        return xorg.Key.__members__[name].value
    except KeyError as e:
        return xorg.KeyCode.from_char(name)


class KeyboardConfigMeta(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.SPECIAL_KEYS = xorg.Key
        self.SPECIAL_KEYS_NAMES = {key.value: key.name for key in xorg.Key.__members__.values()}
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            return str_to_keycode(name)


class KeyboardConfig(EventManager[PynputKeyboardEvent, base.KeyCode, base.KeyCode], metaclass=KeyboardConfigMeta):
    """
    Handler for keyboard
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listener = pynput.keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
    
    def _on_press(self, key: base.KeyCode | xorg.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, KeyAction.PRESS)
        )
    
    def _on_release(self, key: base.KeyCode | xorg.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, KeyAction.RELEASE)
        )
        
    def is_input_valid(self, input: str) -> bool:
        return True
    
    def get_input_id(self, input: str) -> str:
        return input
    
    def get_input_offset(self, input: str) -> float:
        return 0.0
    
    def get_input_amplitude(self, input: str) -> float:
        return 1.0
    
    def find_input(self, id: str) -> str:
        return id
    
    def get_event_id(self, event: PynputKeyboardEvent) -> str:
        return event.key
    
    def get_event_raw_value(self, event: PynputKeyboardEvent) -> float:
        return 1.0 if event.action is KeyAction.PRESS else 0.0
    
    def get_input_name(self, input: base.KeyCode) -> str:
        if input.char is not None:
            return input.char
        try:
            return KeyboardConfig.SPECIAL_KEYS_NAMES[input]
        except KeyError:
            return str(input)
    
    def make_input(self, input_like: base.KeyCode | xorg.Key | str) -> int:
        try:
            if isinstance(input_like, base.KeyCode):
                return input_like
            if isinstance(input_like, enum.Enum):
                return input_like.value
            if isinstance(input_like, str):
                return str_to_keycode(input_like)
            raise ValueError
        except:
            raise ValueError(f"Unable to interpret '{input_like}' as a keyboard input")


SPECIAL_KEYS = KeyboardConfig.SPECIAL_KEYS
