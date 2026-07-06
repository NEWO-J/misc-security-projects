import threading

class RingBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = bytearray(capacity)
        self.view = memoryview(self.buffer)
        self.head = 0
        self.tail = 0
        self.size = 0
        self.lock = threading.Lock()

    def write(self, data: bytes):
        data_len = len(data)
        if data_len == 0:
            return
        
        with self.lock:

            if self.size + data_len == self.capacity:
                raise OverflowError("Ring buffer is full!")
            
            if self.head + data_len > self.capacity:
                first_chunk_len = self.capacity - self.head
                self.buffer[self.head : self.capacity] = data[:first_chunk_len]

                second_chunk_len = data_len - first_chunk_len
                self.buffer[0 : second_chunk_len] = data[first_chunk_len:]
            else:
                # the data will fit without wrapping
                self.buffer[self.head : self.head + data_len] = data
            
            self.head = (self.head + data_len) % self.capacity
            self.size += data_len

    def get_readable_view(self):
        with self.lock:
            if self.size == 0:
                return self.view[0:0]

            if self.tail < self.head:
                return self.view[self.tail:self.head]
            
            return self.view[self.tail:self.capacity]


    def advance_tail(self, num_bytes: int):
        with self.lock:

            if num_bytes > self.size:
                raise ValueError("Cannot advance tail past available data.")
            self.tail = (self.tail + num_bytes) % self.capacity
            self.size -= num_bytes


