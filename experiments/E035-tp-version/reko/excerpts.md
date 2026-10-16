# Reko 0.12.5 on the unpacked GOAL.EXE: excerpts (derived from the original; the project is private, rule 18)

Run: `dotnet decompile.dll GOAL.EXE` (CmdLine-0.12.5-x64 release zip, net8.0 runtime unpacked into a scratch directory; no flags: it detected MS-DOS real mode itself), about 66 s, 20 MB of output (not committed).
Input: GOAL.unp.exe sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
Reko loads the image at segment 0800, so 23E4 appears as 2BE4 and 214B as 294B.

Run log: one procedure failed to rewrite to C (fn0800_00E2: "Collection was modified", in the structure analysis); one "Stopping value propagation after iterating 10000 times" (fn0F91_384C); many "Warning: Selector 0000/0040 has no known segment" (BIOS data area accesses).

Observed in the first excerpt: Reko's scan loop compares `es_12->*di_172` a second time after `++di_172` (the original `repne scasb` compares before the increment), and the `memcmp` is its reading of `repe cmpsb`; Ghidra's counterpart does the compare before the increment. Types come out as anonymous `Eq_NNN`.

## Str Pos, 23E4:06E3 (Ghidra: static/goal-exe/decompiled/seg_23E4_01.c line 851)
```c
word16 fn2BE4_06E3(Eq_14 ptrArg04, Eq_14 ptrArg08)
{
	word16 wArg04_116 = (word16) ptrArg04;
	struct Eq_86716 * ds_21 = SLICE(ptrArg08, selector, 16);
	word16 si_22 = (word16) ptrArg08;
	struct Eq_86720 * es_12 = SLICE(ptrArg04, selector, 16);
	word16 di_13 = (word16) ptrArg04;
	uint16 cx_19 = (uint16) ptrArg04.u4->t0000.u0.u1;
	word16 ax_126;
	if (cx_19 != 0x00)
	{
		Eq_14 al_23;
		al_23.u1 = ptrArg08.u4->t0000.u0.u1;
		byte Eq_86720::* di_172 = di_13 + 0x01;
		<unknown>* si_24 = si_22 + 1;
		bool v30_108 = al_23 != 0x01;
		if (al_23 < 0x01)
		{
l2BE4_0725:
			ax_126 = di_172 - wArg04_116;
			return ax_126;
		}
		if (al_23 <= 0x01)
		{
			Eq_14 al_60;
			al_60.u1 = ptrArg08.u4->t0001.u1;
			while (cx_19 != 0x00)
			{
				v30_108 = al_60 != es_12->*di_172;
				++di_172;
				--cx_19;
				if (al_60 != es_12->*di_172)
					break;
			}
			if (!v30_108)
			{
				--di_172;
				goto l2BE4_0725;
			}
		}
		else
		{
			uint16 ax_30 = (uint16) al_23;
			uint16 dx_31 = cx_19 - ax_30;
			if (dx_31 >= 0x00)
			{
				uint16 dx_34 = dx_31 + 0x01;
				do
```

## LCG step, 214B:0688 (the game own unit)
```c
word16 fn294B_0688(Eq_14 wArg04, uint16 * ptrArg06)
{
	uint16 ax_20 = *ptrArg06;
	*ptrArg06 = ax_20 * 31421 + 0x1B0F;
	return SLICE(wArg04 *32 (ax_20 * 31421 + 0x1B0F), word16, 16) + 0x01;
}
```

## Real multiply, 23E4:0A52 (register-argument routine; first 40 lines)
```c
bool fn2BE4_0A52(byte al, bu8 ah, word16 cx, Eq_7883 dx, Eq_7883 bx, Eq_7883 si, Eq_7883 di, word16 & axOut, word16 & dxOut, word16 & bxOut)
{
	word16 bx_289;
	word16 dx_291;
	word16 ax_288;
	word16 bx_24;
	word16 dx_25;
	word16 ax_23;
	word16 bx_11;
	word16 dx_12;
	word16 ax_10;
	uint8 cl = (byte) cx;
	bu8 ch = SLICE(cx, byte, 8);
	if (al == 0x00)
	{
		Eq_87375 C_14 = fn2BE4_0A4F(out ax_10, out dx_12, out bx_11);
		axOut = ax_10;
		dxOut = dx_12;
		bxOut = bx_11;
		return C_14 != 0x00;
	}
	if (cl == 0x00)
	{
		Eq_87375 C_27 = fn2BE4_0A4F(out ax_23, out dx_25, out bx_24);
		axOut = ax_23;
		dxOut = dx_25;
		bxOut = bx_24;
		return C_27 != 0x00;
	}
	uint16 dh_dl_299 = SEQ(SLICE(dx ^ di, byte, 8) & 0x80, al) + (uint16) cl;
	uint16 bp_213 = dx | 0x8000;
	uint16 di_212 = di | 0x8000;
	uint16 ax_107 = SEQ(ah, 0x00);
	Eq_7883 dx_202;
	ui32 ax_bx_379;
	if (ah != 0x00 || bx != 0x00)
	{
		uint16 cx_94 = SEQ(ch, 0x00);
		if (ch != 0x00 || si != 0x00)
		{
```
