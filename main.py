#!/usr/bin/python3.6

import subprocess


def main():
    subprocess.Popen(
        ['./projecteuler/app.py',]
    )
    subprocess.Popen(
        ['./tasks/app.py',]
    )
    subprocess.Popen(
        ['./users/app.py',]
    )

    while True:
        pass


if __name__ == '__main__':
    main()
