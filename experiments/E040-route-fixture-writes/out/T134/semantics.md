# T134 original roster semantics

[confirmed: F031/F012/F010, b3c64e18 named views; producer/fixture/source hashes in receipt-v2.json]
DEA6 swaps two word-list entries at 214B:007B. Its return DF29 precedes the
C1E branch: 52CC when not set up, 230C otherwise. Both sort starters and bench
independently. E022 has a separate in-match XI/bench restriction.

[confirmed: receipt-v2.json, actual original and PyPy held entry]
The same-position starter pair (123,124) stays reordered; differing positions
(121,122) are sorted back. In both cases the exact intermediate word swap was
observed before sorting. The bench/pool case (140,2564) leaves the XI intact
but sorts the incoming keeper into the bench, instead of retaining the model's
naive replacement index. Fresh decisions expose the actual guest order.

[designed: T134 API] Full-squad/made-pool membership is validated on copied
lists for the complete batch, before consumption. Ordinary in-match rules stay
unchanged. A word-swap witness is required even when final membership or visible
order is unchanged. There is no guest memory/opts patch or forced unsorted order.

The native original and PyPy tests compare lists, exact keys, events and draw
trace; supported saved/replayed boundaries compare full memory and all16 inside
PyPy. First-minute raw cross-backend identity is not claimed; the broader
T132/#709 Prover obligation remains separate. No comparison mask was added.
