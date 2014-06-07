""""Functions to edit documents and items."""

import os
import sys
from distutils.spawn import find_executable
import subprocess
import time
import logging

from doorstop.common import DoorstopError


# TODO: add edit_document
# TODO: add edit_item, refactor code from Tree.edit_item

LAUNCH_DELAY = 0.5  # number of seconds to let a program try to launch


def edit(path, tool=None):  # pragma: no cover (integration test)
    """Open a file and wait for the default editor to exit.

    @param path: path of file to open
    @param tool: path of alternate editor

    @return: launched process

    """
    process = launch(path, tool=tool)
    if process:
        try:
            process.wait()
        except KeyboardInterrupt:
            pass
        finally:
            if process.returncode is None:
                process.terminate()
                logging.warning("force closed editor")
        logging.debug("process exited: {}".format(process.returncode))


def launch(path, tool=None):  # pragma: no cover (integration test)
    """Open a file using the default editor.

    @param path: path of file to open
    @param tool: path of alternate editor

    @raise: DoorstopError: no default editor or editor unavailable

    @return: launched process if long-running, else None

    """
    # Determine how to launch the editor
    if tool:
        args = [tool, path]
    elif sys.platform.startswith('darwin'):
        args = ['open', path]
    elif os.name == 'nt':
        cygstart = find_executable('cygstart')
        if cygstart:
            args = [cygstart, path]
        else:
            args = ['start', path]
    elif os.name == 'posix':
        args = ['xdg-open', path]

    # Launch the editor
    try:
        process = _call(args)
    except FileNotFoundError:
        raise DoorstopError("editor not found: {}".format(args[0]))

    # Wait for the editor to launch
    time.sleep(LAUNCH_DELAY)
    if process.poll() is None:
        logging.debug("process is running...")
    else:
        logging.debug("process exited: {}".format(process.returncode))
        if process.returncode != 0:
            raise DoorstopError("no default editor for: {}".format(path))

    # Return the process if it's still running
    if process.returncode is None:
        return process


def _call(args):  # pragma: no cover (integration test)
    """Call a program with arguments and return the process."""
    logging.debug("$ {}".format(' '.join(args)))
    process = subprocess.Popen(args)
    return process
