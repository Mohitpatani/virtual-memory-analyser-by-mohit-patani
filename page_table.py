# page_table.py
class PageTable:
    def __init__(self, size: int):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size must be positive integer")
        self.size = size
        self.entries = [-1] * size

    def is_loaded(self, page_number: int) -> bool:
        return 0 <= page_number < self.size and self.entries[page_number] != -1

    def get_frame(self, page_number: int):
        if 0 <= page_number < self.size:
            frame = self.entries[page_number]
            return None if frame == -1 else frame
        raise IndexError("page out of range")

    def load_page(self, page_number: int, frame_number: int):
        if not isinstance(frame_number, int) or frame_number < 0:
            raise ValueError("frame_number must be non-negative int")
        if not (0 <= page_number < self.size):
            raise IndexError("page out of range")
        self.entries[page_number] = frame_number

    def unload_page(self, page_number: int):
        if not (0 <= page_number < self.size):
            raise IndexError("page out of range")
        self.entries[page_number] = -1

    def clear(self):
        self.entries = [-1] * self.size

    def get_entries(self):
        return [{"page": i, "frame": (None if f == -1 else f), "valid": f != -1} for i, f in enumerate(self.entries)]
