#!/usr/bin/python3
import os
import re

import ezdxf

MATERIALS = [
    "Hardox400",
    "11523",
    "Slza",
    "Nerez17240",
]
THICKNESSES = ['1','1,5','1.5','2','2,5','2.5','3','4','5','6','8','10','12','15','20','25','30','35','40','50','60','70','100']
MAX_PARTS = 20


accepted = []

thickness_re = r'T= (.*)'
material_re = r'M= (.*)'
name_re = r'N= (.*)'
quantity_re = r'Q= (.*)'
order_re = r'Z= (.*)'

value_missing_re = r'^\s*$'

correct_thickness_re = r'^(\S+)$'
correct_material_re = r'^(\w+)$'
correct_name_re = r'^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*?)$'
correct_quantity_re = r'^(\d+)$'

msgs= {
    'processing': 'Zpracovavam soubor: ',
    'err_name_missing': 'Chybejici jmeno vypalku: ',
    'err_name_wrong': 'Spatne jmeno vypaku: ',
    'err_thic_missing': 'Chybejici tloustka: ',
    'err_thic_wrong': 'Spatna tloustka: ',
    'err_mat_missing': 'Chybejici material: ',
    'err_mat_wrong': 'Spatny material: ',
    'err_qty_missing': 'Chybejici mnozstvi: ',
    'err_qty_wrong': 'Spatna mnozstvi: ',
    'warn_qty_high': 'Velke mnozstvi vypalku: ',
    'err_not_in_block': 'Text mimo blok: ',
    'warn_engrave_too_small': 'Vypalek prilis maly na gravir: ',
}

c_accepted_layers = ['0', 'SLD-0', 'GRAV', 'GRAVIROVANI', 'TECHNOLOGIE']
c_engraving_color = (255, 0, 191)
c_text_height_to_width_ratio = 1.4
c_text_height = 8
c_order_type = 'order'
c_name_type = 'name'
c_row_order = {
    c_order_type: 0,
    c_name_type: 1,
    }
c_attachment_bot_left = 7
c_attachment_top_left = 1

class ValidateDWG():
    def __init__(self):
        pass

    def check_dxfs(self):
        files = filter(os.path.isfile, os.listdir(os.curdir))
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            if ext == '.dxf':
                self.process_dxf(f)

    def process_dxf(self, f):
        self.dxf = ezdxf.readfile(f)
        self.dxf.filename = f #bug in dxf...
        self.msp = self.dxf.modelspace()

        print(msgs['processing'], f)

        # process texts
        #for e in msp:
        #    if re.match('.*TEXT.*', e.dxftype(), flags=re.IGNORECASE):
        #        self.validate_entity(e, err='err_not_in_block')

        #disable layers
        for layer in self.dxf.layers:
            if layer.dxf.name not in c_accepted_layers:
                layer.off()

        # process blocks
        blocks = self.msp.query('*')
        for e in blocks:
            if isinstance(e, ezdxf.entities.mtext.MText) or isinstance(e, ezdxf.entities.text.Text):
                self.validate_entity(e)
        self.dxf.save()

    def check_material(self, s):
        res = re.match(correct_material_re, s)
        if res and res.groups()[0] in MATERIALS:
            return None
        elif re.match(value_missing_re, s):
            return 'err_mat_missing'
        else:
            return 'err_mat_wrong'

    def check_name(self, s):
        res = re.match(correct_name_re, s)
        if res:
            return None
        elif re.match(value_missing_re, s):
            return 'err_name_missing'
        else:
            return 'err_name_wrong'

    def check_thickness(self, s):
        res = re.match(correct_thickness_re, s)
        if res and str(res.groups()[0]) in THICKNESSES:
            return None
        elif re.match(value_missing_re, s):
            return 'err_thic_missing'
        else:
            return 'err_thic_wrong'

    def check_quantity(self, s):
        res = re.match(correct_quantity_re, s)
        if res:
            if int(res.groups()[0]) > MAX_PARTS:
                return 'warn_qty_high'
            return None
        elif re.match(value_missing_re, s):
            return 'err_qty_missing'
        else:
            return 'err_qty_wrong'

    def print_error(self, text, err, tabs=0):
        print(
            '\t'*tabs,
            msgs[err],
            text
        )

    def crop_name(self, name_text):
        name_match = re.match(r'(.*)-(.+?)-(-*\d+)', name_text)
        if name_match:
            groups = list(name_match.groups())
            groups[1] = ''
            return '-'.join(groups)
        only_part_number_match = re.match(r'^.*-(\S+)$', name_text)
        if only_part_number_match:
            return only_part_number_match.group(1)
        return None

    def format_engraving(self, text, text_type, attachment_point, old_height, old_insert, full_length):
        new_insert = old_insert
        new_text = re.sub(r'^0+', '', text)
        new_text = re.sub(r'-0+', '-', new_text)


        new_height = c_text_height
        zooming_in = new_height > old_height
        old_width = full_length * (old_height / c_text_height_to_width_ratio)
        new_width = len(new_text) * (new_height/ c_text_height_to_width_ratio)

        if text_type == c_name_type:
            while new_width > old_width:
                new_text = self.crop_name(new_text)
                if new_text:
                    new_width = len(new_text) * (new_height / c_text_height_to_width_ratio)
                else:
                    return None, None, None

        elif text_type == c_order_type:
            if new_width > old_width:
                new_text = re.match(r'^(\S.*?)-.*', new_text).group(1)
                new_width = len(new_text) * (new_height / c_text_height_to_width_ratio)

            # if the shortening didn't help -> don't engrave
            if new_width > old_width:
                return None, None, None

        # move insertion point when new text is shorter than the old one
        row_compensation = (c_row_order[text_type] * new_height) if zooming_in else 0
        if attachment_point == c_attachment_top_left:
            new_insert = ezdxf.math.Vector((
                old_insert[0] + (old_width - new_width) / 2,
                old_insert[1] - (old_height - new_height) - new_height - row_compensation,
                0,
            ))
        else:
            new_insert = ezdxf.math.Vector((
                old_insert[0] + (old_width - new_width) / 2,
                old_insert[1] + (old_height - new_height) - row_compensation,
                0,
            ))
            

        return new_text, new_height, new_insert

    def copy_engraving(self, e, text, text_type, full_length):
        if isinstance(e, ezdxf.entities.text.Text):
            return self.copy_engraving_text(e, text, text_type, full_length)
        elif isinstance(e, ezdxf.entities.mtext.MText):
            return self.copy_engraving_mtext(e, text, text_type, full_length)

    def copy_engraving_mtext(self, e, text, text_type, full_length):
        """
        ugly hack here - 1 deg rotation means it has already been copied
        """
        rotation = e.get_rotation()
        if not rotation:
            old_attrs = e.dxfattribs()
            new_text, new_height, new_insert = self.format_engraving(text, text_type, old_attrs['attachment_point'], old_attrs['char_height'], old_attrs['insert'], full_length)
            if not new_text:
                return 'warn_engrave_too_small'
            new_attrs = {
                'true_color': 255 * 65536 + 0 * 256 +  191,
                'height': new_height,
                'insert': new_insert,
                'layer': old_attrs['layer'],
                'linetype': 'Continuous',
                'style': old_attrs['style'],
                'text': new_text,
                'width': old_attrs['width'],
            }
            new_text = self.msp.add_text(new_text, new_attrs)
            e.set_rotation(0.00001)

    def copy_engraving_text(self, e, text, text_type, full_length):
        rotation = e.dxf.rotation
        if not rotation:
            old_attrs = e.dxfattribs()
            new_text, new_height, new_insert = self.format_engraving(text, text_type, c_attachment_top_left, old_attrs['height'], old_attrs['insert'], full_length)
            if not new_text:
                return 'warn_engrave_too_small'
            new_attrs = {
                'true_color': 255 * 65536 + 0 * 256 +  191,
                'height': new_height,
                'insert': new_insert,
                'layer': old_attrs['layer'],
                'linetype': old_attrs['linetype'],
                'style': old_attrs['style'],
                'text': new_text,
                'width': old_attrs['width'],
            }
            new_text = self.msp.add_text(new_text, new_attrs)
            e.dxf.rotation = 0.00001

    def validate_entity(self, e, err=None, do_copy_engraving=True):
        if isinstance(e, ezdxf.entities.text.Text):
            text = e.dxf.text
        elif isinstance(e, ezdxf.entities.mtext.MText):
            text = re.sub('[^a-zA-Z0-9\-= ]', '', e.text)

        if text in accepted:
            return True

        if err:
            self.print_error(text, err, 1)
        else:
            res_name = re.match(name_re, text)
            res_material = re.match(material_re, text)
            res_thickness = re.match(thickness_re, text)
            res_quantity = re.match(quantity_re, text)
            res_order = re.match(order_re, text)
            if res_name:
                full_name_length = len(res_name.group(0))
                name = res_name.group(1)
                err = self.check_name(name)
                if not err and do_copy_engraving:
                    # remove redundant part no
                    redundant_part_no = re.match(r"(.*-\d\d\d)(-\d\d\d)", name)
                    if redundant_part_no:
                        name = redundant_part_no.group(1)
                    err = self.copy_engraving(e, name, c_name_type, full_name_length)
            elif res_material:
                err = self.check_material(res_material.groups()[0])
            elif res_thickness:
                err = self.check_thickness(res_thickness.groups()[0])
            elif res_quantity:
                err = self.check_quantity(res_quantity.groups()[0])
            elif res_order:
                full_order_length = len(res_order.group(0))
                order = res_order.group(1)
                err = None
                if not err and do_copy_engraving:
                    err = self.copy_engraving(e, order, c_order_type, full_order_length)


            if err:
                self.print_error(text, err, 1)


validate = ValidateDWG()
validate.check_dxfs()

input("Zmackni Enter pro zavreni")

