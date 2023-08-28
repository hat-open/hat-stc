from pathlib import Path
import subprocess

from hat.doit import common
from hat.doit.docs import (build_sphinx,
                           build_pdoc)
from hat.doit.py import (get_task_build_wheel,
                         get_task_run_pytest,
                         get_task_create_pip_requirements,
                         run_flake8)


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_pip_requirements']


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
    return get_task_build_wheel(src_dir=src_py_dir,
                                build_dir=build_py_dir)


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir])]}


def task_test():
    """Test"""
    return get_task_run_pytest()


def task_docs():
    """Docs"""

    def build():
        p = subprocess.run(['which', 'drawio'],
                           capture_output=True,
                           check=True)
        drawio_binary_path = p.stdout.decode('utf-8').strip()

        build_sphinx(src_dir=docs_dir,
                     dst_dir=build_docs_dir,
                     project='hat-stc',
                     extensions=['sphinxcontrib.drawio'],
                     conf={'drawio_binary_path': drawio_binary_path})

        build_pdoc(module='hat.stc',
                   dst_dir=build_docs_dir / 'py_api')

    return {'actions': [build]}


def task_pip_requirements():
    """Create pip requirements"""
    return get_task_create_pip_requirements()
