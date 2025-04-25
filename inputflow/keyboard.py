from .flow_core import *
from typing import Any
import enum
import pynput.keyboard as kbrd


class KeyAction(enum.Enum):
    PRESS = 0
    RELEASE = 1


class PynputKeyboardEvent:
    def __init__(self, key: kbrd.KeyCode | kbrd.Key, action: KeyAction):
        if isinstance(key, kbrd.KeyCode):
            _key = key
        elif isinstance(key, enum.Enum):
            _key = key.value
        else:
            raise ValueError(f"Invalid key '{key}'")
        self.key = _key
        self.action = action


def str_to_keycode(name: str) -> kbrd.KeyCode:
    try:
        return kbrd.Key.__members__[name].value
    except KeyError as e:
        return kbrd.KeyCode.from_char(name)


class KeyboardHandlerMeta(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.SPECIAL_KEYS = kbrd.Key
        self.SPECIAL_KEYS_NAMES = {key.value: key.name for key in kbrd.Key.__members__.values()}
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            return str_to_keycode(name)


class KeyboardHandler(HandlerCore[PynputKeyboardEvent, kbrd.KeyCode, kbrd.KeyCode], metaclass=KeyboardHandlerMeta):
    """
    Handler for keyboard
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listener = kbrd.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
    
    def _on_press(self, key: kbrd.KeyCode | kbrd.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, KeyAction.PRESS)
        )
    
    def _on_release(self, key: kbrd.KeyCode | kbrd.Key) -> None:
        self.handle_event(
            PynputKeyboardEvent(key, KeyAction.RELEASE)
        )
        
    def is_input_valid(self, input: kbrd.KeyCode) -> bool:
        return isinstance(input, kbrd.KeyCode)
    
    def get_input_id(self, input: kbrd.KeyCode) -> kbrd.KeyCode:
        return input
    
    def find_input(self, id: kbrd.KeyCode) -> kbrd.KeyCode:
        return id
    
    def get_event_id(self, event: PynputKeyboardEvent) -> kbrd.KeyCode:
        return event.key
    
    def get_event_raw_value(self, event: PynputKeyboardEvent) -> float:
        return 1.0 if event.action is KeyAction.PRESS else 0.0
    
    def get_input_name(self, input: kbrd.KeyCode) -> str:
        if input.char is not None:
            return input.char
        try:
            return KeyboardHandler.SPECIAL_KEYS_NAMES[input]
        except KeyError:
            return str(input)
    
    def make_input(self, input_like: kbrd.KeyCode | kbrd.Key | str) -> int:
        try:
            if isinstance(input_like, kbrd.KeyCode):
                return input_like
            if isinstance(input_like, enum.Enum):
                return input_like.value
            if isinstance(input_like, str):
                return str_to_keycode(input_like)
            raise ValueError
        except:
            raise ValueError(f"Unable to interpret '{input_like}' as a keyboard input")


SPECIAL_KEYS = KeyboardHandler.SPECIAL_KEYS
