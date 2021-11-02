from pathlib import Path
import subprocess
import sys

from hat.doit import common
from hat.doit.py import (build_wheel,
                         run_pytest,
                         run_flake8)
from hat.doit.docs import (SphinxOutputType,
                           build_sphinx,
                           build_pdoc)


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs']


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir])]}


def task_build():
    """Build"""

    def build():
        build_wheel(
            src_dir=src_py_dir,
            dst_dir=build_dir / 'py',
            name='hat-stc',
            description='Hat statechart engine',
            url='https://github.com/hat-open/hat-stc',
            license=common.License.APACHE2,
            packages=['hat'])

    return {'actions': [build]}


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir])]}


def task_test():
    """Test"""
    return {'actions': [lambda args: run_pytest(pytest_dir, *(args or []))],
            'pos_arg': 'args'}


def task_docs():
    """Docs"""
    return {'actions': [(build_sphinx, [SphinxOutputType.HTML,
                                        docs_dir,
                                        build_docs_dir]),
                        (build_pdoc, ['hat.stc',
                                      build_docs_dir / 'py_api'])]}
