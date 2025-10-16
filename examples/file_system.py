from mcl import Board

with Board("COM4") as board:
    fs = board.fs

    files = fs.ls()
    print("Listing /")
    for file in files:
        print(file)

    fs.mkdir("test")
    fs.write_text("test/test.txt", "hi, hello!")
    print("Reading test/test.txt...")
    print(fs.read_text("test/test.txt"))

    print(fs.ls("test"))
