from ai.signals.adaptive_signal import (
    AdaptiveSignalController,
    SignalConfig,
    SignalState,
)


def test_green_respects_minimum_duration():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=5, max_green=20, yellow=3, all_red=1)
    )
    first = controller.reset(now=0)

    assert first.state == SignalState.GREEN
    assert first.direction == "NORTH"
    assert first.remaining_seconds == 5

    before_expiry = controller.update({"NORTH": 1, "EAST": 9}, now=4.9)
    assert before_expiry.state == SignalState.GREEN
    assert before_expiry.direction == "NORTH"
    assert before_expiry.remaining_seconds == 1


def test_green_changes_to_yellow_before_all_red():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=5, max_green=20, yellow=3, all_red=1)
    )
    controller.reset(now=0)

    yellow = controller.update(
        {"NORTH": 1, "EAST": 9, "SOUTH": 2, "WEST": 1},
        now=5,
    )
    assert yellow.state == SignalState.YELLOW
    assert yellow.direction == "NORTH"
    assert yellow.next_direction == "EAST"
    assert yellow.remaining_seconds == 3

    all_red = controller.update(
        {"NORTH": 1, "EAST": 9, "SOUTH": 2, "WEST": 1},
        now=8,
    )
    assert all_red.state == SignalState.ALL_RED
    assert all_red.remaining_seconds == 1


def test_all_red_clears_before_next_green():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=5, max_green=20, yellow=3, all_red=1)
    )
    controller.reset(now=0)

    green = controller.update(
        {"NORTH": 1, "EAST": 9, "SOUTH": 2, "WEST": 1},
        now=9,
    )
    assert green.state == SignalState.GREEN
    assert green.direction == "EAST"
    assert green.next_direction == "EAST"
    assert green.remaining_seconds == 20


def test_no_conflicting_green_directions():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=5, max_green=20, yellow=3, all_red=1)
    )
    controller.reset(now=0)

    for now in (0, 4, 5, 7, 8, 9, 14):
        snapshot = controller.update(
            {"NORTH": 2, "EAST": 10, "SOUTH": 4, "WEST": 1},
            now=now,
        )
        if snapshot.state == SignalState.GREEN:
            assert snapshot.direction in controller.DIRECTIONS
            assert snapshot.next_direction == snapshot.direction
