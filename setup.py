#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import platform
from distutils import log
from subprocess import check_call
from setuptools import setup, find_packages, Command
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info


name = "exa"
description = "A framework for data processing, computation, and visualization."
datadir = "data"
nbdir = "static"
readme = "README.md"
requirements = "requirements.txt"
verfile = "_version.py"
root = os.path.dirname(os.path.abspath(__file__))
is_repo = os.path.exists(os.path.join(root, ".git"))
prckws = {'shell': True} if platform.system().lower() == "windows" else {}
jsroot = os.path.join(root, "js")
node_modules = os.path.join(jsroot, "node_modules")
npm_path = os.pathsep.join([os.path.join(node_modules, ".bin"),
                            os.environ.get("PATH", os.defpath)])
log.set_verbosity(log.DEBUG)
try:
    import pypandoc
    long_description = pypandoc.convert(readme, "rst")
except ImportError:
    with open(readme) as f:
        long_description = f.read()
with open(requirements) as f:
    dependencies = f.read().splitlines()
with open(os.path.join(root, name, verfile)) as f:
    v = f.readlines()[-2]
    v = v.split('=')[1].strip()[1:-1]
    version = '.'.join(v.replace(" ", "").split(","))


def update_package_data(distribution):
    """Modify the ``package_data`` to catch changes during setup."""
    build_py = distribution.get_command_obj("build_py")
    build_py.finalize_options()    # Updates package_data


def js_prerelease(command, strict=False):
    """Build minified JS/CSS prior to performing the command."""
    class DecoratedCommand(command):
        """Used by ``js_prerelease`` to modify JS/CSS prior to running the command."""
        def run(self):
            jsdeps = self.distribution.get_command_obj("jsdeps")
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return
            try:
                self.distribution.run_command("jsdeps")
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    log.warn("Rebuilding JS/CSS failed")
                    if missing:
                        log.error("Missing files: {}".format(missing))
                    raise e
                else:
                    log.warn("Rebuilding JS/CSS failed but continuing...")
                    log.warn(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return DecoratedCommand


#def update_package_data(distribution):
#    """Update package_data to catch changes during setup."""
#    build_py = distribution.get_command_obj('build_py')
#    # distribution.package_data = find_package_data()
#    # re-init build_py options which load package_data
#    build_py.finalize_options()


class NPM(Command):
    description = "Install package.json dependencies using npm."
    user_options = []
    targets = [os.path.join(root, name, nbdir, "extension.js"),
               os.path.join(root, name, nbdir, "index.js")]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def has_npm(self):
        try:
            check_call(["npm", "--version"], **prckws)
            return True
        except Exception:
            return False

    def should_run_npm_install(self):
        #package_json = os.path.join(jsroot, "package.json")
        #node_modules_exists = os.path.exists(node_modules)
        return self.has_npm()

    def run(self):
        has_npm_ = self.has_npm()
        if not has_npm_:
            log.error("`npm` unavailable.  If you're running this command using sudo, make sure `npm` is available to sudo")

        env = os.environ.copy()
        env['PATH'] = npm_path

        if self.should_run_npm_install():
            log.info("Installing build dependencies with npm. This may take a while...")
            check_call(["npm", "install"], cwd=jsroot, stdout=sys.stdout, stderr=sys.stderr, **prckws)
            os.utime(node_modules, None)

        for t in self.targets:
            if not os.path.exists(t):
                msg = "Missing file: %s" % t
                if not has_npm_:
                    msg += "\nnpm is required to build a development version of jupyter-" + name
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)


setup_args = {
    'name': name,
    'version': version,
    'description': description,
    'long_description': long_description,
    'include_package_data': True,
    'data_files': [
        ("share/jupyter/nbextensions/jupyter-" + name, [
            os.path.join(name, nbdir, "extension.js"),
            os.path.join(name, nbdir, "index.js"),
            os.path.join(name, nbdir, "index.js.map")
        ]),
    ],
    'package_data': {name: [datadir + "/*"]},
    'include_package_data': True,
    'install_requires': dependencies,
    'packages': find_packages(),
    'zip_safe': False,
    'cmdclass': {
        'build_py': js_prerelease(build_py),
        'egg_info': js_prerelease(egg_info),
        'sdist': js_prerelease(sdist, strict=True),
        'jsdeps': NPM,
    },
    'license': "Apache License Version 2.0",
    'author': "Thomas J. Duignan and Alex Marchenko",
    'author_email': "exa.data.analytics@gmail.com",
    'maintainer_email': "exa.data.analytics@gmail.com",
    'url': "https://exa-analytics.github.io/" + name,
    'download_url': "https://github.com/avmarchenko/" + name + "/tarball/{}.tar.gz".format(version),
    'keywords': ["data", "analytics", "hpc", "jupyter", "notebook", "visualization"],
    'classifiers': [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Natural Language :: English"
    ]
}

setup(**setup_args)
