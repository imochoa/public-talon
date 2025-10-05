""" """

from talon import Module, Context, actions, cron, settings, speech_system
import time
import logging
from enum import IntFlag, auto, IntEnum
from threading import Timer
from typing import NamedTuple

ctx_default = Context()
ctx_default.matches = r"""
# Should be overridden by more specific contexts for other footswitch actions
mode: all
"""


@ctx_default.action_class("user")
class FootswitchDefaultActions:
    """
    Default footswitch action:
    - up/down: scroll
    - left/right: go back/forward

    The scroll speed can be set in a per-app context: my-overrides/community/imo-scoped-settings.py
    """

    # Continuous scrolling
    def foot_switch_top_held():
        # actions.user.mouse_scrolling("up") # From Andreas
        # actions.user.mouse_scroll_up_continuous() # From community
        # (can't scroll on VSCode unless you set by_lines=true on "scroll_continuous_helper")
        if not settings.get("user.reverse_footswitch_scroll"):
            actions.user.mouse_scroll_up_continuous()
        else:
            actions.user.mouse_scroll_down_continuous()

    def foot_switch_top_released():
        actions.user.mouse_scroll_stop()

    def foot_switch_center_held():
        if not settings.get("user.reverse_footswitch_scroll"):
            actions.user.mouse_scroll_down_continuous()
        else:
            actions.user.mouse_scroll_up_continuous()

    def foot_switch_center_released():
        actions.user.mouse_scroll_stop()

    # def foot_switch_center_double_click():
    #     actions.user.desktop_show()

    # Single step scrolling (with by_lines=True)
    def foot_switch_top_down():
        if not settings.get("user.reverse_footswitch_scroll"):
            actions.mouse_scroll(y=-1, by_lines=True)  # just 1 step
        else:
            actions.mouse_scroll(y=+1, by_lines=True)  # just 1 step

    def foot_switch_center_down():
        if not settings.get("user.reverse_footswitch_scroll"):
            actions.mouse_scroll(y=+1, by_lines=True)  # just 1 step
        else:
            actions.mouse_scroll(y=-1, by_lines=True)  # just 1 step

    # def foot_switch_top_down():
    #     # actions.user.mouse_scrolling("up") # From Andreas
    #     # actions.user.mouse_scroll_up_continuous() # From community (can't scroll on VSCode?)
    #     # TODO maybe try: from user.knausj_talon.code.mouse import start_cursor_scrolling, stop_scroll
    #     # https://wiki.gpunktschmitz.com/index.php/Talon
    #     # actions.mouse_scroll(y=-1,by_lines=True) # just 1 step
    #     actions.user.mouse_scroll_up_continuous()

    # Back/Close tab
    def foot_switch_left_up():
        """
        Do not try to trigger on down, it does not work since the keypress is merged
        More importantly, you don't know if it's held until it's released!
        """
        actions.user.go_back()  # Defined by tag.navigation, implementation depends
        # tag(): user.navigation

    def foot_switch_left_held():
        actions.user.tab_close_wrapper()

    def foot_switch_left_double_click():
        """
        Faster than holding... might be more practical to remap to something else?
        """
        # actions.user.tab_close_wrapper()
        # community/core/windows_and_tabs/window_snap_positions.talon-list
        # actions.user.snap_window(position="right", window=None)
        # sim = speech_system._sim(str("snap right"))
        speech_system.mimic("snap left")

    # Forward/app switch
    def foot_switch_right_up():
        """
        Do not try to trigger on down, it does not work since the keypress is merged
        More importantly, you don't know if it's held until it's released!
        """
        actions.user.go_forward()  # Defined by tag.navigation, implementation depends

    def foot_switch_right_held():
        actions.user.desktop_show()

    def foot_switch_right_double_click():
        """
        Faster than holding... might be more practical to remap to something else?
        """
        # community/core/windows_and_tabs/window_snap_positions.talon-list
        # actions.user.snap_window(position="right", window=None)
        # sim = speech_system._sim(str("snap right"))
        speech_system.mimic("snap right")


# Do undo/redo with left/right INSTEAD of back/forward" on these apps...
# ------------------------------------------------------------------------------------------
ctx_undo = Context()
ctx_undo.matches = r"""
app: vscode
app: Code
app: Com.github.xournalpp.xournalpp
app: jetbrains-pycharm
app: libreoffice
app: joplin
app: slack
app: Anki
app: journal
app: xournalpp
app: zotero
app: Preview
"""

# If you need to overwrite the edit.undo/edit.redo behaviour
# Option1 redefine them in their corresonding .py file
# Option2 redefine them all here

#        ctx = Context()
#        ctx.matches = r"""
#        app: offending app1
#        app: offending app2
#        """
#
#        @ctx.action_class("edit")
#        class EditActions:
#            def undo():
#                print("called")
#                actions.key("ctrl-z")
#            def redo():
#                actions.key("ctrl-y")


@ctx_undo.action_class("user")
class UndoRedoFootPedalBehaviour:
    """

    Overwrite the left/right footswitch behaviour to do undo/redo

    >>> # 'gnome_terminal' App definition
    >>> mod = Module()
    >>> mod.apps.gnome_terminal = r\"\"\"
    >>> os: linux
    >>> and app.exe: gnome-terminal-server
    >>> os: linux
    >>> and app.name: Gnome-terminal
    >>> os: linux
    >>> and app.name: Mate-terminal
    >>> \"\"\"

    >>> # New context that finds the app we just defined
    >>> ctx = Context()
    >>> ctx.matches = r\"\"\"
    >>> app: gnome_terminal
    >>> \"\"\"
    >>>
    >>> # overwrite linux/edit.py in that ctx
    >>> @ctx.action_class("edit")
    >>> class EditActions:
    >>>    def undo():
    >>>        actions.key("ctrl-z")
    >>>    def redo():
    >>>        actions.key("ctrl-z")

    """

    def foot_switch_left_up():
        """
        actions.edit.undo() and actions.edit.redo() require extra connections defined by action_class("edit")
        """
        # actions.key("ctrl-z")
        actions.edit.undo()

    def foot_switch_right_up():
        # actions.key("ctrl-y")
        actions.edit.redo()


# enable/disable eye-tracker...
# ------------------------------------------------------------------------------------------

ctx_eye_tracker = Context()
ctx_eye_tracker.matches = r"""
# tag: user.eye_tracker
# tag: user.eye_tracker_frozen
# mode: command
# mode: dictation
# mode: sleep
# ^^^^^^^^^ Has to be more specific than the default context...
app: matchNothing
"""


# def enable_tracker():
#     # https://github.com/AndreasArvidsson/andreas-talon/blob/main/core/mouse/eye_tracker.py#L43
#     actions.tracking.control_toggle(True)
#     if actions.tracking.control_enabled():
#         storage.set("tracking_control", "enabled")
#         ctx.tags = ["user.eye_tracker"]


# def disable_tracker():
#     actions.tracking.control_toggle(False)
#     storage.set("tracking_control", "disabled")
#     ctx.tags = []

TOGGLE_EYETRACKING = True
# True -> toggle on/off
# False -> hold to activate


@ctx_eye_tracker.action_class("user")
class FootswitchEyeTrackerActions:
    """
    Turning the eye-tracking on/off has a small delay...
    """

    def foot_switch_right_down():
        if TOGGLE_EYETRACKING:
            actions.tracking.control_toggle()
            return None
        actions.tracking.control_toggle(True)

    def foot_switch_right_up():
        if TOGGLE_EYETRACKING:
            return None
        actions.tracking.control_toggle(False)
        # actions.user.mouse_freeze_toggle()


# if enable is None:
#     enable = not actions.tracking.control_enabled()
# enabled = actions.tracking.control_enabled()
# actions.user.notify(f"Control mouse: {enabled}")


# Eye tracking
# track on:                   user.mouse_control_toggle(true)
# track off:                  user.mouse_control_toggle(false)
# tracking:                   user.mouse_control_toggle()
# track gaze:                 tracking.control_gaze_toggle(true)
# track head:                 tracking.control_gaze_toggle(false)
# track debug:                tracking.control_debug_toggle()
# track calibrate:            tracking.calibrate()

# # Cursor
# cursor center:              user.mouse_move_center_window()

# enable/disable microphone/talon?
# ------------------------------------------------------------------------------------------

ctx_eye_tracker = Context()
ctx_eye_tracker.matches = r"""
# tag: user.eye_tracker
# tag: user.eye_tracker_frozen
# mode: command
# mode: dictation
# mode: sleep
# ^^^^^^^^^ Has to be more specific than the default context...
# TODO  where should this be applied?
app: matchNothing
"""

TOGGLE_MUTE = True
# True -> toggle on/off
# False -> hold to activate


@ctx_eye_tracker.action_class("user")
class FootswitchMuteActions:
    """
    So far only enables/disables talon and does not mute
    That is probably application independent? (e.g. alt-m)
    """

    def foot_switch_right_down():
        if TOGGLE_MUTE:
            actions.speech.toggle()
            # actions.mode.toggle("sleep")
            return None
        actions.speech.enable()
        # actions.mode.disable("sleep")

    def foot_switch_right_up():
        if TOGGLE_MUTE:
            return None
        actions.speech.disable()
        # actions.mode.enable("sleep")
