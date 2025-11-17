# process.py
class Process:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.page_sequence = []

    def simulate(self, sequence, reset_before=False, verbose=False):
        if reset_before and hasattr(self.memory_manager, "reset"):
            self.memory_manager.reset()
        self.page_sequence = list(sequence)
        faults = 0
        for p in self.page_sequence:
            state = self.memory_manager.access_page(int(p))
            if state.get("last_fault"):
                faults += 1
        return faults
