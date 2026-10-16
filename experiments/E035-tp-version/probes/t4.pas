program t4;
uses Crt, Dos;
type
  TScr = array[0..1999] of word;
  TRec = record a: integer; b: real; c: string[20]; end;
  PRec = ^TRec;
  TSet = set of 0..40;
var
  f: file; t: text; fr: file of TRec; r: TRec; p: PRec;
  s, s2: string; i, j: integer; l: longint; x, y: real; w: word; b: byte;
  sa, sb: TScr; st: TSet; buf: array[0..1023] of byte; c: char;
  h, m, sec, hund: word; reg: registers; sr: SearchRec; ev: string; yy, mo, dd, dw: word;
begin
  sa := sb; Move(sa, sb, 4000); if s < s2 then i := 1; l := MemL[$B800:0];
  Randomize; i := Random(100); x := Random;
  s := 'abc'; s2 := s + 'def'; s2 := Copy(s2, 2, 3); Delete(s2, 1, 1); Insert('zz', s2, 1);
  i := Pos('c', s2); Str(x:8:3, s); Val(s, y, j); s := UpCase(s[1]) + s;
  x := Sqrt(x) + Sin(y) * Cos(x) + Exp(y) - Ln(x + 1) + ArcTan(x) + Int(x) + Frac(y);
  l := Round(x); i := Trunc(y); x := Abs(x) + Sqr(y) + Pi;
  st := [1, 2, 3, 40]; if i in st then st := st + [5] - [2];
  if st <= [1..40] then Inc(i);
  Assign(f, 'x.dat'); {$I-} Reset(f, 1); {$I+} if IOResult <> 0 then Rewrite(f, 1);
  BlockRead(f, buf, 1024, w); BlockWrite(f, buf, 1024, w); Seek(f, 100); l := FileSize(f); Close(f);
  Assign(t, 'x.txt'); Reset(t); while not Eof(t) do begin ReadLn(t, s); WriteLn(s, i:5, x:8:2); end; Close(t);
  Assign(fr, 'y.dat'); Rewrite(fr); Write(fr, r); Close(fr);
  New(p); p^.a := 1; Dispose(p); GetMem(p, 100); FreeMem(p, 100);
  FillChar(buf, 1024, 0); Move(buf, buf[10], 100);
  c := ReadKey; GotoXY(1, 2); TextColor(14); ClrScr; Delay(100); Sound(440); NoSound;
  GetTime(h, m, sec, hund); reg.ax := 0; Intr($10, reg);
  Write(l, ' ', x, ' ', i:3, ' ', c); WriteLn(MemAvail, MaxAvail, ParamCount, ParamStr(1));
  case i of 1: i := 2; 3: i := 4; end;
  FindFirst('*.*', AnyFile, sr); while DosError = 0 do FindNext(sr);
  ev := GetEnv('PATH'); GetDate(yy, mo, dd, dw); SetTime(h, m, sec, hund);
  SwapVectors; Exec('COMMAND.COM', ''); SwapVectors; WriteLn(DosExitCode, ev);
  Halt(l);
end.
