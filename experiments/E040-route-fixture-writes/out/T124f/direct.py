"""Durable DECLARED synthetic ageing branches and four required falsifiers.

Exact frozen unit mechanisms, published E006 asset, hash/scalar receipts only.
The direct caller frames are synthetic, separate from PRIMARY actual70E6 tails.
"""
import argparse,json,subprocess,time
from pathlib import Path
import proof as P
from tests import test_port_in_season_ageing as T
from tests.test_port_stages import IMAGE_SHA
from original_match.port.prove import ProofError


def duplicate(m,zero=False):
    T.computer(m)
    if zero:T.computer(m,0)
    for i in range(20):T.word(m,m.far(0xA917)+191+2*i,0 if zero else 1)
    player=0 if zero else 1
    T.record(m,player,p0=0 if zero else 1,p1=255 if zero else 20,p2=0 if zero else 28,p6=2 if zero else 9,p7=0 if zero else 1,p11=9)
    T.word(m,T.pa(m,player,8),0)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);opts=ap.parse_args()
    test=T.Leaves('test_ability_peak_plateau_half_step_and_word_wrap');test.setUpClass()
    country=test.image.memory[test.image.far(0xA91F)+3*129]
    cases=[('computer-duplicates','1771:7FDF',(1,),lambda m:duplicate(m)),
      ('computer-zero','1771:7FDF',(1,),lambda m:duplicate(m,True)),
      ('managed80-duplicates','1771:7FDF',(country,),lambda m:T.pool_setup(m)),
      ('managed80-doubled-word-alias','1771:7FDF',(country,),lambda m:T.pool_setup(m,0x8000)),
      ('managed80-signed-boundary','1771:7FDF',(country,),lambda m:T.pool_setup(m,0x7FE0,0x40)),
      ('managed80-end-wrap-skip','1771:7FDF',(country,),lambda m:T.pool_setup(m,0xFFF0))]
    with Path(opts.out).open('x') as f:
        P.emit(f,{'schema':'t124f-direct/1','source_asset_sha256':IMAGE_SHA,
          'source_hashes':{**P.sources(),str(Path(__file__).relative_to(P.ROOT)):P.sha(Path(__file__).read_bytes())},
          'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'declared_call_frame':{'sp':0x3E00,'bp':0x3E80,'SS_paragraph':0x3052,'returns':T.RET},
          'scope':'DECLARED unit fixtures: computer20duplicate/zero or managed80duplicate/word-wrap; no natural-career claim; standardT59 strictreturns/orderedLIVEwrites'})
        for name,target,args,setup in cases:
            before={};start=time.monotonic()
            def prepared(m):setup(m);before.update(P.hashes(m))
            m,p=test.call_age(target,args,before=prepared);test.proved(p,target)
            P.emit(f,{'status':'proved','case':name,'target':target,'args_push_order':args,'summary':p.summary(),
              'before_record_hashes':before,'after_record_hashes':P.hashes(m),
              'initials_sha256':P.sha(m.read(m.far(0x9B70),3061)),
              'year_word':m.word_at(m.far(0xA923)+0x38),'elapsed_s':round(time.monotonic()-start,4)})
        def aged(m):T.record(m,1,p1=27,p2=28,p3=160)
        def retire(m):T.record(m,1,p1=31,p2=250,p7=1);T.word(m,T.pa(m,1,8),0)
        def replacement(m):T.computer(m);T.record(m,1,p0=1,p6=9,p7=1)
        for variant,target,args,setup in [('age-increment-dropped','1771:7E4A',(1,),aged),
          ('retirement-threshold-plus-one','1771:7F40',(1,),retire),
          ('replacement-draw-dropped','1771:7E80',(1,),replacement),
          ('pool-scorer-write-dropped','1771:7FDF',(country,),T.pool_setup)]:
            try:test.call_age(target,args,before=setup,variant=variant)
            except ProofError as exc:P.emit(f,{'status':'falsifier-caught','case':variant,'target':target,'difference':str(exc)})
            else:raise AssertionError('uncaught required falsifier '+variant)
if __name__=='__main__':main()
