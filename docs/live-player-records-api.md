# Opt-in live player records at decisions

[designed: #682, goal2#611] `Match(..., live_players=True)` includes `player_records` in
existing decision data: `[[player_word, record_hex], ...]`, in the current managed squad's
order (eleven then bench). Each lowercase hex string encodes one complete20-byte current
record, copied from guest memory. Withdrawn/bench players are included. The default and
explicitFalse omit the option from saved opts and retain the legacy decision payload.

[confirmed: F008, original1771:42BC/3827] The original card reads records through DS:A91B,
with PLAYER_SIZE0x14; energy is byte+0x0E, confidence+0x0C, status+0x10 and performance
the word+0x12. A saved career record is not a substitute for that current match record.
This API exports the source bytes; the consumer's existing decoder interprets them.

[derived: match.py _decide] The snapshot follows the existing flush and uses memory reads
before the existing decision stop. It adds no guest instruction or game-state write.
The opt-in is stored only whenTrue, retained by the ordinary checkpoint codec, and must
be a boolean in both a constructor request and a checkpoint header. All existing menu,
edit-only and illegal-substitution guards are unchanged.

[designed: #682] The intended consumer requests this data explicitly, validates bounded
record/word membership and uses it as a read-only card overlay. Pending UI edits remain
separate; no career state or accepted substitution is replaced by a display snapshot.
Goal2 adoption/wire/UI changes follow accepted upstream delivery. They are not supplied
by this upstream API alone. Private natural player-record bytes are not committed as
proof outputs: source-bound hashes/counts/equality results are sufficient public receipts.
