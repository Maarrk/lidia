import argparse


def main():
    parser = argparse.ArgumentParser(
        prog='lidia',
        description='serve an aircraft instruments panel as a web page')
    parser.parse_args()
    print('Lidia running')


if __name__ == '__main__':
    main()
