class VersionInfo:
    major = 0
    minor = 0
    micro = 6

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def __str__(self):
        return "{}.{}.{}".format(self.major, self.minor, self.micro)

version = VersionInfo()

class potatoscript:

    class missingFunc(Exception):

        def __init__(self, name):
            self.name = name

        def __str__(self):
            return "Function '{}' is missing from function library".format(self.name)

    class _var:

        def __init__(self, name):
            self.name = name

        def __call__(self, ps):
            if self.name in ps._l:
                return ps._l[self.name]

            if self.name in ps._g:
                return ps._g[self.name]

            raise NameError("Name '{}' not in any scope".format(self.name))

    class _math:

        def __init__(self, source):
            import re
            self.source = '\n' + re.sub(r"read\s*?(\s*?)", '0', source) + '\n'

        def __call__(self, ps):
            import subprocess
            import re

            source = re.sub(r"(\s)(?P<name>[_a-zA-Z][_a-zA-Z0-9]*)(\s)", r"\g<1>{\g<name>}\g<3>", self.source).format(**ps._g, **ps._l)

            o = subprocess.run(['./bc', '-l'], input=source, check=True, text=True, capture_output=True).stdout.strip()

            try:
                v = float(o)
                try:
                    i = int(o)
                    return i
                except ValueError:
                    return v
            except ValueError:
                return o


    class stdlib:

        @staticmethod
        def set_(ps, name, value):
            import re
            if re.fullmatch(r"[_a-zA-Z][_a-zA-Z0-9]*", name):
                ps._l[name] = value
            else:
                raise NameError("Not a valid variable name")

        @staticmethod
        def del_(ps, name):
            del ps._l[name]

        @staticmethod
        def return_(ps, value):
            ps.returnval = value

        @staticmethod
        def println_(ps, output):
            ps.output += str(output) + '\n'

        @staticmethod
        def print_(ps, output):
            """
            print output

            Prints output to output buffer
            """
            ps.output += str(output)

        @staticmethod
        def help_(ps, name):
            """
            help 'name'

            Shows documentation of defined functions.
            """
            from inspect import cleandoc

            doc = ps._func(name).__doc__
            if doc:
                doc = cleandoc(doc)
            else:
                doc = 'No documentation'

            ps.output += '---------------\n' + doc + '\n---------------'


        @classmethod
        def __call__(cls, _):
            return {
                'set' : cls.set_,
                'del' : cls.del_,
                'return' : cls.return_,
                'print' : cls.print_,
                'println' : cls.println_,
                'help' : cls.help_,
            }

    def __init__(self, source="",  var=None, stdout=False, *, deflib=stdlib(), comp=True):
        if var:
            self._g = {**var}
        else:
            self._g = {**deflib(self)}

        self._l = {}
        self.returnval = None
        self.source = source
        self.output = ""
        self.exec = []

        if comp:
            self.comp()

    def __call__(self):
        self._l = {}

        for ins in self.exec:

            for i, instr in enumerate(ins[1]):
                if callable(instr):
                    ins[1][i] = instr(self)

            ins[0](self, *ins[1])

            if self.returnval != None:
                return self.returnval

        return self.returnval

    def comp(self):
        import re

        source, maths = self._mathparse(self.source)
        source = source.split('\n')

        for exp in source:
            args = []
            s = exp.split()

            if not s:
                continue

            func = s[0]

            strings = re.finditer(r"[\"'](.+?)[\"']", exp + ' ')
            strless = re.sub(r"[\"'].+?[\"']", '{}', exp + ' ')

            for arg in strless.split()[1:]:
                if arg == '{}':
                    string = next(strings).group(1)
                    fi = 0
                    while True:
                        fi = string.find('$()', fi)
                        if fi == -1:
                            break
                        fi += 2

                        string = string.replace('$()', '$(' + next(maths) + ')', 1)

                    args.append(string)
                    continue

                if arg == '$()':
                    args.append(self._math(next(maths)))
                    continue

                try:
                    v = float(arg)
                    try:
                        i = int(arg)
                        args.append(i)
                    except ValueError:
                        args.append(v)
                    finally:
                        continue

                except ValueError:
                    pass

                if re.fullmatch(r"[_a-zA-Z][_a-zA-Z0-9]*", arg):
                    args.append(self._var(arg))
                    continue

                raise ValueError("Cannot determine the type of '{}'".format(arg))


            if func in self._funcs():
                self.exec.append([self._funcs()[func], args])
            else:
                raise self.missingFunc(func)


    def _getvar(self, name):
        if name in self._l:
            return self._l[name]

        if name in self._g:
            return self._g[name]

        raise NameError("Name '{}' not in any scope".format(name))

    def _func(self, name):
        if name in self._funcs():
            return self._funcs()[name]
        else:
            raise KeyError("Function '{}' not in any scope".format(name))

    def _funcs(self):
        test = lambda v : callable(v[1])
        return {**dict(filter(test, self._g.items())), **dict(filter(test, self._l.items()))}


    @staticmethod
    def _mathparse(source):
        maths = []
        start = 0
        while start < len(source):
            if source[start:start+2] == '$(':
                am = 1
                end = start + 2
                while am > 0:
                    if source[end] == '(':
                        am += 1
                    elif source[end] == ')':
                        am -= 1

                    end += 1

                else:
                    maths.append(source[start+2:end-1])
                    source = source[:start+2] + source[end-1:]

                    start += 1

            start += 1

        def mathsiter(maths):
            for value in maths:
                yield value

        return source, mathsiter(maths)


if __name__ == '__main__':
    testp = potatoscript("""
set 'a' $(5 * (8 + 10))
set 'b' $(8 + 9 + a * 100)
help 'help'
return 'Now that is $($(1 + 1) 1 + 1) lot of damage'
""")

    print(testp())
    print('-' * 20)
    print(testp.output)
