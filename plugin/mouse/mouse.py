from talon import Context, Module, actions, ctrl, settings, ui

mod = Module()
ctx = Context()

mod.list(
    "mouse_button",
    desc="List of mouse button words to mouse_click index parameter",
)
mod.setting(
    "mouse_enable_pop_click",
    type=int,
    default=0,
    desc="Pop noise clicks left mouse button. 0 = off, 1 = on with eyetracker but not with zoom mouse mode, 2 = on but not with zoom mouse mode",
)
setting_mouse_enable_pop_drag = mod.setting(
    "mouse_enable_pop_drag",
    type=int,
    default=0,
    desc="Enable pop to drag when control mouse is enabled. mouse_enable_pop_click has precedence over this",
)

mod.setting(
    "mouse_enable_pop_stops_scroll",
    type=bool,
    default=False,
    desc="When enabled, pop stops continuous scroll modes (wheel upper/downer/gaze)",
)
mod.setting(
    "mouse_enable_pop_stops_drag",
    type=bool,
    default=False,
    desc="When enabled, pop stops mouse drag",
)
mod.setting(
    "mouse_wake_hides_cursor",
    type=bool,
    default=False,
    desc="When enabled, mouse wake will hide the cursor. mouse_wake enables zoom mouse.",
)


@mod.action_class
class Actions:
    def zoom_close():
        """Closes an in-progress zoom. Talon will move the cursor position but not click."""
        actions.user.deprecate_action(
            "2024-12-26",
            "user.zoom_close",
            "tracking.zoom_cancel",
        )
        actions.tracking.zoom_cancel()

    def mouse_wake():
        """Enable control mouse, zoom mouse, and disables cursor"""
        actions.tracking.control_zoom_toggle(True)

        if settings.get("user.mouse_wake_hides_cursor"):
            actions.user.mouse_cursor_hide()

    def mouse_drag(button: int):
        """Press and hold/release a specific mouse button for dragging"""
        # Clear any existing drags
        actions.user.mouse_drag_end()

        # Start drag
        actions.mouse_drag(button)

    def mouse_swipe(horizontal_change: int, vertical_change: int):
        """Click and drag the cursor a relative distance from the current position"""
        ctrl.mouse_click(button=0, down=True)
        actions.mouse_move(actions.mouse_x() + horizontal_change, actions.mouse_y() + vertical_change)
        actions.sleep("20ms")
        actions.mouse_release(0)

    def mouse_drag_end() -> bool:
        """Releases any held mouse buttons"""
        buttons = ctrl.mouse_buttons_down()
        if buttons:
            for button in buttons:
                actions.mouse_release(button)
            return True
        return False

    def mouse_drag_toggle(button: int):
        """If the button is held down, release the button, else start dragging"""
        if button in ctrl.mouse_buttons_down():
            actions.mouse_release(button)
        else:
            actions.mouse_drag(button)

    def mouse_sleep():
        """Disables control mouse, zoom mouse, and re-enables cursor"""
        actions.tracking.control_zoom_toggle(False)
        actions.tracking.control_toggle(False)
        actions.tracking.control1_toggle(False)

        actions.user.mouse_cursor_show()
        actions.user.mouse_scroll_stop()
        actions.user.mouse_drag_end()

    def copy_mouse_position():
        """Copy the current mouse position coordinates"""
        x, y = actions.mouse_x(), actions.mouse_y()
        actions.clip.set_text(f"{x}, {y}")

    def mouse_move_center_active_window():
        """Move the mouse cursor to the center of the currently active window"""
        rect = ui.active_window().rect
        actions.mouse_move(rect.center.x, rect.center.y)

last_pop_time = False
single_click = False

def on_pop(active):
    if settings.get("user.mouse_enable_pop_stops_scroll") >= 1 and (gaze_job or scroll_job):
        stop_scroll()
    elif (
        not eye_zoom_mouse.zoom_mouse.enabled
    ):
        if settings.get("user.mouse_enable_pop_stops_scroll") >= 1:
            if ctrl.mouse_buttons_down():
                self.mouse_drag_end()
            else:
                ctrl.mouse_click(button=0, hold=16000)
        elif setting_mouse_enable_pop_drag.get() >= 1:
            global last_pop_time, single_click
            current_time = time.time()
            print(f"time difference: {current_time - last_pop_time}")
            if last_pop_time and current_time - last_pop_time > .2:
                single_click = True
                cron.after("200ms", pop_drag_handler)
            else:
                single_click = False
            last_pop_time = current_time

def pop_drag_handler():
    if single_click:
        ctrl.mouse_click(button=0, hold=16000)
    else:
        ctrl.mouse_click(button=0, down=False, up=True)
        ctrl.mouse_click(button=0, down=True, up=False)


# TODO should I keep this or replace it with the new stuff?
# noise.register("pop", on_pop)

@ctx.action_class("user")
class UserActions:
    def noise_trigger_pop():
        dont_click = False

        # Allow pop to stop drag
        if settings.get("user.mouse_enable_pop_stops_drag"):
            if actions.user.mouse_drag_end():
                dont_click = True

        # Allow pop to stop scroll
        if settings.get("user.mouse_enable_pop_stops_scroll"):
            if actions.user.mouse_scroll_stop():
                dont_click = True

        if dont_click:
            return

        # Otherwise respect the mouse_enable_pop_click setting
        setting_val = settings.get("user.mouse_enable_pop_click")

        is_using_eye_tracker = (
            actions.tracking.control_zoom_enabled()
            or actions.tracking.control_enabled()
            or actions.tracking.control1_enabled()
        )

        should_click = (
            setting_val == 2 and not actions.tracking.control_zoom_enabled()
        ) or (
            setting_val == 1
            and is_using_eye_tracker
            and not actions.tracking.control_zoom_enabled()
        )

        if should_click:
            ctrl.mouse_click(button=0, hold=16000)
