from hex_data import HexData


class TestHexEditor:

    def test_data_change(self):
        data = HexData("test.txt")
        assert(data.check_change(0, 0, "aa") is True)

    def test_data_long_change(self):
        data = HexData("test.txt")
        assert(data.check_change(0, 0, "aaaaa") is False)

    def test_data_bad_change(self):
        data = HexData("test.txt")
        assert(data.check_change(0, 0, "fashfbaksj") is False)

    def test_data_change_last_row(self):
        data = HexData("test.txt")
        assert(data.check_change(-1, 15, "aa") is True)

    def test_encoding(self):
        data = HexData("test.txt")
        assert(data.check_change_encoded_text(0, "A.ab" * 4) is True)

    def test_bad_encoding(self):
        data = HexData("test.txt")
        assert(data.check_change_encoded_text(0, "a" * 24) is False)

    def test_add_row(self):
        data = HexData("test.txt")
        rows = len(data.data)
        data.add_row()
        assert(len(data.data) - rows == 1)

    def test_delete_row(self):
        data = HexData("test.txt")
        rows = len(data.data)
        data.delete_row()
        assert(len(data.data) - rows == -1)

    def test_save(self):
        data = HexData("test.txt")
        length = len(data.data)
        data.save()
        data = HexData("test.txt")
        assert(len(data.data) == length)
