# replacement_algo.py
from collections import deque, OrderedDict
from typing import Optional, List

class FIFOPageReplacement:
    def __init__(self, frame_count: int):
        self.frame_count = frame_count
        self.queue = deque()

    def replace(self, page_number: int) -> Optional[int]:
        if page_number in self.queue:
            return None
        evicted = None
        if len(self.queue) >= self.frame_count:
            evicted = self.queue.popleft()
        self.queue.append(page_number)
        return evicted

    def access(self, page_number: int):
        pass

    def get_frames(self) -> List[Optional[int]]:
        frames = list(self.queue)
        if len(frames) < self.frame_count:
            frames += [None] * (self.frame_count - len(frames))
        return frames

    def reset(self):
        self.queue.clear()

class LRUPageReplacement:
    def __init__(self, frame_count: int):
        self.frame_count = frame_count
        self.od = OrderedDict()

    def replace(self, page_number: int) -> Optional[int]:
        if page_number in self.od:
            return None
        evicted = None
        if len(self.od) >= self.frame_count:
            evicted, _ = self.od.popitem(last=False)
        self.od[page_number] = True
        return evicted

    def access(self, page_number: int):
        if page_number in self.od:
            self.od.move_to_end(page_number, last=True)

    def get_frames(self) -> List[Optional[int]]:
        frames = list(self.od.keys())
        if len(frames) < self.frame_count:
            frames += [None] * (self.frame_count - len(frames))
        return frames

    def reset(self):
        self.od.clear()

class MRUPageReplacement:
    def __init__(self, frame_count: int):
        self.frame_count = frame_count
        self.od = OrderedDict()

    def replace(self, page_number: int) -> Optional[int]:
        if page_number in self.od:
            return None
        evicted = None
        if len(self.od) >= self.frame_count:
            evicted, _ = self.od.popitem(last=True)
        self.od[page_number] = True
        return evicted

    def access(self, page_number: int):
        if page_number in self.od:
            self.od.move_to_end(page_number, last=True)

    def get_frames(self) -> List[Optional[int]]:
        frames = list(self.od.keys())
        if len(frames) < self.frame_count:
            frames += [None] * (self.frame_count - len(frames))
        return frames

    def reset(self):
        self.od.clear()

class OptimalPageReplacement:
    def __init__(self, frame_count: int, reference_string: Optional[List[int]] = None):
        self.frame_count = frame_count
        self.reference_string = reference_string or []
        self.frames: List[int] = []
        self.current_index = 0

    def replace(self, page_number: int) -> Optional[int]:
        if page_number in self.frames:
            self.current_index += 1
            return None
        evicted = None
        if len(self.frames) < self.frame_count:
            self.frames.append(page_number)
        else:
            future = self.reference_string[self.current_index + 1:] if self.current_index + 1 <= len(self.reference_string) else []
            next_idxs = []
            for f in self.frames:
                try:
                    idx = future.index(f)
                except ValueError:
                    idx = float("inf")
                next_idxs.append(idx)
            victim_pos = int(max(range(len(next_idxs)), key=lambda i: next_idxs[i]))
            evicted = self.frames[victim_pos]
            self.frames[victim_pos] = page_number
        self.current_index += 1
        return evicted

    def access(self, page_number: int):
        self.current_index += 1

    def get_frames(self) -> List[Optional[int]]:
        frames = list(self.frames)
        if len(frames) < self.frame_count:
            frames += [None] * (self.frame_count - len(frames))
        return frames

    def reset(self):
        self.frames.clear()
        self.current_index = 0

def get_algorithm(name: str, frame_count: int, reference_string: Optional[List[int]] = None):
    name = name.upper()
    if name == "FIFO":
        return FIFOPageReplacement(frame_count)
    elif name == "LRU":
        return LRUPageReplacement(frame_count)
    elif name == "MRU":
        return MRUPageReplacement(frame_count)
    elif name == "OPTIMAL":
        return OptimalPageReplacement(frame_count, reference_string)
    else:
        raise ValueError(f"Unknown replacement algorithm: {name}")
