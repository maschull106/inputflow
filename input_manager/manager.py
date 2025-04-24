from __future__ import annotations
import threading
from dataclasses import dataclass
from collections.abc import Callable
from typing import List, Dict, TypeVar, Generic
from abc import ABC, abstractmethod


T = TypeVar("T")
EventType = TypeVar("EventType")
IdType = TypeVar("IdType")
InputType = TypeVar("InputType")


@dataclass
class EventInfo(Generic[InputType]):
    input: InputType
    event_value: float


class EventFuncWrapper(Generic[T]):
    """
    keeping information about a function to be called upon a certain event, the function must take the event value as a parameter
    """

    def __init__(self, func: Callable[..., T] = None, event_value_arg_name: str = "", input_origin_arg_name: str = "", **kwargs):
        """
        :param func: the function to call
        :param event_value_arg_name: the name of the function's parameter for the event value (if none is given, the event value won't be passed to the function)
        :param kwargs: additional arguments of the function
        """
        if func is None:
            func = lambda *args, **kwargs: None
        self.func = func
        self.event_value_arg_name = event_value_arg_name
        self.input_origin_arg_name = input_origin_arg_name
        self.kwargs = kwargs
        if event_value_arg_name:
            self.kwargs[event_value_arg_name] = None
    
    def __call__(self, event_info: EventInfo) -> T:
        if self.event_value_arg_name:
            self.kwargs[self.event_value_arg_name] = event_info.event_value
        if self.input_origin_arg_name:
            self.kwargs[self.input_origin_arg_name] = event_info.input
        return self.func(**self.kwargs)


# class MetaEventManager(type):
#     """
#     Metaclass for EventHandlerConfig and all its child classes
#     """
#     def __init__(self, *args, **kwargs):
#         self.NULL = -1
#         if not hasattr(self, "INPUTS"):
#             self.INPUTS = {}
#         default_ids = {inp: -1 for inp in self.INPUTS}
#         if not hasattr(self, "DEFAULT_IDS"):
#             self.DEFAULT_IDS = default_ids
#         else:
#             self.DEFAULT_IDS = default_ids | self.DEFAULT_IDS


class EventManager(Generic[EventType, IdType, InputType]): #, ABC):
    """
    (abstract class)
    Handler for input events giving a continuous value (and also discrete values which are treated as continuous values)
    from a physical (or not) device, for example keyboard or gamepad.
    Comprises input ids, value offsets and amplitudes.
    Also allows to bind functions to be called upon the event of a certain input.
    """
    NULL: InputType = None
    
    def __init__(self, **kwargs):
        """
        :param kwargs: Must contain all the ids, offsets and amplitudes of the inputs that need to be set to a different than default value.
            All parameters need to be given as keyword arguments in the format [name of input]_id, [name of input]_offset and [name of input]_amplitude.
            Default ids are given by EventHandlerConfig.DEFAULT_IDS, default offsets are set to 0,  default amplitudes are set to 1.
        """
        self.smoothing_epsilon = kwargs.get("smoothing_epsilon", 0)

        # list of functions to be called on event for every input
        self.event_signals : Dict[InputType, List[EventFuncWrapper]] = {}   # {k: [] for k in self.INPUTS}
        self.common_event_signals : List[EventFuncWrapper] = []

    def is_input_valid(self, input: InputType) -> bool:
        return True
    
    def enforce_valid_input(self, input: InputType) -> None:
        if not self.is_input_valid(input):
            raise ValueError(f"Invalid input '{input}' for '{self.__class__.__name__}")
    
    # @abstractmethod
    def get_input_id(self, input: InputType) -> IdType:
        ...
    
    # @abstractmethod
    def get_input_offset(self, input: InputType) -> float:
        ...
    
    # @abstractmethod
    def get_input_amplitude(self, input: InputType) -> float:
        ...
    
    # @abstractmethod
    def find_input(self, id: IdType) -> InputType:
        """
        Determine the input that has the given id.
        :return: an input type
        """
        ...
    
    def get_input_name(self, input: InputType) -> str:
        return str(input)

    def bind(self, input: InputType, func: Callable, event_value_arg_name: str = "", **kwargs) -> None:
        """
        Bind a function call to the trigger event of a certain input.
        :param input: an input type
        :param func: the function to bind (it needs to take the event value as a parameter)
        :param event_value_arg_name: the name of the function's parameter for the event value (if none is given, the event value won't be passed to the function)
        :param kwargs: other arguments of the function given as keyword arguments
        """
        self.enforce_valid_input(input)
        # self.event_signals[input].append(EventFuncWrapper(func, event_value_arg_name, **kwargs))
        event_func = EventFuncWrapper(func, event_value_arg_name, **kwargs)
        self.event_signals.setdefault(input, []).append(event_func)
    
    def bind_all(
            self,
            func: Callable,
            event_value_arg_name: str = "",
            input_origin_arg_name: str = "",
            **kwargs
        ) -> None:
        """
        Bind the same function call to the trigger event of all inputs at once.
        """
        event_func = EventFuncWrapper(func, event_value_arg_name, input_origin_arg_name, **kwargs)
        self.common_event_signals.append(event_func)

    def valid_event(self, event: EventType) -> bool:
        """
        A check that the event is valid.
        Should be overridden to match the specific event type of the child class.
        """
        return True
    
    def get_event_id(self, event: EventType) -> IdType:
        """
        Extract a usable event id.
        Should be overridden to match the specific event type of the child class.
        """
        return self.NULL

    def get_event_raw_value(self, event: EventType) -> float:
        """
        Should be overridden
        """
        return 1.0
    
    def smoothen(self, value: float) -> float:
        if abs(value) < self.smoothing_epsilon:
            return 0.0
        return value
    
    def get_event_value(self, input: InputType, raw_value: float) -> float:
        offset = self.get_input_offset(input)
        amplitude = self.get_input_amplitude(input)
        event_value = (raw_value - offset) / amplitude
        event_value = self.smoothen(event_value)
        return event_value
    
    def get_event_info(self, event: EventType) -> EventInfo:
        event_id = self.get_event_id(event)
        input = self.find_input(event_id)
        raw_value = self.get_event_raw_value(event)
        event_value = self.get_event_value(input, raw_value)
        return EventInfo(
            input=input,
            event_value=event_value
        )

    def handle_event(self, event: EventType) -> None:
        """
        Obtains the event info then calls then calls emit_signal for treatment of the event and calling of the binded functions
        """
        if not self.valid_event(event):
            return
        event_info = self.get_event_info(event)
        if event_info.input == self.NULL:
            return
        self.emit_signal(event_info)

    def emit_signal(self, event_info: EventInfo) -> None:
        """
        Call functions binded to input.
        :param input: an input type
        :param raw_value: raw value of the event, to be transformed to the desired range using the corresponding offset and amplitude of the config
        """
        for func in self.event_signals.get(event_info.input, []):
            func(event_info)
        for func in self.common_event_signals:
            func(event_info)

    def read_inputs(self) -> None:
        """
        Override this method to read the inputs of the specific device
        """
        pass
    
    def loop(self) -> None:
        while True:
            self.read_inputs()

    def background_loop(self, daemon: bool = True) -> None:
        thread = threading.Thread(target=self.loop, daemon=daemon)
        thread.start()
    
    def connect_events(
            src_handler: EventManager,
            src_input: int,
            target_handler: EventManager,
            target_input: int
        ) -> None:
        """
        Connect an input from one handler to an input of another handler
        """
        src_handler.enforce_valid_input(src_input)
        target_handler.enforce_valid_input(target_input)
        
        def connection(value: float) -> None:
            event_info = EventInfo(
                input=target_input,
                event_value=value
            )
            target_handler.emit_signal(event_info)
        
        src_handler.bind(src_input, connection, "value")


class MetaEventManager(type):
    """
    Metaclass for EventHandlerConfig and all its child classes
    """
    def __init__(self, *args, **kwargs):
        self.NULL = -1
        if not hasattr(self, "INPUTS"):
            self.INPUTS = {}
        default_ids = {inp: -1 for inp in self.INPUTS}
        if not hasattr(self, "DEFAULT_IDS"):
            self.DEFAULT_IDS = default_ids
        else:
            self.DEFAULT_IDS = default_ids | self.DEFAULT_IDS


class EventManagerFixedInputList(EventManager[EventType, IdType, InputType], metaclass=MetaEventManager):
    def __init__(self, **kwargs):
        """
        :param kwargs: Must contain all the ids, offsets and amplitudes of the inputs that need to be set to a different than default value.
            All parameters need to be given as keyword arguments in the format [name of input]_id, [name of input]_offset and [name of input]_amplitude.
            Default ids are given by EventHandlerConfig.DEFAULT_IDS, default offsets are set to 0,  default amplitudes are set to 1.
        """
        smoothing_epsilon = kwargs.get("smoothing_epsilon", 0)
        super().__init__(smoothing_epsilon=smoothing_epsilon)

        self.input_ids : Dict[InputType, IdType] = {}
        self.input_offsets : Dict[InputType, float] = {self.NULL: 0.0}
        self.input_amplitudes : Dict[InputType, float] = {self.NULL: 1.0}
        for input, name in self.INPUTS.items():
            attr = f"{name}_id"
            self.input_ids[input] = kwargs.get(attr, self.DEFAULT_IDS[input])
            attr = f"{name}_offset"
            self.input_offsets[input] = kwargs.get(attr, 0.0)
            attr = f"{name}_amplitude"
            self.input_amplitudes[input] = kwargs.get(attr, 1.0)

        # dict of inputs correspondig to ids (if multiple inputs have the same id, for instance -1, the behaviour is undefined)
        self.reverse_id_dict : Dict[IdType, InputType] = {}
        for inp, id in self.input_ids.items():
            self.reverse_id_dict[id] = inp
        self.fast_id_finding = True
    
    def is_input_valid(self, input: InputType) -> bool:
        return input in self.INPUTS
    
    def get_input_id(self, input: InputType) -> IdType:
        self.enforce_valid_input(input)
        return self.input_ids[input]
    
    def get_input_offset(self, input: InputType) -> float:
        self.enforce_valid_input(input)
        return self.input_offsets[input]
    
    def get_input_amplitude(self, input: InputType) -> float:
        self.enforce_valid_input(input)
        return self.input_amplitudes[input]
    
    def find_input(self, id: IdType) -> InputType:
        """
        Determine the input that has the given id.
        :return: an input type
        """
        if self.fast_id_finding:
            return self.reverse_id_dict.get(id, self.NULL)
        for input, inp_id in self.input_ids.items():
            if inp_id == id:
                return input
        return self.NULL
    
    def get_input_name(self, input: InputType) -> str:
        return self.INPUTS[input]
