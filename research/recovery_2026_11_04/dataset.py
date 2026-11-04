"""Read public OOXML. Locked-test outcome values are inaccessible to development loader."""
from pathlib import Path
import re,math
import zipfile,xml.etree.ElementTree as ET,json
from fetch_data import verify_cache
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheets(path):
    with zipfile.ZipFile(path) as z:
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        else:strings=[]
        book=ET.fromstring(z.read('xl/workbook.xml'))
        names=[e.attrib['name'] for e in book.find('m:sheets',NS)]
        result={}
        for i,name in enumerate(names,1):
            rows=[]
            for row in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('m:sheetData/m:row',NS):
                cells={}
                for c in row:
                    v=c.findtext('m:v',None,NS)
                    if c.attrib.get('t')=='s' and v is not None:v=strings[int(v)]
                    elif c.attrib.get('t')=='inlineStr':v=''.join(c.find('m:is',NS).itertext())
                    cells[''.join(x for x in c.attrib['r'] if x.isalpha())]=v
                rows.append((int(row.attrib['r']),cells))
            result[name]=rows
        return result
def power_rows(split='development',unlock=False):
    if split not in ('development','test','all'):raise ValueError('split')
    if split!='development' and not unlock:raise ValueError('locked test requires explicit unlock after model lock')
    cache=verify_cache();book=sheets(cache/'Power_rawdata.xlsx');out=[]
    for rest in [12,18,24]:
        for rownum,cells in book[f'Avg_{rest}']:
            match=re.match(r'^WTR(\d+)_',cells.get('A') or '')
            if not match:continue
            sid=int(match[1]);group='test' if sid%3==0 else 'development'
            if split!='all' and group!=split:continue
            baseline=cells.get('B')
            if baseline is None or float(baseline)<=0:continue
            for j,col in enumerate('BCDEFGHIJK',1):
                value=cells.get(col)
                if value is None:continue
                y=float(value)
                if not math.isfinite(y) or y<0:raise ValueError('invalid measured power')
                out.append(dict(participant=sid,split=group,rest_s=rest,effort_s=6.,repetition=j,reference_W=float(baseline),power_W=y,ratio=y/float(baseline),source_cell=f'Avg_{rest}!{col}{rownum}'))
    return out

def development_audit():
    cache=verify_cache();power=sheets(cache/'Power_rawdata.xlsx');vo=sheets(cache/'VO2_rawdata.xlsx');out=[]
    for sheet,rows in power.items():
        for rownum,r in rows:
            match=re.match(r'^WTR(\d+)_',r.get('A') or '')
            if not match or int(match[1])%3==0:continue
            if sheet.startswith('Avg_'):
                rest=sheet.split('_')[1];tw=dict(power['TW_'+rest]);twrow=next(v for _,v in power['TW_'+rest] if v.get('A')==r['A'])
                for col in 'BCDEFGHIJK':
                    if r.get(col) is not None and twrow.get(col) is not None:
                        out.append(abs(float(twrow[col])-6*float(r[col])))
    return dict(development_participants=sorted({r['participant'] for r in power_rows()}),test_ids_from_labels=[3,6,9,12,15,18,21],max_work_minus_6power_J=max(out),VO2_sheets=list(vo),VO2_scope='per-bout extrema only; not breath-by-breath or time-integrated oxygen; no PCr',leakage='all conditions grouped by WTR prefix; test outcomes not used by development audit')
if __name__=='__main__':
    cache=verify_cache()
    for file in cache.glob('*.xlsx'):
        print(file.name)
        for name,rows in sheets(file).items():
            print(name,'rows',len(rows),'first row labels',rows[:2])
