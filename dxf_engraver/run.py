#!/usr/bin/env python3

import sys

from src.backend.sheet_manager import SheetManager
from src.frontend.gui import AppGui


if __name__ == '__main__':
    if len(sys.argv) == 1:
        #Builder.load_file('src/frontend/app.kv')
        app = AppGui()
        app.run()
    else:
        # collect arguements from sys.argv
        pass
