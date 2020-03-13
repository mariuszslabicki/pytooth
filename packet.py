class Packet(object):
    def __init__(self, src_id, window_id):
        self.src_id = src_id
        self.window_id = window_id