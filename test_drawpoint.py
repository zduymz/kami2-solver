import unittest
import solver


class TestDrawPoint(unittest.TestCase):

    def setUp(self):
        self.T = solver.create_point(256, 128)

    def test_first_row(self):
        assert self.T[0].pos == ((0, 0), (0, 32), (64, 0))
        assert self.T[1].pos == ((64, 0), (128, 0), (128, 32))
        assert self.T[2].pos == ((128, 0), (128, 32), (192, 0))
        assert self.T[3].pos == ((192, 0), (256, 0), (256, 32))

    def test_second_row(self):
        assert self.T[4].pos == ((0, 32), (64, 0), (64, 64))
        assert self.T[5].pos == ((64, 0), (64, 64), (128, 32))
        assert self.T[6].pos == ((128, 32), (192, 0), (192, 64))
        assert self.T[7].pos == ((192, 0), (192, 64), (256, 32))

    def test_third_row(self):
        assert self.T[8].pos == ((0, 32), (0, 96), (64, 64))
        assert self.T[9].pos == ((64, 64), (128, 32), (128, 96))
        assert self.T[10].pos == ((128, 32), (128, 96), (192, 64))
        assert self.T[11].pos == ((192, 64), (256, 32), (256, 96))

    def test_fourth_row(self):
        assert self.T[12].pos == ((0, 96), (64, 64), (64, 128))
        assert self.T[13].pos == ((64, 64), (64, 128), (128, 96))
        assert self.T[14].pos == ((128, 96), (192, 64), (192, 128))
        assert self.T[15].pos == ((192, 64), (192, 128), (256, 96))

    def test_last_row(self):
        assert self.T[16].pos == ((0, 96), (0, 128), (64, 128))
        assert self.T[17].pos == ((64, 128), (128, 96), (128, 128))
        assert self.T[18].pos == ((128, 96), (128, 128), (192, 128))
        assert self.T[19].pos == ((192, 128), (256, 96), (256, 128))

if __name__ == '__main__':
    unittest.main()
