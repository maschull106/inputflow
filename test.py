import sys
from input_manager.manager import EventManager


def print_input_value_info(config: EventManager, value: float, input_origin: str, eps: float = 0.1):
    if 0 < abs(value) < eps:
        return
    print(f"{config.INPUTS[input_origin]+' :':<10s}{value}")


def test_keyboard():
    from input_manager.keyboard import KeyboardConfig
    config = KeyboardConfig()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", provide_input_origin=True)
    config.background_loop(daemon=False)


def test_gamepad():
    from input_manager.gamepad import GamePadConfig
    config = GamePadConfig()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", provide_input_origin=True)
    config.background_loop(daemon=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Please specify the name of the test as command line argument")
    if sys.argv[1] == "keyboard":
        test_keyboard()
    elif sys.argv[1] == "gamepad":
        test_gamepad()
    else:
        raise ValueError(f"Unknown test \"{sys.argv[1]}\"")
