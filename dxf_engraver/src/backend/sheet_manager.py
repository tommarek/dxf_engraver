#!/usr/bin/env python3
import ezdxf

from src.backend.part import Part

class SheetManager():
    def __init__(self, filename):
        self.filename = filename
        self.dxf = self._load_dxf(filename)
        self.msp = self.dxf.modelspace()

    def _load_dxf(self, filename):
        dxf = ezdsf.readfile(filename)
        dxf.filename = filename
        return dxf

    def load_parts(self):
        for block in self.msp.query('*'):
            print(blocks)

    def explode_blocks(self):
        for flag_ref in msp.query('INSERT[name=="FLAG"]'):
            print(flag_ref)
            #lag_ref.explode()
