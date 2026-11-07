"""Declared continental-host call frame from the actual original6B55 announcement.

Only manager ownership/group/cursor and the corresponding pushed country/AX
are controlled. All country ranks, original-built group rows, calendar/result
and player bytes remain unchanged. Not a naturally played manager switch.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import proof as P
from tests.test_port_stage_news import managers,manager_country
from original_match.machine import REGS
HERE=P.HERE;ROOT=P.ROOT

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-out',default=str(HERE/'controlled-continental-host-input-v1.jsonl'));ap.add_argument('--proof-out',default=str(HERE/'controlled-continental-host-proof-v1.jsonl'));ap.add_argument('--plain-out',default=str(HERE/'plain-continental-host-v1.jsonl'));args=ap.parse_args()
    source=HERE/'natural-continental-input-v1.jsonl';cp=json.loads(source.read_text().splitlines()[-1])['checkpoint']
    r=P.load(cp);m=r.m;g=m.far(0xA923);countries=m.far(0xA917)
    assert P.D.game(m)['stage']==3 and P.D.game(m)['mode']==0
    before=m.read(0,0x110000);old=manager_country(m);continent=m.read(countries+191*old+44,1)[0]
    host=m.word_at(g+0x2C+2*continent)
    assert m.read(countries+191*host+44,1)[0]==continent
    table=m.far(0xA933)+continent*0x1C0+0x700-0x1F8
    groups={m.word_at(table+group*0x38+8*slot):group for group in range(1,9) for slot in range(4)}
    assert host in groups and host!=old
    fixtures=m.read(m.far(0xA92B),2408*8);tables=m.read(m.far(0xA933),0x1C00);players=m.read(m.far(0xA91B),3061*20)
    managers(m,[host],groups=groups)
    # Actual7148/714B/714D on this declared manager record would zeroextend the
    # country into AX and push it before714E/714F's pushCS+near far-frame.
    s=m.reg('ss')*16+m.reg('sp');m.write(s+4,host.to_bytes(2,'little'));m.set_reg('ax',host)
    assert m.read(m.far(0xA92B),2408*8)==fixtures and m.read(m.far(0xA933),0x1C00)==tables
    assert m.read(m.far(0xA91B),3061*20)==players
    assert all(m.reg(k)==v for k,v in cp['context']['regs'].items() if k!='EAX')
    for c in range(129):
        a=before[countries+191*c:countries+191*(c+1)];b=m.read(countries+191*c,191)
        assert all(x==y or i==46 for i,(x,y) in enumerate(zip(a,b)))
    out=Path(args.input_out)
    with out.open('x') as f:
        P.emit(f,{'schema':'t124e-controlled-continental-host/1','source':cp,'source_receipt_sha256':P.sha(source.read_bytes()),
          'source_hashes':{**P.sources(),str(Path(__file__).relative_to(ROOT)):P.sha(Path(__file__).read_bytes())},
          'declared_edits':{'manager1_country_before':old,'manager1_country_after':host,'manager_tag':129,
          'group':groups[host],'cursor':1,'count':1,'sacked':0,'caller_pushed_country_and_AX':host},
          'unchanged_original_data':{'all2408fixtures_sha256':P.sha(fixtures),'allgroup_tables_sha256':P.sha(tables),
          'all3061players_sha256':P.sha(players),'country_rank_and_player_bytes_unchanged':True},'scope':'DECLARED valid synthetic news frame, not a natural manager switch; original6B55-built continental inputs'})
        P.emit(f,{'status':'announcement-entry','phase':'continental-host','checkpoint':P.checkpoint(r,'continental-host-entry'),'game':P.D.game(m)})
    P.prove('continental-host',out,Path(args.proof_out))
    subprocess.run([sys.executable,'-B',str(HERE/'plain.py'),'--phase','continental-host','--input',str(out),'--out',args.plain_out],check=True)
if __name__=='__main__':main()
