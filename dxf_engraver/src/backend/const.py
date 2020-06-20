#!/usr/bin/env python3

# validator constants and regular expressions
MATERIALS = [
    "Hardox400",
    "11523",
    "Slza",
    "Nerez17240",
]
THICKNESSES = ['1','1,5','1.5','2','2,5','2.5','3','4','5','6','8','10','12','15','20','25','30','35','40','50','60','70','100']
MAX_PARTS = 20

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
