import sys


# Montis-MBP:tests monti$ python
# Python 2.7.10 (default, Jul 15 2017, 17:16:57)
# >>> print(2)
# 2
# >>> print 2
# 2
# >>> print(2, "hi")
# (2, 'hi')  # <- Ausgabe als Tupel
#
#
# Montis-MBP:tests monti$ python3
# Python 3.6.4 (default, Feb  9 2018, 19:09:41)
# >>> print(2, "hi")
# 2 hi  # <- Ausgabe als String
# >>> print((2, "hi"))
# (2, 'hi')  # <- Ausgabe als Tupel, weil uebergabe als Tupel


def is_python3():
    return sys.version_info >= (3,0)


def print_python_version():
    v = sys.version_info
    version_str = str(v[0]) + "." + str(v[1]) + "." + str(v[2])
    print(version_str)


def main():
    print_python_version()

    if is_python3():
        print("Python Version 3.x.x")
        import python3_stuff as p3s
        p3s.exec_python3_stuff()
    else:
        # Funktioniert nur, weil Python 2.x.x das als Tupel mit einem
        # Element interpretiert und dann einfach als String
        # ausgibt.
        print("Python Version 2.x.x")
        import python2_stuff as p2s
        p2s.exec_python2_stuff()


if __name__ == "__main__":
    main()
