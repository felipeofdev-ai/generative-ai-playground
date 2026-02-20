from dataclasses import dataclass


@dataclass
class BackpressureState:
    queue_depth: int
    threshold: int


class BackpressureController:
    def __init__(self, threshold: int = 1000):
        self.threshold = threshold

    def should_reject(self, queue_depth: int) -> bool:
        return queue_depth > self.threshold

    def scaling_signal(self, queue_depth: int) -> str:
        if queue_depth > int(self.threshold * 1.5):
            return "scale_up_urgent"
        if queue_depth > self.threshold:
            return "scale_up"
        return "stable"
