class HexData:

    def __init__(self, path):
        self.path = path
        self.data = []
        self.encoding = []
        self.alphabet = "0123456789abcdef"
        self.read_data()
        self.decode_data_in_ascii()
        self.changed_cells = set()

    def read_data(self):
        data = ""
        with open(self.path, "rb") as f:
            data = f.read()
        row_count = len(data) // 16 + 1
        self.data = [["00" for y in range(16)] for x in range(row_count)]
        self.data[-1] = ["00" for x in range(len(data) % 16)]
        for i in range(len(data)):
            item = hex(data[i]).split("x")[1]
            if len(item) < 2:
                item = "0" + item
            self.data[i // 16][i % 16] = item

    def check_change(self, x, y, text):
        if not (len(text) == 2 and text[0] in self.alphabet and text[1] in self.alphabet):
            return False
        if len(self.data[x]) - 1 < y:
            self.fill_row(x, y)
        if text != self.data[x][y]:
            self.data[x][y] = text
            self.update_encoding(x)
            self.changed_cells.add((x, y))
            return True
        return False

    def decode_data_in_ascii(self):
        self.encoding = ["" for x in range(len(self.data))]
        text = ""
        for s in range(len(self.data)):
            for ch in self.data[s]:
                if int(ch, 16) < 32:
                    symb = "."
                else:
                    symb = bytearray.fromhex(ch).decode(encoding="ansi")
                text += symb
            self.encoding[s] = text
            text = ""

    def update_encoding(self, row):
        text = ""
        for ch in self.data[row]:
            if int(ch, 16) < 32:
                symb = "."
            else:
                symb = bytearray.fromhex(ch).decode(encoding="ansi")
            text += symb
        self.encoding[row] = text

    def check_change_encoded_text(self, row, text):
        if len(self.encoding[row]) < len(text) < 16:
            self.fill_row(row, len(text) - 1)
            self.update_encoding(row)
        if len(text) == len(self.encoding[row]):
            for x in range(len(self.encoding[row])):
                if int.from_bytes(text[x].encode("ansi"), byteorder="little") > 255:
                    return False
            for x in range(len(self.encoding[row])):
                if text[x] == ".":
                    if int(self.data[row][x], 16) > 31:
                        self.data[row][x] = hex(int.from_bytes(text[x].encode("ansi"), byteorder="little"))[2:].zfill(2)
                    else:
                        continue
                else:
                    self.data[row][x] = hex(int.from_bytes(text[x].encode("ansi"), byteorder="little"))[2:].zfill(2)
            self.update_encoding(row)
            return True
        return False

    def save(self):
        with open(self.path, "bw") as f:
            for row in self.data:
                for item in row:
                    f.write(bytes.fromhex(item))

    def add_row(self):
        self.fill_row(-1, 15)
        self.update_encoding(-1)
        self.data.append([])
        self.encoding.append("")

    def delete_row(self):
        self.data.remove(self.data[-1])
        self.encoding.remove(self.encoding[-1])

    def fill_row(self, row, length):
        while len(self.data[row]) - 1 < length:
            self.data[row].append("00")
