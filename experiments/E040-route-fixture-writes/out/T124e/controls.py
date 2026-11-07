"""Durable two-manager page history and the three required caller falsifiers.

Reuses the EXACT frozen unit mechanisms and accepted D original-built world
input. Manager/tag/group relocation is declared synthetic; original bytes stay
private. This adds receipts, never a replacement owner or display stand-in.
"""
import argparse,json,time
from pathlib import Path
import proof as P
from tests import test_port_stage_news as T
from original_match.machine import Machine
from original_match.port.prove import ProofError
from original_match.news import news_pages


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();start=time.monotonic()
    image=T.world_image();m=Machine(image.memory,image.load);countries=list(T.group_members(m))[:2]
    with Path(a.out).open('x') as f:
        P.emit(f,{'schema':'t124e-controlled-pages/1','source_hashes':{**P.sources(),str(Path(__file__).relative_to(P.ROOT)):P.sha(Path(__file__).read_bytes())},
          'source_memory_sha256':P.sha(bytes(image.memory[:0x110000])),
          'scope':'DECLARED original-built world image; coherent manager/tag/group/count/cursor relocation and manager2 name representation copied from manager1; exact frozen T.announce synthetic real7152 far-return frame and original Route.Keys policy'})
        r,p,contexts=T.announce(image,countries)
        assert p.summary()['000E:60CB']['proved']==2 and len(r.news_history)==len(contexts)==2
        assert r.m.read(r.m.far(0xA923)+1,1)[0]==2
        pages=[]
        for i,(snap,ctx) in enumerate(zip(r.news_history,contexts)):
            assert ctx[:3]==(countries[i],i+1,129+i)
            h=P.sha(snap.cells);data=json.dumps({'cells_hex':snap.cells.hex(),'decoded_lines':news_pages(snap)[0],'observed_context':ctx},ensure_ascii=False,sort_keys=True).encode()
            path=P.ROOT/'.cache/t124e/pages'/f'controlled-two-manager-{i}-{h[:16]}.json';path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(data)
            assert path.read_bytes()==data
            pages.append({'index':i,'country':ctx[0],'manager_cursor':ctx[1],'manager_tag':ctx[2],'next_fixture_word':ctx[3],
              'cells_sha256':h,'flags_words':list(snap.flags_words),'waiting_key':snap.waiting_key,'pushed_back':snap.pushed_back,
              'private_capture':{'path':str(path.relative_to(P.ROOT)),'sha256':P.sha(data)}})
        P.emit(f,{'status':'two-managers-proved','pages':pages,'cursor_before':2,'cursor_after':2,'summary':p.summary(),
          'ordered_record_sha256':P.sha(json.dumps(P.D.public(r.record),sort_keys=True).encode()),'elapsed_s':round(time.monotonic()-start,4)})
        country=T.tour_country(image)
        def failure(m):m.write(m.far(0xA923)+2,b'\0')
        def stale(m):m.wr(0x9B43,0)
        for name,selected,kwargs in [
          ('news-draw',[country],{'variant':'stage-news-draw-dropped','setup':failure}),
          ('cursor-restoration',countries,{'variant':'stage-news-cursor-not-restored'}),
          ('tour-next-write',[country],{'helper_variant':'next-write-omitted','setup':stale})]:
            try:T.announce(image,selected,**kwargs)
            except ProofError as exc:P.emit(f,{'status':'falsifier-caught','case':name,'difference':str(exc)})
            else:raise AssertionError('uncaught required falsifier '+name)
if __name__=='__main__':main()
