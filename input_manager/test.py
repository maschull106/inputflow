from input_manager.keyboard import KeyboardConfig


if __name__ == "__main__":
    config = KeyboardConfig()
    config.background_loop(daemon=False)
