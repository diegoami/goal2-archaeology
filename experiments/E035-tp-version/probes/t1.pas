program t1;
uses Crt, Dos;
var i: integer; s: string;
begin
  s := 'hello';
  for i := 1 to 3 do WriteLn(s, i);
  Halt(0);
end.
