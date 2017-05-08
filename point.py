class Point(object):

    def __init__(self, x1, x2, y1, y2,
                 value=None, delta=0.0,
                 is_first_row=None, is_last_row=None):

        self.color = value
        if is_first_row:
            self.pos_color = (x1 + (x2 - x1) / 2 - 2, y1 +
                              (y2 - y1) / 2 + int(delta) - 15)
            if (x2 / 64) % 2 == 0:
                self.pos = (x1, y1), (x2, y1), (x2, y2)
            else:
                self.pos = (x1, y1), (x1, y2), (x2, y1)
        elif is_last_row:
            self.pos_color = (x1 + (x2 - x1) / 2 - 2, y1 +
                              (y2 - y1) / 2 + int(delta) + 15)
            if (x2 / 64) % 2 == 0:
                self.pos = (x1, y2), (x2, y1), (x2, y2)
            else:
                self.pos = (x1, y1), (x1, y2), (x2, y2)
        else:
            self.pos_color = (x1 + (x2 - x1) / 2, y1 +
                              (y2 - y1) / 2 + int(delta))
            if (y2 / 36) % 2 == 0:
                if (x2 / 64) % 2 == 0:
                    self.pos = (x1, y1), (x1, y2), (x2, y1 + 36)
                else:
                    self.pos = (x1, y1 + 36), (x2, y1), (x2, y2)
            else:
                if (x2 / 64) % 2 == 0:
                    self.pos = (x1, y1 + 36), (x2, y1), (x2, y2)
                else:
                    self.pos = (x1, y1), (x1, y2), (x2, y1 + 36)
        self.neighbors = []
        self.group = None


class Group(object):

    def __init__(self, id):
        self.id = id
        self.points = []

    def __repr__(self):
        return str(self.id)

    def prepare_for_graph(self):
        self.color = self.get_color()
        self.neighbors = self.get_group_neighbors()

    def weight(self):
        return len(self.neighbors)

    def get_color(self):
        if self.points:
            return self.points[0].color
        else:
            return None

    def set_color(self, color):
        for p in self.points:
            p.color = color

    def get_neighbors_color(self):
        gc = set()
        for p in self.points:
            for n in p.neighbors:
                if n.group == self.id:
                    continue
                gc.add(n.color)
        return list(gc)

    def get_group_neighbors(self):
        gn = set()
        for p in self.points:
            for n in p.neighbors:
                if n.group == self.id:
                    continue
                gn.add(n.group)
        # remove my own group id
        return list(gn)

    def replace_neighbor(self, old, new):
        for n in self.neighbors:
            if old == n:
                self.neighbors.remove(old)
                if self.id != new:
                    self.neighbors.append(new)
                    self.neighbors = list(set(self.neighbors))

    def set_group_id(self, id):
        self.id = id
        for p in self.points:
            self.group = id
