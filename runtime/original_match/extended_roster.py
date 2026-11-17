"""[designed: owner2026-11-18, T138a/#727] Optional larger-bench planning.

The original country still has20 words. This immutable plan describes selected
additional members and a declared promotion into a native bench slot; it never
constructs a machine or writes guest memory. Default Match is not changed here.
"""
from dataclasses import dataclass


def _words(values, maximum=24):
    if not isinstance(values, (list, tuple)) or len(values)>maximum:
        raise ValueError('roster words need a bounded list or tuple')
    if any(type(w) is not int or not 1<=w<=3060 for w in values):
        raise ValueError('roster word must be an integer1..3060')
    result=tuple(values)
    if len(set(result))!=len(result):
        raise ValueError('roster words must be distinct')
    return result


@dataclass(frozen=True)
class Promotion:
    incoming: int
    displaced: int
    squad_index: int
    pool_index: int


@dataclass(frozen=True)
class ExtendedRoster:
    members: tuple

    def __post_init__(self):
        members=_words(self.members)
        if not 20<=len(members)<=24:
            raise ValueError('a selected extended roster needs20..24 members')
        object.__setattr__(self,'members',members)

    @classmethod
    def from_squads(cls, core, pool, extras=()):
        core=_words(core,20);pool=_words(pool,80);extras=_words(extras,4)
        if len(core)!=20 or set(core)&set(pool):
            raise ValueError('native twenty and made pool must be distinct')
        if not set(extras)<=set(pool):
            raise ValueError('additional members must belong to the made pool')
        return cls(core+extras)

    def _current(self, core):
        core=_words(core,20)
        if len(core)!=20 or not set(core)<=set(self.members):
            raise ValueError('current native twenty differs from selected membership')
        return core

    def squad(self, core):
        core=self._current(core)
        return core+tuple(w for w in self.members if w not in core)

    def bench(self, core):
        return self.squad(core)[11:]

    def promotion(self, incoming, core, pool, unavailable=()):
        core=self._current(core);pool=_words(pool,80)
        if type(incoming) is not int or incoming not in self.members:
            raise ValueError('incoming player is outside the selected roster')
        if set(core)&set(pool):
            raise ValueError('native twenty overlaps its made pool')
        if incoming in core:
            return None
        if incoming not in pool:
            raise ValueError('additional player no longer belongs to the made pool')
        unavailable=_words(unavailable,9)
        if not set(unavailable)<=set(core[11:]):
            raise ValueError('unavailable preference needs current native bench words')
        choices=[i for i in range(19,10,-1) if core[i] in unavailable]
        index=choices[0] if choices else 19
        return Promotion(incoming,core[index],index,pool.index(incoming))

    def replaced(self, outgoing, incoming, current_core):
        if (type(outgoing) is not int or outgoing not in self.members
                or type(incoming) is not int or not 1<=incoming<=3060
                or outgoing==incoming):
            raise ValueError('replacement needs distinct valid selected/outside words')
        if incoming in self.members:
            self._current(current_core)
            return self
        core=_words(current_core,20)
        if len(core)!=20 or incoming not in core or outgoing in core:
            raise ValueError('replacement must have been made in the native twenty')
        changed=list(self.members);changed[changed.index(outgoing)]=incoming
        result=ExtendedRoster(tuple(changed));result._current(core)
        return result
