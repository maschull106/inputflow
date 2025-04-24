import sys
from input_manager.manager import EventManager


def print_input_value_info(config: EventManager, value: float, input_origin: str, eps: float = 0.1) -> None:
    if 0 < abs(value) < eps:
        return
    print(f"{config.get_input_name(input_origin)+' :':<10s}{value}")


def test_keyboard() -> None:
    from input_manager.keyboard import KeyboardConfig
    config = KeyboardConfig()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", "input_origin")
    config.background_loop(daemon=False)


def test_keyboard_pynput() -> None:
    from input_manager.keyboard_pynput import KeyboardConfig
    config = KeyboardConfig()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", "input_origin")
    config.background_loop(daemon=False)


def test_gamepad() -> None:
    from input_manager.gamepad import GamePadConfig
    config = GamePadConfig()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", "input_origin")
    config.background_loop(daemon=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Please specify the name of the test as command line argument")
    
    tests = {
        "keyboard": test_keyboard,
        "keyboard_pynput": test_keyboard_pynput,
        "gamepad": test_gamepad,
    }
    try:
        tests[sys.argv[1]]()
    except KeyError as e:
        raise ValueError(f"Unknown test \"{sys.argv[1]}\"") from e
