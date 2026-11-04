"""Read immutable OOXML with stdlib; blanks remain None, never zero/imputed."""
from pathlib import Path
import csv,zipfile,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def workbook_rows(path=None):
    path=path or BASE/'data/pone.0276314.s001.xlsx'
    with zipfile.ZipFile(path) as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        rows=[]
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',NS):
            values={}
            for cell in row:
                value=cell.findtext('m:v',None,NS)
                if cell.attrib.get('t')=='s' and value is not None:value=strings[int(value)]
                values[''.join(c for c in cell.attrib['r'] if c.isalpha())]=value
            rows.append((int(row.attrib['r']),values))
        return rows
def observations():
    rows=workbook_rows();header=dict(rows[1][1]);out=[]
    for rownum,r in rows[2:]:
        if not r.get('A') or not r.get('B'):continue
        # Lp is a row index, NOT a verified cross-climate participant identifier.
        subject=int(float(r['A']))
        for col,key in header.items():
            if key and key.startswith('MeanP') and '(W)' in key:
                rep=int(key.split('(')[0].replace('MeanP',''))
                value=r.get(col)
                split=('fit' if subject%2 else 'validation') if r['B']=='Thermoneutral' else 'excluded_unresolved_pairing'
                out.append(dict(participant=subject,condition=r['B'],repetition=rep,mean_power_W=float(value) if value is not None else None,source_cell=f'Results!{col}{rownum}',split=split))
    return out
if __name__=='__main__':
    rows=workbook_rows()
    print('headers:',rows[1]);print('rows',len(rows));print('IDs',[(i,r.get('A'),r.get('B')) for i,r in rows[2:]])
    out=observations();print('observations',len(out),'missing',sum(x['mean_power_W'] is None for x in out))
