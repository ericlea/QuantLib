"""
 Copyright (C) 2000-2001 QuantLib Group

 This file is part of QuantLib.
 QuantLib is a C++ open source library for financial quantitative
 analysts and developers --- http://quantlib.sourceforge.net/

 QuantLib is free software and you are allowed to use, copy, modify, merge,
 publish, distribute, and/or sell copies of it under the conditions stated
 in the QuantLib License.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 or FITNESS FOR A PARTICULAR PURPOSE. See the license for more details.

 You should have received a copy of the license along with this file;
 if not, contact ferdinando@ametrano.net
 The license is also available at http://quantlib.sourceforge.net/LICENSE.TXT

 The members of the QuantLib Group are listed in the Authors.txt file, also
 available at http://quantlib.sourceforge.net/Authors.txt
"""

"""
    $Id$
    $Source$
    $Log$
    Revision 1.11  2001/04/20 15:34:27  marmar
    Compiling options changed

    Revision 1.10  2001/04/20 13:45:14  nando
    minor changes

"""

import sys
sys.path.append("./Tests")

from distutils.core import setup, Extension
from distutils.cmd import Command
from distutils import sysconfig
import QuantLibSuite

if sys.platform == 'win32':
    import win32api
    quantLibInstallDirectory = win32api.GetEnvironmentVariable('QL_DIR')
    if len(quantLibInstallDirectory) == 0:
        raise('Please set environment variable "QL_DIR" to installation directory of QuantLib')
    include_dirs = [quantLibInstallDirectory + "\\Include"]
    library_dirs = [quantLibInstallDirectory + '\\lib\\win32\\VisualStudio']
    extra_compile_args = ['/Fp"..\Release\PyQuantLib.pch"',
                          '/YX',
                          '/Fd"..\Release"',
                          '/FD']
    extra_link_args = ['/subsystem:windows',
                       '/pdb:"..\Release\QuantLibc.pdb"',
                       '/machine:I386']
    define_macros = [('WIN32', None),
                     ('NDEBUG', None),
                     ('_WINDOWS', None)]
else:
    include_dirs = ["/usr/local/include"]
    library_dirs = None
    extra_compile_args = None
    extra_link_args = None
    define_macros = None
    # changes the compiler from gcc to g++
    save_init_posix = sysconfig._init_posix
    def my_init_posix():
        print 'my_init_posix: changing gcc to g++'
        save_init_posix()
        g = sysconfig._config_vars
        g['CC'] = 'g++'
        g['LDSHARED'] = 'g++ -shared'
    sysconfig._init_posix = my_init_posix

class test(Command):
    # Original version of this class posted
    # by Berthold H�llmann to distutils-sig@python.org
    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),
        ('test-prefix=', None,
         "prefix to the testcase filename"),
        ('test-suffixes=', None,
         "a list of suffixes used to generate names the of the testcases")
        ]

    def initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user or client)
        self.test_dir = 'Tests'
        self.test_prefix = 'QuantLibSuite'
        self.test_suffixes = None

    # initialize_options()

    def finalize_options(self):
        import os
        if self.test_suffixes is None:
            self.test_suffixes = []
            pref_len = len(self.test_prefix)
            for file in os.listdir(self.test_dir):
                if (file[-3:] == ".py" and
                    file[:pref_len]==self.test_prefix):
                    self.test_suffixes.append(file[pref_len:-3])

        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib

    # finalize_options()


    def run(self):
        import sys
        # Invoke the 'build' command to "build" pure Python modules
        # (ie. copy 'em into the build tree)
        self.run_command('build')

        # remember old sys.path to restore it afterwards
        old_path = sys.path[:]

        # extend sys.path
        sys.path.insert(0, self.build_purelib)
        sys.path.insert(0, self.build_platlib)
        sys.path.insert(0, self.test_dir)

        # build include path for test

        for case in self.test_suffixes:
            TEST = __import__(self.test_prefix+case,
                              globals(), locals(),
                              [''])
            try:
                tested_modules = TEST.tested_modules
            except AttributeError:
                tested_modules = None
            else:
                from code_coverage import Coverage
                coverage = Coverage(modules=tested_modules)
                sys.settrace(coverage.trace)

            TEST.test()

            if tested_modules is not None:
                # reload tested modules to get coverage of imports, etc.
                for name in tested_modules:
                    module = sys.modules.get(name)
                    if module:
                        reload(module)

                sys.settrace(None)
                sys.stdout.write("code coverage:\n")
                coverage.write_results(sys.stdout)

        # restore sys.path
        sys.path = old_path[:]

    # run()

# class test


cmdclass = {'test': test}

setup ( cmdclass = cmdclass,
        name = "pyQuantLib",
        version = "0.1.1",
        maintainer = "Enrico Sirola",
        maintainer_email = "enri@users.sourceforge.net",
        url = "http://quantlib.sourceforge.net",
        py_modules = ["QuantLib"],
        ext_modules = [Extension
                       ("QuantLibc",
                        ["quantlib_wrap.cpp"],
                        libraries = ["QuantLib"],
                        define_macros = define_macros,
                        include_dirs = include_dirs,
                        library_dirs = library_dirs,
                        extra_compile_args = extra_compile_args,
                        extra_link_args = extra_link_args
                        )
                       ]
        )
