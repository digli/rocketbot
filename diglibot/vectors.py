
class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Vector3(self.x - other.x,
                       self.y - other.y,
                       self.z - other.z)

    def __add__(self, other):
        return Vector3(self.x + other.x,
                       self.y + other.y,
                       self.z + other.z)

    def copy(self, other):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def normalize():
        # fancy algo
        pass

    @property
    def ground_coords(self):
        return (self.z, self.x)
