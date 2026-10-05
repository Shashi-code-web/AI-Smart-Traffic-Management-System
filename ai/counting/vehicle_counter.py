from collections import Counter
from typing import Iterable

class VehicleCounter:
    def __init__(self) -> None:
        self.total_seen_ids: set[int] = set()
        self.class_counts: Counter[str] = Counter()

    def update(self, tracked_objects: Iterable[tuple[int, str]]) -> None:
        for track_id, label in tracked_objects:
            if track_id not in self.total_seen_ids:
                self.total_seen_ids.add(track_id)
                self.class_counts[label] += 1

    @property
    def total(self) -> int:
        return len(self.total_seen_ids)

    def snapshot(self) -> dict[str, int]:
        return dict(self.class_counts)
