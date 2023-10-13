from validarArgumentos import validarArgs

def funcion1():
    print("funcion1")


def function2():
    print("function2")

if __name__ == "__main__":
    args = validarArgs()

    if args.f1:
        funcion1()
    elif args.f2:
        function2()
    else:
        print("no se llamo nada")

