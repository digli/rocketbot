import time

JUMP_STARTING = 0
JUMP_BUFFERING = 1
JUMP_DODGING = 2
JUMP_FINISHED = 3
JUMP_TO_DODGE_DT = 0.08 # (seconds) __test this__
UPDATE_BUFFER = 1 / 60 # one frame should be enough right?


class DodgeTimer:
    def __init__(self, d0=JUMP_TO_DODGE_DT, d1=UPDATE_BUFFER, d2=UPDATE_BUFFER):
        self.start = time.time()
        self.d0 = d0
        self.d1 = d1
        self.d2 = d2
        self.first_buffer = None
        self.second_buffer = None
        self.state = JUMP_STARTING

    def update_state(self):
        now = time.time()

        if self.state == JUMP_STARTING:
            if now - self.start < self.d0:
                return self.state
            self.state = JUMP_BUFFERING

        if self.state == JUMP_BUFFERING:
            if self.first_buffer is None:
                self.first_buffer = now
            if now - self.first_buffer < self.d1:
                return self.state
            self.state = JUMP_DODGING

        if self.state == JUMP_DODGING:
            if self.second_buffer is None:
                self.second_buffer = now
            if now - self.second_buffer < self.d2:
                return self.state
            self.state = JUMP_FINISHED

        return self.state

    def jump_button(self):
        return (True, False, True, False)[self.state]

    def is_finished(self):
        return self.state == JUMP_FINISHED
