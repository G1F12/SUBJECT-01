# -*- coding: utf-8 -*-
"""
Standard-library OOXML (.xlsx) reader and test fixture writer.
Zero external dependencies (uses standard library zipfile and xml.etree.ElementTree).
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def col_idx_to_name(idx: int) -> str:
    """Convert 0-based column index to Excel column name (0 -> A, 1 -> B, etc.)."""
    result = ""
    idx += 1
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result

def col_name_to_idx(col_str: str) -> int:
    """Convert Excel column name to 0-based index ('A' -> 0, 'B' -> 1)."""
    num = 0
    for c in col_str.upper():
        if 'A' <= c <= 'Z':
            num = num * 26 + (ord(c) - ord('A') + 1)
    return num - 1

def read_xlsx_sheets(path: Path) -> dict[str, list[list[str | float | int | None]]]:
    """
    Read an OOXML .xlsx file into a dictionary: {sheet_name: 2D table of cell values}.
    stdlib only.
    """
    if not zipfile.is_zipfile(path):
        raise ValueError(f"File {path} is not a valid zip / xlsx archive.")
        
    with zipfile.ZipFile(path, 'r') as z:
        namelist = z.namelist()
        if 'xl/workbook.xml' not in namelist:
            raise ValueError(f"File {path} missing xl/workbook.xml.")
            
        strings = []
        if 'xl/sharedStrings.xml' in namelist:
            sst_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in sst_root.findall('m:si', NS):
                strings.append(''.join(si.itertext()))
                
        book_root = ET.fromstring(z.read('xl/workbook.xml'))
        sheets_elem = book_root.find('m:sheets', NS)
        if sheets_elem is None:
            return {}
            
        sheet_entries = []
        for s in sheets_elem.findall('m:sheet', NS):
            sheet_entries.append((s.attrib.get('name', 'Sheet'), s.attrib.get('sheetId', '1')))
            
        result = {}
        for idx, (sheet_name, sheet_id) in enumerate(sheet_entries, start=1):
            sheet_filename = f'xl/worksheets/sheet{idx}.xml'
            if sheet_filename not in namelist:
                # Try finding by target or name
                candidates = [n for n in namelist if n.startswith('xl/worksheets/sheet')]
                sheet_filename = candidates[idx - 1] if len(candidates) >= idx else None
                
            if not sheet_filename or sheet_filename not in namelist:
                continue
                
            ws_root = ET.fromstring(z.read(sheet_filename))
            sheet_data = ws_root.find('m:sheetData', NS)
            if sheet_data is None:
                result[sheet_name] = []
                continue
                
            grid = []
            for row_elem in sheet_data.findall('m:row', NS):
                r_num = int(row_elem.attrib.get('r', len(grid) + 1))
                # Expand grid if rows skipped
                while len(grid) < r_num:
                    grid.append([])
                    
                row_cells = {}
                max_c = 0
                for c_elem in row_elem.findall('m:c', NS):
                    r_attr = c_elem.attrib.get('r', '')
                    col_letters = ''.join(ch for ch in r_attr if ch.isalpha())
                    col_idx = col_name_to_idx(col_letters) if col_letters else len(row_cells)
                    max_c = max(max_c, col_idx)
                    
                    val_elem = c_elem.find('m:v', NS)
                    raw_val = val_elem.text if val_elem is not None else None
                    cell_type = c_elem.attrib.get('t', '')
                    
                    parsed_val = None
                    if cell_type == 's' and raw_val is not None:
                        s_idx = int(raw_val)
                        parsed_val = strings[s_idx] if s_idx < len(strings) else raw_val
                    elif cell_type == 'inlineStr':
                        is_elem = c_elem.find('m:is', NS)
                        parsed_val = ''.join(is_elem.itertext()) if is_elem is not None else ''
                    elif raw_val is not None:
                        try:
                            if '.' in raw_val or 'e' in raw_val.lower():
                                parsed_val = float(raw_val)
                            else:
                                parsed_val = int(raw_val)
                        except ValueError:
                            parsed_val = raw_val
                            
                    row_cells[col_idx] = parsed_val
                    
                row_list = [row_cells.get(c) for c in range(max_c + 1)]
                grid[r_num - 1] = row_list
                
            result[sheet_name] = grid
            
        return result

def create_test_xlsx(path: Path, sheets_data: dict[str, list[list]]):
    """
    Create a valid OOXML .xlsx workbook with multiple sheets from Python data structures.
    Uses only stdlib zipfile and XML.
    """
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                     '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                     '  <Default Extension="xml" ContentType="application/xml"/>',
                     '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    
    wb_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    
    wb_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
              '  <sheets>']
    
    shared_strings = []
    string_map = {}
    
    def get_str_id(s):
        s = str(s)
        if s not in string_map:
            string_map[s] = len(shared_strings)
            shared_strings.append(s)
        return string_map[s]
        
    sheets_xml_map = {}
    
    for s_idx, (s_name, rows) in enumerate(sheets_data.items(), start=1):
        content_types.append(f'  <Override PartName="/xl/worksheets/sheet{s_idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        wb_rels.append(f'  <Relationship Id="rId{s_idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{s_idx}.xml"/>')
        wb_xml.append(f'    <sheet name="{s_name}" sheetId="{s_idx}" r:id="rId{s_idx}"/>')
        
        ws_lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
                    '  <sheetData>']
        
        for r_num, row in enumerate(rows, start=1):
            ws_lines.append(f'    <row r="{r_num}">')
            for c_idx, val in enumerate(row):
                if val is None:
                    continue
                col_letter = col_idx_to_name(c_idx)
                cell_ref = f"{col_letter}{r_num}"
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    ws_lines.append(f'      <c r="{cell_ref}"><v>{val}</v></c>')
                else:
                    s_id = get_str_id(val)
                    ws_lines.append(f'      <c r="{cell_ref}" t="s"><v>{s_id}</v></c>')
            ws_lines.append('    </row>')
            
        ws_lines.append('  </sheetData>')
        ws_lines.append('</worksheet>')
        sheets_xml_map[f'xl/worksheets/sheet{s_idx}.xml'] = '\n'.join(ws_lines)
        
    # Shared strings relationship
    sst_id = len(sheets_data) + 1
    content_types.append('  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>')
    content_types.append('</Types>')
    
    wb_rels.append(f'  <Relationship Id="rId{sst_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>')
    wb_rels.append('</Relationships>')
    
    wb_xml.append('  </sheets>')
    wb_xml.append('</workbook>')
    
    sst_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">']
    for s in shared_strings:
        escaped = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        sst_xml.append(f'  <si><t>{escaped}</t></si>')
    sst_xml.append('</sst>')
    
    root_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                 '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>',
                 '</Relationships>']
                 
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '\n'.join(content_types))
        z.writestr('_rels/.rels', '\n'.join(root_rels))
        z.writestr('xl/_rels/workbook.xml.rels', '\n'.join(wb_rels))
        z.writestr('xl/workbook.xml', '\n'.join(wb_xml))
        z.writestr('xl/sharedStrings.xml', '\n'.join(sst_xml))
        for filename, content in sheets_xml_map.items():
            z.writestr(filename, content)
