# memory_manager.py
from replacement_algo import get_algorithm
from page_table import PageTable
from config import PAGE_TABLE_SIZE

class MemoryManager:
    def __init__(self, algorithm_name="FIFO", frame_count=4, reference_string=None):
        # allow dynamic frame_count; page table size is fixed from config or can be adjusted externally
        self.page_table = PageTable(PAGE_TABLE_SIZE)
        self.frame_count = int(frame_count)
        self.algorithm_name = str(algorithm_name).upper()
        self.replacement = get_algorithm(self.algorithm_name, self.frame_count, reference_string)

        self.frame_map = {}   # page -> frame index
        self.last_fault = False
        self.total_accesses = 0
        self.total_faults = 0

    def set_algorithm(self, algorithm_name, frame_count=None, reference_string=None):
        if frame_count is not None:
            self.frame_count = int(frame_count)
        self.algorithm_name = str(algorithm_name).upper()
        self.replacement = get_algorithm(self.algorithm_name, self.frame_count, reference_string)
        self.frame_map.clear()
        self.page_table.clear()
        self.last_fault = False
        self.total_accesses = 0
        self.total_faults = 0

    def reset(self):
        self.frame_map.clear()
        self.page_table.clear()
        if hasattr(self.replacement, "reset"):
            try:
                self.replacement.reset()
            except Exception:
                pass
        self.last_fault = False
        self.total_accesses = 0
        self.total_faults = 0

    def _validate_page(self, page_number):
        if not isinstance(page_number, int):
            raise ValueError("page must be integer")
        if page_number < 0 or page_number >= self.page_table.size:
            raise ValueError(f"page {page_number} out of range (0..{self.page_table.size - 1})")

    def access_page(self, page_number):
        self._validate_page(page_number)
        self.total_accesses += 1
        self.last_fault = False

        if self.page_table.is_loaded(page_number):
            # inform replacement policy about access (LRU/MRU)
            if hasattr(self.replacement, "access"):
                try:
                    self.replacement.access(page_number)
                except Exception:
                    pass
            return self.get_state()

        # miss
        self.last_fault = True
        self.total_faults += 1

        evicted = self.replacement.replace(page_number)  # returns evicted page or None

        # snapshot frames after replacement and normalize length
        frames = list(self.replacement.get_frames())
        if len(frames) < self.frame_count:
            frames = frames + [None] * (self.frame_count - len(frames))
        elif len(frames) > self.frame_count:
            frames = frames[:self.frame_count]

        # unload evicted pages (explicit + inferred)
        evicted_pages = []
        if evicted is not None:
            if isinstance(evicted, (list, tuple, set)):
                evicted_pages.extend(evicted)
            else:
                evicted_pages.append(evicted)
        prev_pages = set(self.frame_map.keys())
        current_pages = set([p for p in frames if p is not None])
        inferred = list(prev_pages - current_pages)
        for p in inferred:
            if p not in evicted_pages:
                evicted_pages.append(p)
        for p in evicted_pages:
            if p in self.frame_map:
                try:
                    self.page_table.unload_page(p)
                except Exception:
                    pass
                del self.frame_map[p]

        # set mapping for new page
        try:
            frame_number = frames.index(page_number)
        except ValueError:
            raise RuntimeError(f"replacement policy didn't place page {page_number} into frames: {frames}")

        self.page_table.load_page(page_number, frame_number)
        self.frame_map[page_number] = frame_number

        return self.get_state()

    def get_state(self):
        frames = list(self.replacement.get_frames())
        if len(frames) < self.frame_count:
            frames = frames + [None] * (self.frame_count - len(frames))
        elif len(frames) > self.frame_count:
            frames = frames[:self.frame_count]

        # rebuild frame_map
        self.frame_map = {}
        for idx, pg in enumerate(frames):
            if pg is not None:
                self.frame_map[pg] = idx

        page_table_state = {i: 1 if self.page_table.is_loaded(i) else 0 for i in range(self.page_table.size)}
        frame_occupancy = [1 if frames[i] is not None else 0 for i in range(self.frame_count)]

        hit_rate = 0.0
        if self.total_accesses > 0:
            hit_rate = ((self.total_accesses - self.total_faults) / self.total_accesses) * 100

        return {
            "algorithm": self.algorithm_name,
            "page_table": page_table_state,
            "frames": frames,
            "frame_occupancy": frame_occupancy,
            "last_fault": bool(self.last_fault),
            "total_accesses": int(self.total_accesses),
            "total_faults": int(self.total_faults),
            "hit_rate": round(hit_rate, 2),
            "frame_count": self.frame_count
        }
