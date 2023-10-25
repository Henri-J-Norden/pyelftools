# -------------------------------------------------------------------------------
# elftools example: dwarf_die_tree.py
#
# In the .debug_info section, Dwarf Information Entries (DIEs) form a tree.
# pyelftools provides easy access to this tree, as demonstrated here.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
# -------------------------------------------------------------------------------
from __future__ import print_function
from pathlib import Path
import sys
from pprint import pprint

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.elf.elffile import ELFFile
from elftools.dwarf.datatype_cpp import parse_cpp_datatype


def process_file(filename):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()

        for CU in dwarfinfo.iter_CUs():
            # DWARFInfo allows to iterate over the compile units contained in
            # the .debug_info section. CU is a CompileUnit object, with some
            # computed attributes (such as its offset in the section) and
            # a header which conforms to the DWARF standard. The access to
            # header elements is, as usual, via item-lookup.
            print('  Found a compile unit at offset %s, length %s' % (
                CU.cu_offset, CU['unit_length']))

            # Start with the top DIE, the root for this CU's DIE tree
            top_DIE = CU.get_top_DIE()
            print('    Top DIE with tag=%s' % top_DIE.tag)

            # We're interested in the filename...
            print('    name=%s' % Path(top_DIE.get_full_path()).as_posix())

            # Display DIEs recursively starting with top_DIE
            die_info_rec(top_DIE)


def die_info_rec(die, indent_level='    '):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    # print(indent_level + 'DIE tag=%s' % die.tag)
    die_var_info(die, indent_level)
    child_indent = indent_level + '  '
    for child in die.iter_children():
        die_info_rec(child, child_indent)


def die_var_info(die, indent_level):
    if die.tag != "DW_TAG_variable":
        return
    if "DW_AT_name" not in die.attributes:
        return

    print(f"{indent_level}> name={die.attributes['DW_AT_name'].value} type='{parse_cpp_datatype(die)}'")
    #print(f"{indent_level}> DW_AT_type tags:")
    die_var_type_rec(die, indent_level + '  ')


def die_var_type_rec(die, indent_level):
    if "DW_AT_type" not in die.attributes:
        return

    t = die.get_DIE_from_attribute("DW_AT_type")
    type_desc = parse_cpp_datatype(die)
    print(f"{indent_level}DIE tag={t.tag} type='{type_desc}' modifiers={type_desc.modifiers}")
    die_var_type_rec(t, indent_level + '  ')


if __name__ == '__main__':
    if sys.argv[1] == '--test':
        for filename in sys.argv[2:]:
            process_file(filename)
