import argparse

def validarArgs():
    parser = argparse.ArgumentParser(description="ejemplo")
    parser.add_argument('-f1', action="store_true", help="llama a la función 1")
    parser.add_argument('-f2', action="store_true", help="llama a la función 2")
    args = parser.parse_args()
    return args


