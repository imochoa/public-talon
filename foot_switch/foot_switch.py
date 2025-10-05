"""
In a hotkey event, eg "key(ctrl:down)", any key you press with key/insert
actions will be combined with ctrl since it's still held. Just updating a
boolean in the actual hotkey event and reading it asynchronously with cron
gets around this issue.
    > cron.interval("16ms", on_interval)
Or using threading

A much easier option is to trigger on the up event: key(ctrl:up).
Where nothing is held down

# References
- https://github.com/AndreasArvidsson/andreas-talon/tree/master/core/foot_switch
"""

from talon import Module, Context, actions, cron, settings
import time
import logging
from enum import IntEnum

mod = Module()
mod.setting(
    "reverse_footswitch_scroll",
    type=bool,
    default=False,
    desc="tag for reversing the scroll direction of the foot switch",
)
mod.setting(
    "footswitch_hold_timeout",
    type=float,
    default=0.2,
    desc="timeout for holding the foot switch",
)
mod.setting(
    "footswitch_double_click_timeout",
    type=float,
    default=0.2,
    desc="timeout for double clicking the foot switch",
)


class State(IntEnum):
    DOWN = 0
    """
    Pressed
    """
    UP = 1
    """
    Unpressed/Released
    """


class Key(IntEnum):
    """
    map each foot switch pedal to an int
    """

    LEFT = 0
    CENTER = 1
    RIGHT = 2
    TOP = 3


current_state = {i: State.UP for i in range(4)}
last_state = {i: State.UP for i in range(4)}
timestamps = [0.0 for i in range(4)]  # Updated on EVERY event: up/down
prev_timestamps = [0.0 for i in range(4)]  # Updated on EVERY event: up/down


def on_interval():
    """
    (2/3)

    Do not save the large dictionary as a constant, has to be found dynamically!
    """
    global current_state, last_state, timestamps, prev_timestamps

    for key in (Key(i) for i in range(4)):
        now = time.perf_counter()  # [s]
        if current_state[key] != last_state[key]:
            # State changed for that key

            if current_state[key] == State.DOWN and (
                now - prev_timestamps[key] < settings.get("user.footswitch_double_click_timeout")
            ):  # [s]
                # Double click (only on DOWN)
                flipped_state_fcn = {
                    Key.LEFT: actions.user.foot_switch_left_double_click,
                    Key.CENTER: actions.user.foot_switch_center_double_click,
                    Key.RIGHT: actions.user.foot_switch_right_double_click,
                    Key.TOP: actions.user.foot_switch_top_double_click,
                }[key]
            else:
                # Single click
                flipped_state_fcn = {
                    (State.DOWN, Key.LEFT): actions.user.foot_switch_left_down,
                    (State.DOWN, Key.CENTER): actions.user.foot_switch_center_down,
                    (State.DOWN, Key.RIGHT): actions.user.foot_switch_right_down,
                    (State.DOWN, Key.TOP): actions.user.foot_switch_top_down,
                    (State.UP, Key.LEFT): actions.user.foot_switch_left_up,
                    (State.UP, Key.CENTER): actions.user.foot_switch_center_up,
                    (State.UP, Key.RIGHT): actions.user.foot_switch_right_up,
                    (State.UP, Key.TOP): actions.user.foot_switch_top_up,
                }[current_state[key], key]
            flipped_state_fcn()
            last_state[key] = current_state[key]  # to prevent future calls
            continue  # to next key

        # No state change for that key
        if timestamps[key] <= 0:
            continue  # Key has already been handled (***) -> skip

        if now - timestamps[key] > settings.get("user.footswitch_hold_timeout"):  # [s]
            timestamps[key] = 0.0  # Prevents future calls (***)
            no_state_change_fcn = {
                (State.DOWN, Key.LEFT): actions.user.foot_switch_left_held,
                (State.DOWN, Key.CENTER): actions.user.foot_switch_center_held,
                (State.DOWN, Key.RIGHT): actions.user.foot_switch_right_held,
                (State.DOWN, Key.TOP): actions.user.foot_switch_top_held,
                (State.UP, Key.LEFT): actions.user.foot_switch_left_released,
                (State.UP, Key.CENTER): actions.user.foot_switch_center_released,
                (State.UP, Key.RIGHT): actions.user.foot_switch_right_released,
                (State.UP, Key.TOP): actions.user.foot_switch_top_released,
            }[current_state[key], key]
            no_state_change_fcn()


# In a hotkey event, eg "key(ctrl:down)", any key you press with key/insert
# actions will be combined with ctrl since it's still held. Just updating a
# boolean in the actual hotkey event and reading it asynchronously with cron
# gets around this issue.
cron.interval("16ms", on_interval)


@mod.action_class
class Actions:
    """
    methods only called on change!
    """

    def foot_switch_down_event(key: int) -> None:
        """
        (1/3) Update the global foot switch data
        Key events. Don't touch these.
        """
        global current_state, last_state, timestamps, prev_timestamps
        prev_timestamps[key] = timestamps[key]
        timestamps[key] = time.perf_counter()
        current_state[key] = State.DOWN

    def foot_switch_up_event(key: int) -> None:
        """
        (1/3) Update the global foot switch data
        Key events. Don't touch these.
        """
        global current_state, last_state, timestamps, prev_timestamps
        prev_timestamps[key] = timestamps[key]
        timestamps[key] = time.perf_counter()
        current_state[key] = State.UP

    def foot_switch_top_down() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Top] DOWN")

    def foot_switch_top_double_click() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Top] DOUBLE CLICK")

    def foot_switch_top_up() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Top] UP")

    def foot_switch_top_held() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Top] HELD")

    def foot_switch_top_released() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Top] RELEASED")

    def foot_switch_center_down() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Center] DOWN")

    def foot_switch_center_double_click() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Center] DOUBLE CLICK")

    def foot_switch_center_up() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Center] UP")

    def foot_switch_center_held() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Center] HELD")

    def foot_switch_center_released() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Center] RELEASED")

    def foot_switch_left_down() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Left] DOWN")

    def foot_switch_left_double_click() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Left] DOUBLE CLICK")

    def foot_switch_left_up() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Left] UP")

    def foot_switch_left_held() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Left] HELD")

    def foot_switch_left_released() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Left] RELEASED")

    def foot_switch_right_down() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Right] DOWN")

    def foot_switch_right_double_click() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Right] DOUBLE CLICK")

    def foot_switch_right_up() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Right] UP")

    def foot_switch_right_held() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Right] HELD")

    def foot_switch_right_released() -> None:
        """
        (3/3) <Should be overwritten by a separate implementation>
        """
        print("Unhandled Footswitch [Right] RELEASED")
