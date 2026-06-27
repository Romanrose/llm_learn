from execute_util import text

def compute(a: int):  # @inspect a
    return a + 1

def main():
    # what
    x = 4  # @inspect x
    y = 5  # @inspect y
    z = compute(x)  # @inspect z
    text("Hello $x^2$")

if __name__ == "__main__":
    main()
