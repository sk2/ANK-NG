AutoNetkit installation instructions.

These apply to both Linux and Mac OS X.

Note: you may need to run the commands as "sudo" if you receive permission errors.

Download the setuptools installation from http://pypi.python.org/pypi/setuptools#downloads

$ sh ./setuptools-0.6c11-py2.6.egg

then install pip (a better package manager)

$ easy_install pip

and then
$ pip install autonetkit-0.0.1.tar.gz

easy_install/pip adds the console_script entry point to the path, so you should be able to then run AutoNetkit as:

$ autonetkit -f file.graphml

eg

sk:Desktop sk2$ autonetkit -f virl2.graphml 
Compiling Cisco for demo
sk:Desktop sk2$ tree demo/
demo/
└── 20120711_164028
    ├── r1
    │   ├── admin-config.conf
    │   └── router.conf
    ├── r10.conf
    ├── r2
    │   ├── admin-config.conf
    │   └── router.conf
    ├── r3.conf
    ├── r4.conf
    ├── r5.conf
    ├── r6.conf
    ├── r7.conf
    ├── r8.conf
    └── r9.conf

3 directories, 12 files
