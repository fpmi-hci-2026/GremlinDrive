"""Guard the original Lab3 use-case meanings and all 52 operation cross-references."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent;L4=R/'lab4'
spec=json.loads((L4/'openapi.json').read_text());trace=json.loads((L4/'traceability.json').read_text());ops={o['operationId']:(m.upper(),p,o) for p,v in spec['paths'].items() for m,o in v.items() if m in {'get','post','put','patch','delete'}}
assert len(ops)==len(trace)==52
expected={'startUpload':'UC-01','completeUpload':'UC-01','createShare':'UC-02','inviteMember':'UC-03','restoreVersion':'UC-04','createAccessRequest':'UC-05','decideAccessRequest':'UC-05'}
for operation,uc in expected.items():assert ops[operation][2]['x-use-case']==uc,(operation,uc)
for row in trace:
 method,path,op=ops[row['operation']]
 assert (method,path,op['x-use-case'])==(row['method'],row['path'],row['uc'])
 assert op['x-requirements']==row['fr'].split(',')
 assert op['x-user-stories']==row['us'].split(',')
 assert all(1<=int(x[3:])<=30 for x in op['x-requirements'])
 assert all(1<=int(x[3:])<=16 for x in op['x-user-stories'])
expiry=spec['components']['schemas']['ShareCreate']['properties']['expires_in_days']
assert expiry['default']==14 and any(x.get('type')=='null' for x in expiry['anyOf'])
assert 'null' in spec['components']['schemas']['ShareLink']['properties']['expires_at']['type']
registry=(L4/'requirements.md').read_text();listed=re.findall(r'^\| (UC-\d+) \|',registry,re.M)
assert listed==[f'UC-{n:02}' for n in range(1,20)]
print('OK: original UC-01..05 meanings; sorted UC-01..19 registry; 52 API/FR/US/UC cross-references')
