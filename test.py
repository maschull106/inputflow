import sys
from inputflow.flow_core import HandlerCore


def print_input_value_info(config: HandlerCore, value: float, input_origin: str, eps: float = 0.1) -> None:
    if 0 < abs(value) < eps:
        return
    print(f"{config.get_input_name(input_origin)+' :':<10s}{value}")


def test_keyboard() -> None:
    from inputflow.keyboard import KeyboardHandler
    config = KeyboardHandler()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", "input_origin")
    config.bind(KeyboardHandler.enter, lambda value: print("A"*10, value), "value")
    config.background_loop(daemon=False)


def test_gamepad() -> None:
    from inputflow.gamepad import GamepadHandler
    config = GamepadHandler()
    _print_input_value_info = lambda *args, **kwargs: print_input_value_info(config, *args, **kwargs)
    config.bind_all(_print_input_value_info, "value", "input_origin")
    config.background_loop(daemon=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Please specify the name of the test as command line argument")
    
    tests = {
        "keyboard": test_keyboard,
        "gamepad": test_gamepad,
    }
    try:
        tests[sys.argv[1]]()
    except KeyError as e:
        raise ValueError(f"Unknown test \"{sys.argv[1]}\"") from e
