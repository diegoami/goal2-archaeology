; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 22 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:DAF8  (found by: call, far)
sub_DAF8:
DAF8  55              push bp
DAF9  89 E5           mov bp, sp
DAFB  83 EC 02        sub sp, 2
DAFE  9A FC 55 71 17  call far 1771:55FC
DB03  08 C0           or al, al
DB05  74 1F           je 0xdb26
DB07  FF 76 06        push word ptr [bp + 6]
DB0A  A1 43 9B        mov ax, word ptr [0x9b43]
DB0D  B1 03           mov cl, 3
DB0F  D3 E0           shl ax, cl
DB11  C4 3E 2B A9     les di, ptr [0xa92b]
DB15  03 F8           add di, ax
DB17  81 C7 F8 FF     add di, 0xfff8
DB1B  06              push es
DB1C  57              push di
DB1D  9A 38 5A 71 17  call far 1771:5A38
DB22  08 C0           or al, al
DB24  75 04           jne 0xdb2a
loc_DB26:
DB26  B0 00           mov al, 0
DB28  EB 02           jmp 0xdb2c
loc_DB2A:
DB2A  B0 01           mov al, 1
loc_DB2C:
DB2C  88 46 FF        mov byte ptr [bp - 1], al
DB2F  8A 46 FF        mov al, byte ptr [bp - 1]
DB32  89 EC           mov sp, bp
DB34  5D              pop bp
DB35  CA 02 00        retf 2

; ---- routine 0791:DB38  (found by: call, far)
sub_DB38:
DB38  55              push bp
DB39  89 E5           mov bp, sp
DB3B  83 EC 04        sub sp, 4
DB3E  C6 46 FF 00     mov byte ptr [bp - 1], 0
DB42  FF 76 06        push word ptr [bp + 6]
DB45  0E              push cs
DB46  E8 AF FF        call 0xdaf8
DB49  08 C0           or al, al
DB4B  75 03           jne 0xdb50
DB4D  E9 82 00        jmp 0xdbd2
loc_DB50:
DB50  C7 46 FD 24 00  mov word ptr [bp - 3], 0x24
loc_DB55:
DB55  83 7E FD 00     cmp word ptr [bp - 3], 0
DB59  76 31           jbe 0xdb8c
DB5B  8B 46 FD        mov ax, word ptr [bp - 3]
DB5E  D1 E0           shl ax, 1
DB60  8B C8           mov cx, ax
DB62  8B 46 06        mov ax, word ptr [bp + 6]
DB65  BA 48 00        mov dx, 0x48
DB68  F7 E2           mul dx
DB6A  C4 3E 2F A9     les di, ptr [0xa92f]
DB6E  03 F8           add di, ax
DB70  03 F9           add di, cx
DB72  26 8B 45 FE     mov ax, word ptr es:[di - 2]
DB76  B1 03           mov cl, 3
DB78  D3 E0           shl ax, cl
DB7A  C4 3E 2B A9     les di, ptr [0xa92b]
DB7E  03 F8           add di, ax
DB80  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
DB85  72 05           jb 0xdb8c
DB87  FF 4E FD        dec word ptr [bp - 3]
DB8A  EB C9           jmp 0xdb55
loc_DB8C:
DB8C  83 7E FD 00     cmp word ptr [bp - 3], 0
DB90  76 37           jbe 0xdbc9
DB92  FF 76 06        push word ptr [bp + 6]
DB95  8B 46 FD        mov ax, word ptr [bp - 3]
DB98  D1 E0           shl ax, 1
DB9A  8B C8           mov cx, ax
DB9C  8B 46 06        mov ax, word ptr [bp + 6]
DB9F  BA 48 00        mov dx, 0x48
DBA2  F7 E2           mul dx
DBA4  C4 3E 2F A9     les di, ptr [0xa92f]
DBA8  03 F8           add di, ax
DBAA  03 F9           add di, cx
DBAC  26 8B 45 FE     mov ax, word ptr es:[di - 2]
DBB0  B1 03           mov cl, 3
DBB2  D3 E0           shl ax, cl
DBB4  C4 3E 2B A9     les di, ptr [0xa92b]
DBB8  03 F8           add di, ax
DBBA  81 C7 F8 FF     add di, 0xfff8
DBBE  06              push es
DBBF  57              push di
DBC0  9A 38 5A 71 17  call far 1771:5A38
DBC5  08 C0           or al, al
DBC7  75 04           jne 0xdbcd
loc_DBC9:
DBC9  B0 00           mov al, 0
DBCB  EB 02           jmp 0xdbcf
loc_DBCD:
DBCD  B0 01           mov al, 1
loc_DBCF:
DBCF  88 46 FF        mov byte ptr [bp - 1], al
loc_DBD2:
DBD2  8A 46 FF        mov al, byte ptr [bp - 1]
DBD5  89 EC           mov sp, bp
DBD7  5D              pop bp
DBD8  CA 02 00        retf 2
; data (not reached as code), 31 bytes
DBDB                  pstr ' during finals'
DBEA                  pstr ' whilst on tour'

; ---- routine 0791:DBFA  (found by: call)
sub_DBFA:
DBFA  55              push bp
DBFB  89 E5           mov bp, sp
DBFD  81 EC 06 02     sub sp, 0x206
DC01  C4 3E 23 A9     les di, ptr [0xa923]
DC05  89 7E FB        mov word ptr [bp - 5], di
DC08  8C 46 FD        mov word ptr [bp - 3], es
DC0B  C4 7E FB        les di, ptr [bp - 5]
DC0E  26 8A 45 01     mov al, byte ptr es:[di + 1]
DC12  30 E4           xor ah, ah
DC14  C4 7E FB        les di, ptr [bp - 5]
DC17  03 F8           add di, ax
DC19  26 8A 45 13     mov al, byte ptr es:[di + 0x13]
DC1D  50              push ax
DC1E  8D BE FB FE     lea di, [bp - 0x105]
DC22  16              push ss
DC23  57              push di
DC24  BF 9C 0A        mov di, 0xa9c
DC27  1E              push ds
DC28  57              push di
DC29  9A 2A 06 E4 23  call far 23E4:062A
DC2E  BF DB DB        mov di, 0xdbdb
DC31  0E              push cs
DC32  57              push di
DC33  9A B7 06 E4 23  call far 23E4:06B7
DC38  9A 65 17 4B 21  call far 214B:1765
DC3D  08 C0           or al, al
DC3F  75 2B           jne 0xdc6c
DC41  FF 76 04        push word ptr [bp + 4]
DC44  0E              push cs
DC45  E8 F0 FE        call 0xdb38
DC48  50              push ax
DC49  8D BE FB FD     lea di, [bp - 0x205]
DC4D  16              push ss
DC4E  57              push di
DC4F  BF 9C 0A        mov di, 0xa9c
DC52  1E              push ds
DC53  57              push di
DC54  9A 2A 06 E4 23  call far 23E4:062A
DC59  BF EA DB        mov di, 0xdbea
DC5C  0E              push cs
DC5D  57              push di
DC5E  9A B7 06 E4 23  call far 23E4:06B7
DC63  9A 65 17 4B 21  call far 214B:1765
DC68  08 C0           or al, al
DC6A  74 04           je 0xdc70
loc_DC6C:
DC6C  B0 00           mov al, 0
DC6E  EB 02           jmp 0xdc72
loc_DC70:
DC70  B0 01           mov al, 1
loc_DC72:
DC72  88 46 FF        mov byte ptr [bp - 1], al
DC75  8A 46 FF        mov al, byte ptr [bp - 1]
DC78  89 EC           mov sp, bp
DC7A  5D              pop bp
DC7B  C2 02 00        ret 2

; ---- routine 0791:DC7E  (found by: call)
sub_DC7E:
DC7E  55              push bp
DC7F  89 E5           mov bp, sp
DC81  83 EC 12        sub sp, 0x12
DC84  C4 3E 23 A9     les di, ptr [0xa923]
DC88  89 7E F4        mov word ptr [bp - 0xc], di
DC8B  8C 46 F6        mov word ptr [bp - 0xa], es
DC8E  C4 7E F4        les di, ptr [bp - 0xc]
DC91  26 8A 45 01     mov al, byte ptr es:[di + 1]
DC95  30 E4           xor ah, ah
DC97  05 80 00        add ax, 0x80
DC9A  BA 03 00        mov dx, 3
DC9D  F7 E2           mul dx
DC9F  C4 3E 1F A9     les di, ptr [0xa91f]
DCA3  03 F8           add di, ax
DCA5  26 8A 05        mov al, byte ptr es:[di]
DCA8  30 E4           xor ah, ah
DCAA  89 46 F8        mov word ptr [bp - 8], ax
DCAD  FF 76 F8        push word ptr [bp - 8]
DCB0  E8 47 FF        call 0xdbfa
DCB3  08 C0           or al, al
DCB5  75 03           jne 0xdcba
DCB7  E9 0D 01        jmp 0xddc7
loc_DCBA:
DCBA  C7 46 FA 01 00  mov word ptr [bp - 6], 1
DCBF  EB 03           jmp 0xdcc4
loc_DCC1:
DCC1  FF 46 FA        inc word ptr [bp - 6]
loc_DCC4:
DCC4  8B 46 F8        mov ax, word ptr [bp - 8]
DCC7  BA BF 00        mov dx, 0xbf
DCCA  F7 E2           mul dx
DCCC  C4 3E 17 A9     les di, ptr [0xa917]
DCD0  03 F8           add di, ax
DCD2  89 7E F0        mov word ptr [bp - 0x10], di
DCD5  8C 46 F2        mov word ptr [bp - 0xe], es
DCD8  C7 46 FC 01 00  mov word ptr [bp - 4], 1
DCDD  EB 03           jmp 0xdce2
loc_DCDF:
DCDF  FF 46 FC        inc word ptr [bp - 4]
loc_DCE2:
DCE2  C4 7E F4        les di, ptr [bp - 0xc]
DCE5  26 8A 45 01     mov al, byte ptr es:[di + 1]
DCE9  30 E4           xor ah, ah
DCEB  8B F8           mov di, ax
DCED  D1 E7           shl di, 1
DCEF  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
DCF3  05 4F 00        add ax, 0x4f
DCF6  89 46 EE        mov word ptr [bp - 0x12], ax
DCF9  C4 7E F4        les di, ptr [bp - 0xc]
DCFC  26 8A 45 01     mov al, byte ptr es:[di + 1]
DD00  30 E4           xor ah, ah
DD02  8B F8           mov di, ax
DD04  D1 E7           shl di, 1
DD06  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
DD0A  3B 46 EE        cmp ax, word ptr [bp - 0x12]
DD0D  76 03           jbe 0xdd12
DD0F  E9 A3 00        jmp 0xddb5
loc_DD12:
DD12  89 46 FE        mov word ptr [bp - 2], ax
DD15  EB 03           jmp 0xdd1a
loc_DD17:
DD17  FF 46 FE        inc word ptr [bp - 2]
loc_DD1A:
DD1A  8B 46 FE        mov ax, word ptr [bp - 2]
DD1D  D1 E0           shl ax, 1
DD1F  C4 3E 27 A9     les di, ptr [0xa927]
DD23  03 F8           add di, ax
DD25  26 8B 05        mov ax, word ptr es:[di]
DD28  BA 14 00        mov dx, 0x14
DD2B  F7 E2           mul dx
DD2D  C4 3E 1B A9     les di, ptr [0xa91b]
DD31  03 F8           add di, ax
DD33  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
DD37  8B 46 FC        mov ax, word ptr [bp - 4]
DD3A  D1 E0           shl ax, 1
DD3C  C4 7E F0        les di, ptr [bp - 0x10]
DD3F  03 F8           add di, ax
DD41  26 8B 45 FE     mov ax, word ptr es:[di - 2]
DD45  BA 14 00        mov dx, 0x14
DD48  F7 E2           mul dx
DD4A  C4 3E 1B A9     les di, ptr [0xa91b]
DD4E  03 F8           add di, ax
DD50  26 8A 45 06     mov al, byte ptr es:[di + 6]
DD54  3A C1           cmp al, cl
DD56  75 52           jne 0xddaa
DD58  8B 46 FE        mov ax, word ptr [bp - 2]
DD5B  D1 E0           shl ax, 1
DD5D  C4 3E 27 A9     les di, ptr [0xa927]
DD61  03 F8           add di, ax
DD63  26 FF 35        push word ptr es:[di]
DD66  9A 7E 37 71 17  call far 1771:377E
DD6B  50              push ax
DD6C  8B 46 FC        mov ax, word ptr [bp - 4]
DD6F  D1 E0           shl ax, 1
DD71  C4 7E F0        les di, ptr [bp - 0x10]
DD74  03 F8           add di, ax
DD76  26 FF 75 FE     push word ptr es:[di - 2]
DD7A  9A 7E 37 71 17  call far 1771:377E
DD7F  5A              pop dx
DD80  3B C2           cmp ax, dx
DD82  73 26           jae 0xddaa
DD84  8B 46 FC        mov ax, word ptr [bp - 4]
DD87  D1 E0           shl ax, 1
DD89  C4 7E F0        les di, ptr [bp - 0x10]
DD8C  03 F8           add di, ax
DD8E  81 C7 FE FF     add di, 0xfffe
DD92  06              push es
DD93  57              push di
DD94  8B 46 FE        mov ax, word ptr [bp - 2]
DD97  D1 E0           shl ax, 1
DD99  C4 3E 27 A9     les di, ptr [0xa927]
DD9D  03 F8           add di, ax
DD9F  06              push es
DDA0  57              push di
DDA1  B8 02 00        mov ax, 2
DDA4  50              push ax
DDA5  9A 7B 00 4B 21  call far 214B:007B
loc_DDAA:
DDAA  8B 46 FE        mov ax, word ptr [bp - 2]
DDAD  3B 46 EE        cmp ax, word ptr [bp - 0x12]
DDB0  74 03           je 0xddb5
DDB2  E9 62 FF        jmp 0xdd17
loc_DDB5:
DDB5  83 7E FC 14     cmp word ptr [bp - 4], 0x14
DDB9  74 03           je 0xddbe
DDBB  E9 21 FF        jmp 0xdcdf
loc_DDBE:
DDBE  83 7E FA 02     cmp word ptr [bp - 6], 2
DDC2  74 03           je 0xddc7
DDC4  E9 FA FE        jmp 0xdcc1
loc_DDC7:
DDC7  89 EC           mov sp, bp
DDC9  5D              pop bp
DDCA  C3              ret

; ---- routine 0791:DDCB  (found by: call)
sub_DDCB:
DDCB  55              push bp
DDCC  89 E5           mov bp, sp
DDCE  83 EC 06        sub sp, 6
DDD1  C4 3E 23 A9     les di, ptr [0xa923]
DDD5  89 7E FA        mov word ptr [bp - 6], di
DDD8  8C 46 FC        mov word ptr [bp - 4], es
DDDB  C4 7E FA        les di, ptr [bp - 6]
DDDE  26 8A 45 01     mov al, byte ptr es:[di + 1]
DDE2  30 E4           xor ah, ah
DDE4  8B F8           mov di, ax
DDE6  D1 E7           shl di, 1
DDE8  8B 8D 18 6D     mov cx, word ptr [di + 0x6d18]
DDEC  C4 7E FA        les di, ptr [bp - 6]
DDEF  26 8A 45 01     mov al, byte ptr es:[di + 1]
DDF3  30 E4           xor ah, ah
DDF5  D1 E0           shl ax, 1
DDF7  C4 7E FA        les di, ptr [bp - 6]
DDFA  03 F8           add di, ax
DDFC  26 8B 55 5E     mov dx, word ptr es:[di + 0x5e]
DE00  C4 7E FA        les di, ptr [bp - 6]
DE03  26 8A 45 01     mov al, byte ptr es:[di + 1]
DE07  30 E4           xor ah, ah
DE09  D1 E0           shl ax, 1
DE0B  C4 7E FA        les di, ptr [bp - 6]
DE0E  03 F8           add di, ax
DE10  26 8B 45 52     mov ax, word ptr es:[di + 0x52]
DE14  03 C2           add ax, dx
DE16  03 C1           add ax, cx
DE18  2D 02 00        sub ax, 2
DE1B  89 46 FE        mov word ptr [bp - 2], ax
DE1E  8B 46 FE        mov ax, word ptr [bp - 2]
DE21  89 EC           mov sp, bp
DE23  5D              pop bp
DE24  C2 02 00        ret 2

; ---- routine 0791:DE27  (found by: call)
sub_DE27:
DE27  55              push bp
DE28  89 E5           mov bp, sp
DE2A  83 EC 02        sub sp, 2
DE2D  8B 7E 04        mov di, word ptr [bp + 4]
DE30  36 83 7D FB 01  cmp word ptr ss:[di - 5], 1
DE35  75 08           jne 0xde3f
DE37  A1 1B 0C        mov ax, word ptr [0xc1b]
DE3A  89 46 FE        mov word ptr [bp - 2], ax
DE3D  EB 09           jmp 0xde48
loc_DE3F:
DE3F  FF 76 04        push word ptr [bp + 4]
DE42  E8 86 FF        call 0xddcb
DE45  89 46 FE        mov word ptr [bp - 2], ax
loc_DE48:
DE48  8B 46 FE        mov ax, word ptr [bp - 2]
DE4B  89 EC           mov sp, bp
DE4D  5D              pop bp
DE4E  C2 02 00        ret 2

; ---- routine 0791:DE51  (found by: call)
sub_DE51:
DE51  55              push bp
DE52  89 E5           mov bp, sp
DE54  83 EC 04        sub sp, 4
DE57  83 7E 08 01     cmp word ptr [bp + 8], 1
DE5B  75 29           jne 0xde86
DE5D  8B 46 06        mov ax, word ptr [bp + 6]
DE60  D1 E0           shl ax, 1
DE62  8B C8           mov cx, ax
DE64  8B 7E 04        mov di, word ptr [bp + 4]
DE67  36 8B 45 06     mov ax, word ptr ss:[di + 6]
DE6B  BA BF 00        mov dx, 0xbf
DE6E  F7 E2           mul dx
DE70  C4 3E 17 A9     les di, ptr [0xa917]
DE74  03 F8           add di, ax
DE76  03 F9           add di, cx
DE78  26 8D 45 FE     lea ax, es:[di - 2]
DE7C  8C C2           mov dx, es
DE7E  89 46 FC        mov word ptr [bp - 4], ax
DE81  89 56 FE        mov word ptr [bp - 2], dx
DE84  EB 15           jmp 0xde9b
loc_DE86:
DE86  8B 46 06        mov ax, word ptr [bp + 6]
DE89  D1 E0           shl ax, 1
DE8B  C4 3E 27 A9     les di, ptr [0xa927]
DE8F  03 F8           add di, ax
DE91  89 F8           mov ax, di
DE93  8C C2           mov dx, es
DE95  89 46 FC        mov word ptr [bp - 4], ax
DE98  89 56 FE        mov word ptr [bp - 2], dx
loc_DE9B:
DE9B  C4 46 FC        les ax, ptr [bp - 4]
DE9E  8C C2           mov dx, es
DEA0  89 EC           mov sp, bp
DEA2  5D              pop bp
DEA3  C2 06 00        ret 6

; ---- routine 0791:DEA6  (found by: call)
sub_DEA6:
DEA6  55              push bp
DEA7  89 E5           mov bp, sp
DEA9  83 EC 04        sub sp, 4
DEAC  C4 3E 23 A9     les di, ptr [0xa923]
DEB0  89 7E FC        mov word ptr [bp - 4], di
DEB3  8C 46 FE        mov word ptr [bp - 2], es
DEB6  8B 7E 04        mov di, word ptr [bp + 4]
DEB9  36 83 7D FB 02  cmp word ptr ss:[di - 5], 2
DEBE  75 11           jne 0xded1
DEC0  8B 7E 04        mov di, word ptr [bp + 4]
DEC3  36 FF 75 06     push word ptr ss:[di + 6]
DEC7  E8 30 FD        call 0xdbfa
DECA  08 C0           or al, al
DECC  75 03           jne 0xded1
DECE  E9 08 01        jmp 0xdfd9
loc_DED1:
DED1  8B 7E 04        mov di, word ptr [bp + 4]
DED4  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
DED9  74 69           je 0xdf44
DEDB  8B 7E 04        mov di, word ptr [bp + 4]
DEDE  36 C6 45 FF 00  mov byte ptr ss:[di - 1], 0
DEE3  8B 7E 04        mov di, word ptr [bp + 4]
DEE6  31 C0           xor ax, ax
DEE8  36 89 45 F5     mov word ptr ss:[di - 0xb], ax
DEEC  8B 7E 04        mov di, word ptr [bp + 4]
DEEF  36 FF 75 FB     push word ptr ss:[di - 5]
DEF3  FF 76 04        push word ptr [bp + 4]
DEF6  E8 2E FF        call 0xde27
DEF9  50              push ax
DEFA  FF 76 04        push word ptr [bp + 4]
DEFD  E8 51 FF        call 0xde51
DF00  89 C7           mov di, ax
DF02  8E C2           mov es, dx
DF04  06              push es
DF05  57              push di
DF06  8B 7E 04        mov di, word ptr [bp + 4]
DF09  36 FF 75 F9     push word ptr ss:[di - 7]
DF0D  8B 7E 04        mov di, word ptr [bp + 4]
DF10  36 FF 75 F7     push word ptr ss:[di - 9]
DF14  FF 76 04        push word ptr [bp + 4]
DF17  E8 37 FF        call 0xde51
DF1A  89 C7           mov di, ax
DF1C  8E C2           mov es, dx
DF1E  06              push es
DF1F  57              push di
DF20  B8 02 00        mov ax, 2
DF23  50              push ax
DF24  9A 7B 00 4B 21  call far 214B:007B
DF29  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
DF2E  74 05           je 0xdf35
DF30  E8 D9 43        call 0x1230c
DF33  EB 0C           jmp 0xdf41
loc_DF35:
DF35  8B 7E 04        mov di, word ptr [bp + 4]
DF38  36 FF 75 06     push word ptr ss:[di + 6]
DF3C  9A CC 52 71 17  call far 1771:52CC
loc_DF41:
DF41  E9 95 00        jmp 0xdfd9
loc_DF44:
DF44  8B 7E 04        mov di, word ptr [bp + 4]
DF47  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
DF4C  74 03           je 0xdf51
DF4E  E9 88 00        jmp 0xdfd9
loc_DF51:
DF51  8B 7E 04        mov di, word ptr [bp + 4]
DF54  36 FF 75 FB     push word ptr ss:[di - 5]
DF58  FF 76 04        push word ptr [bp + 4]
DF5B  E8 C9 FE        call 0xde27
DF5E  50              push ax
DF5F  FF 76 04        push word ptr [bp + 4]
DF62  E8 EC FE        call 0xde51
DF65  89 C7           mov di, ax
DF67  8E C2           mov es, dx
DF69  26 83 3D 00     cmp word ptr es:[di], 0
DF6D  74 6A           je 0xdfd9
DF6F  FF 76 04        push word ptr [bp + 4]
DF72  E8 B2 FE        call 0xde27
DF75  8B 7E 04        mov di, word ptr [bp + 4]
DF78  36 89 45 F7     mov word ptr ss:[di - 9], ax
DF7C  8B 7E 04        mov di, word ptr [bp + 4]
DF7F  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
DF83  8B 7E 04        mov di, word ptr [bp + 4]
DF86  36 89 45 F9     mov word ptr ss:[di - 7], ax
DF8A  8B 7E 04        mov di, word ptr [bp + 4]
DF8D  36 83 7D FB 02  cmp word ptr ss:[di - 5], 2
DF92  75 34           jne 0xdfc8
DF94  C4 7E FC        les di, ptr [bp - 4]
DF97  26 8A 45 01     mov al, byte ptr es:[di + 1]
DF9B  30 E4           xor ah, ah
DF9D  D1 E0           shl ax, 1
DF9F  C4 7E FC        les di, ptr [bp - 4]
DFA2  03 F8           add di, ax
DFA4  26 8B 55 52     mov dx, word ptr es:[di + 0x52]
DFA8  C4 7E FC        les di, ptr [bp - 4]
DFAB  26 8A 45 01     mov al, byte ptr es:[di + 1]
DFAF  30 E4           xor ah, ah
DFB1  D1 E0           shl ax, 1
DFB3  C4 7E FC        les di, ptr [bp - 4]
DFB6  03 F8           add di, ax
DFB8  26 8B 45 5E     mov ax, word ptr es:[di + 0x5e]
DFBC  03 C2           add ax, dx
DFBE  48              dec ax
DFBF  8B 7E 04        mov di, word ptr [bp + 4]
DFC2  36 89 45 F5     mov word ptr ss:[di - 0xb], ax
DFC6  EB 09           jmp 0xdfd1
loc_DFC8:
DFC8  8B 7E 04        mov di, word ptr [bp + 4]
DFCB  31 C0           xor ax, ax
DFCD  36 89 45 F5     mov word ptr ss:[di - 0xb], ax
loc_DFD1:
DFD1  8B 7E 04        mov di, word ptr [bp + 4]
DFD4  36 C6 45 FF 01  mov byte ptr ss:[di - 1], 1
loc_DFD9:
DFD9  89 EC           mov sp, bp
DFDB  5D              pop bp
DFDC  C2 02 00        ret 2
; data (not reached as code), 67 bytes
DFDF                  pstr 'There is no player here'
DFF7                  pstr 'Illegal substitution'
E00C                  pstr ' cannot play'
E019                  pstr 'Nice try'

; ---- routine 0791:E022  (found by: call)
sub_E022:
E022  55              push bp
E023  89 E5           mov bp, sp
E025  81 EC 08 01     sub sp, 0x108
E029  8B 7E 04        mov di, word ptr [bp + 4]
E02C  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
E031  75 5C           jne 0xe08f
E033  8B 7E 04        mov di, word ptr [bp + 4]
E036  36 FF 75 FB     push word ptr ss:[di - 5]
E03A  FF 76 04        push word ptr [bp + 4]
E03D  E8 E7 FD        call 0xde27
E040  50              push ax
E041  FF 76 04        push word ptr [bp + 4]
E044  E8 0A FE        call 0xde51
E047  89 C7           mov di, ax
E049  8E C2           mov es, dx
E04B  26 83 3D 00     cmp word ptr es:[di], 0
E04F  74 04           je 0xe055
E051  B0 00           mov al, 0
E053  EB 02           jmp 0xe057
loc_E055:
E055  B0 01           mov al, 1
loc_E057:
E057  50              push ax
E058  BF DF DF        mov di, 0xdfdf
E05B  0E              push cs
E05C  57              push di
E05D  9A 65 17 4B 21  call far 214B:1765
E062  08 C0           or al, al
E064  74 03           je 0xe069
E066  E9 31 02        jmp 0xe29a
loc_E069:
E069  FF 76 04        push word ptr [bp + 4]
E06C  E8 B8 FD        call 0xde27
E06F  8B 7E 04        mov di, word ptr [bp + 4]
E072  36 89 45 F7     mov word ptr ss:[di - 9], ax
E076  8B 7E 04        mov di, word ptr [bp + 4]
E079  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
E07D  8B 7E 04        mov di, word ptr [bp + 4]
E080  36 89 45 F9     mov word ptr ss:[di - 7], ax
E084  8B 7E 04        mov di, word ptr [bp + 4]
E087  36 C6 45 FF 01  mov byte ptr ss:[di - 1], 1
E08C  E9 0B 02        jmp 0xe29a
loc_E08F:
E08F  8B 7E 04        mov di, word ptr [bp + 4]
E092  36 C6 45 FF 00  mov byte ptr ss:[di - 1], 0
E097  8B 7E 04        mov di, word ptr [bp + 4]
E09A  36 83 7D F7 0C  cmp word ptr ss:[di - 9], 0xc
E09F  72 04           jb 0xe0a5
E0A1  B0 00           mov al, 0
E0A3  EB 02           jmp 0xe0a7
loc_E0A5:
E0A5  B0 01           mov al, 1
loc_E0A7:
E0A7  8A D0           mov dl, al
E0A9  83 3E 1B 0C 0C  cmp word ptr [0xc1b], 0xc
E0AE  72 04           jb 0xe0b4
E0B0  B0 00           mov al, 0
E0B2  EB 02           jmp 0xe0b6
loc_E0B4:
E0B4  B0 01           mov al, 1
loc_E0B6:
E0B6  3A C2           cmp al, dl
E0B8  74 04           je 0xe0be
E0BA  B0 00           mov al, 0
E0BC  EB 02           jmp 0xe0c0
loc_E0BE:
E0BE  B0 01           mov al, 1
loc_E0C0:
E0C0  50              push ax
E0C1  BF F7 DF        mov di, 0xdff7
E0C4  0E              push cs
E0C5  57              push di
E0C6  9A 65 17 4B 21  call far 214B:1765
E0CB  08 C0           or al, al
E0CD  74 03           je 0xe0d2
E0CF  E9 C8 01        jmp 0xe29a
loc_E0D2:
E0D2  A1 1B 0C        mov ax, word ptr [0xc1b]
E0D5  31 D2           xor dx, dx
E0D7  52              push dx
E0D8  50              push ax
E0D9  8B 7E 04        mov di, word ptr [bp + 4]
E0DC  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
E0E0  31 D2           xor dx, dx
E0E2  52              push dx
E0E3  50              push ax
E0E4  9A 56 0D 4B 21  call far 214B:0D56
E0E9  89 46 FE        mov word ptr [bp - 2], ax
E0EC  A1 1B 0C        mov ax, word ptr [0xc1b]
E0EF  31 D2           xor dx, dx
E0F1  52              push dx
E0F2  50              push ax
E0F3  8B 7E 04        mov di, word ptr [bp + 4]
E0F6  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
E0FA  31 D2           xor dx, dx
E0FC  52              push dx
E0FD  50              push ax
E0FE  9A 1C 0D 4B 21  call far 214B:0D1C
E103  89 46 FC        mov word ptr [bp - 4], ax
E106  8B 7E 04        mov di, word ptr [bp + 4]
E109  36 8B 45 06     mov ax, word ptr ss:[di + 6]
E10D  BA BF 00        mov dx, 0xbf
E110  F7 E2           mul dx
E112  C4 3E 17 A9     les di, ptr [0xa917]
E116  03 F8           add di, ax
E118  89 7E F8        mov word ptr [bp - 8], di
E11B  8C 46 FA        mov word ptr [bp - 6], es
E11E  8B 46 FE        mov ax, word ptr [bp - 2]
E121  D1 E0           shl ax, 1
E123  C4 7E F8        les di, ptr [bp - 8]
E126  03 F8           add di, ax
E128  26 FF 75 FE     push word ptr es:[di - 2]
E12C  9A 16 32 71 17  call far 1771:3216
E131  50              push ax
E132  8D BE F8 FE     lea di, [bp - 0x108]
E136  16              push ss
E137  57              push di
E138  8B 46 FE        mov ax, word ptr [bp - 2]
E13B  D1 E0           shl ax, 1
E13D  C4 7E F8        les di, ptr [bp - 8]
E140  03 F8           add di, ax
E142  26 8B 45 FE     mov ax, word ptr es:[di - 2]
E146  BA 0B 00        mov dx, 0xb
E149  F7 E2           mul dx
E14B  C4 3E 6C 9B     les di, ptr [0x9b6c]
E14F  03 F8           add di, ax
E151  06              push es
E152  57              push di
E153  9A 2A 06 E4 23  call far 23E4:062A
E158  BF 0C E0        mov di, 0xe00c
E15B  0E              push cs
E15C  57              push di
E15D  9A B7 06 E4 23  call far 23E4:06B7
E162  9A 65 17 4B 21  call far 214B:1765
E167  08 C0           or al, al
E169  75 38           jne 0xe1a3
E16B  B8 06 00        mov ax, 6
E16E  50              push ax
E16F  8B 46 FC        mov ax, word ptr [bp - 4]
E172  D1 E0           shl ax, 1
E174  C4 7E F8        les di, ptr [bp - 8]
E177  03 F8           add di, ax
E179  26 8B 45 FE     mov ax, word ptr es:[di - 2]
E17D  BA 14 00        mov dx, 0x14
E180  F7 E2           mul dx
E182  C4 3E 1B A9     les di, ptr [0xa91b]
E186  03 F8           add di, ax
E188  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
E18C  30 E4           xor ah, ah
E18E  50              push ax
E18F  9A 57 0C 4B 21  call far 214B:0C57
E194  50              push ax
E195  BF 19 E0        mov di, 0xe019
E198  0E              push cs
E199  57              push di
E19A  9A 65 17 4B 21  call far 214B:1765
E19F  08 C0           or al, al
E1A1  74 03           je 0xe1a6
loc_E1A3:
E1A3  E9 F4 00        jmp 0xe29a
loc_E1A6:
E1A6  8B 46 FE        mov ax, word ptr [bp - 2]
E1A9  D1 E0           shl ax, 1
E1AB  C4 7E F8        les di, ptr [bp - 8]
E1AE  03 F8           add di, ax
E1B0  81 C7 FE FF     add di, 0xfffe
E1B4  06              push es
E1B5  57              push di
E1B6  8B 46 FC        mov ax, word ptr [bp - 4]
E1B9  D1 E0           shl ax, 1
E1BB  C4 7E F8        les di, ptr [bp - 8]
E1BE  03 F8           add di, ax
E1C0  81 C7 FE FF     add di, 0xfffe
E1C4  06              push es
E1C5  57              push di
E1C6  B8 02 00        mov ax, 2
E1C9  50              push ax
E1CA  9A 7B 00 4B 21  call far 214B:007B
E1CF  8B 46 FE        mov ax, word ptr [bp - 2]
E1D2  8B C8           mov cx, ax
E1D4  8B 7E 04        mov di, word ptr [bp + 4]
E1D7  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E1DB  98              cwde
E1DC  BA 14 00        mov dx, 0x14
E1DF  F7 E2           mul dx
E1E1  8B F8           mov di, ax
E1E3  03 F9           add di, cx
E1E5  81 C7 07 9B     add di, 0x9b07
E1E9  1E              push ds
E1EA  57              push di
E1EB  8B 46 FC        mov ax, word ptr [bp - 4]
E1EE  8B C8           mov cx, ax
E1F0  8B 7E 04        mov di, word ptr [bp + 4]
E1F3  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E1F7  98              cwde
E1F8  BA 14 00        mov dx, 0x14
E1FB  F7 E2           mul dx
E1FD  8B F8           mov di, ax
E1FF  03 F9           add di, cx
E201  81 C7 07 9B     add di, 0x9b07
E205  1E              push ds
E206  57              push di
E207  B8 01 00        mov ax, 1
E20A  50              push ax
E20B  9A 7B 00 4B 21  call far 214B:007B
E210  8B 46 FC        mov ax, word ptr [bp - 4]
E213  D1 E0           shl ax, 1
E215  8B C8           mov cx, ax
E217  8B 7E 04        mov di, word ptr [bp + 4]
E21A  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E21E  98              cwde
E21F  BA 28 00        mov dx, 0x28
E222  F7 E2           mul dx
E224  8B F8           mov di, ax
E226  03 F9           add di, cx
E228  31 C0           xor ax, ax
E22A  89 85 3E 9A     mov word ptr [di - 0x65c2], ax
E22E  8B 46 FE        mov ax, word ptr [bp - 2]
E231  D1 E0           shl ax, 1
E233  8B C8           mov cx, ax
E235  8B 7E 04        mov di, word ptr [bp + 4]
E238  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E23C  98              cwde
E23D  BA 28 00        mov dx, 0x28
E240  F7 E2           mul dx
E242  8B F8           mov di, ax
E244  03 F9           add di, cx
E246  81 C7 3E 9A     add di, 0x9a3e
E24A  1E              push ds
E24B  57              push di
E24C  8B 46 FC        mov ax, word ptr [bp - 4]
E24F  D1 E0           shl ax, 1
E251  8B C8           mov cx, ax
E253  8B 7E 04        mov di, word ptr [bp + 4]
E256  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E25A  98              cwde
E25B  BA 28 00        mov dx, 0x28
E25E  F7 E2           mul dx
E260  8B F8           mov di, ax
E262  03 F9           add di, cx
E264  81 C7 3E 9A     add di, 0x9a3e
E268  1E              push ds
E269  57              push di
E26A  B8 02 00        mov ax, 2
E26D  50              push ax
E26E  9A 7B 00 4B 21  call far 214B:007B
E273  8B 7E 04        mov di, word ptr [bp + 4]
E276  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E27A  50              push ax
E27B  8B 7E 04        mov di, word ptr [bp + 4]
E27E  36 8A 45 FD     mov al, byte ptr ss:[di - 3]
E282  98              cwde
E283  8B F8           mov di, ax
E285  8A 85 68 06     mov al, byte ptr [di + 0x668]
E289  30 E4           xor ah, ah
E28B  03 46 FC        add ax, word ptr [bp - 4]
E28E  50              push ax
E28F  FF 76 FE        push word ptr [bp - 2]
E292  E8 47 E3        call 0xc5dc
E295  C6 06 40 9B 00  mov byte ptr [0x9b40], 0
loc_E29A:
E29A  89 EC           mov sp, bp
E29C  5D              pop bp
E29D  C2 02 00        ret 2

; ---- routine 0791:E2A0  (found by: call)
sub_E2A0:
E2A0  55              push bp
E2A1  89 E5           mov bp, sp
E2A3  BF 40 48        mov di, 0x4840
E2A6  1E              push ds
E2A7  57              push di
E2A8  BF 6E A9        mov di, 0xa96e
E2AB  1E              push ds
E2AC  57              push di
E2AD  9A 29 03 4B 21  call far 214B:0329
E2B2  83 3E 1B 0C 0B  cmp word ptr [0xc1b], 0xb
E2B7  76 11           jbe 0xe2ca
E2B9  BF 40 47        mov di, 0x4740
E2BC  1E              push ds
E2BD  57              push di
E2BE  BF 6E A9        mov di, 0xa96e
E2C1  1E              push ds
E2C2  57              push di
E2C3  9A 29 03 4B 21  call far 214B:0329
E2C8  EB 16           jmp 0xe2e0
loc_E2CA:
E2CA  83 3E 1B 0C 0C  cmp word ptr [0xc1b], 0xc
E2CF  73 0F           jae 0xe2e0
E2D1  BF 20 47        mov di, 0x4720
E2D4  1E              push ds
E2D5  57              push di
E2D6  BF 6E A9        mov di, 0xa96e
E2D9  1E              push ds
E2DA  57              push di
E2DB  9A 29 03 4B 21  call far 214B:0329
loc_E2E0:
E2E0  89 EC           mov sp, bp
E2E2  5D              pop bp
E2E3  C2 02 00        ret 2

; ---- routine 0791:E2E6  (found by: call)
sub_E2E6:
E2E6  55              push bp
E2E7  89 E5           mov bp, sp
E2E9  83 EC 0E        sub sp, 0xe
E2EC  C4 3E 23 A9     les di, ptr [0xa923]
E2F0  89 7E F8        mov word ptr [bp - 8], di
E2F3  8C 46 FA        mov word ptr [bp - 6], es
E2F6  8B 7E 04        mov di, word ptr [bp + 4]
E2F9  36 8B 45 06     mov ax, word ptr ss:[di + 6]
E2FD  BA BF 00        mov dx, 0xbf
E300  F7 E2           mul dx
E302  C4 3E 17 A9     les di, ptr [0xa917]
E306  03 F8           add di, ax
E308  89 7E F4        mov word ptr [bp - 0xc], di
E30B  8C 46 F6        mov word ptr [bp - 0xa], es
E30E  BF 4C 45        mov di, 0x454c
E311  1E              push ds
E312  57              push di
E313  BF 6E A9        mov di, 0xa96e
E316  1E              push ds
E317  57              push di
E318  9A 29 03 4B 21  call far 214B:0329
E31D  BF F2 26        mov di, 0x26f2
E320  1E              push ds
E321  57              push di
E322  BF 6E A9        mov di, 0xa96e
E325  1E              push ds
E326  57              push di
E327  9A 29 03 4B 21  call far 214B:0329
E32C  BF F0 57        mov di, 0x57f0
E32F  1E              push ds
E330  57              push di
E331  BF 6E A9        mov di, 0xa96e
E334  1E              push ds
E335  57              push di
E336  9A 29 03 4B 21  call far 214B:0329
E33B  C7 46 FC 02 00  mov word ptr [bp - 4], 2
E340  C4 7E F8        les di, ptr [bp - 8]
E343  26 8A 45 01     mov al, byte ptr es:[di + 1]
E347  30 E4           xor ah, ah
E349  D1 E0           shl ax, 1
E34B  C4 7E F8        les di, ptr [bp - 8]
E34E  03 F8           add di, ax
E350  26 8B 45 52     mov ax, word ptr es:[di + 0x52]
E354  05 14 00        add ax, 0x14
E357  89 46 F2        mov word ptr [bp - 0xe], ax
E35A  C4 7E F8        les di, ptr [bp - 8]
E35D  26 8A 45 01     mov al, byte ptr es:[di + 1]
E361  30 E4           xor ah, ah
E363  D1 E0           shl ax, 1
E365  C4 7E F8        les di, ptr [bp - 8]
E368  03 F8           add di, ax
E36A  26 8B 45 52     mov ax, word ptr es:[di + 0x52]
E36E  3B 46 F2        cmp ax, word ptr [bp - 0xe]
E371  77 6C           ja 0xe3df
E373  89 46 FE        mov word ptr [bp - 2], ax
E376  EB 03           jmp 0xe37b
loc_E378:
E378  FF 46 FE        inc word ptr [bp - 2]
loc_E37B:
E37B  FF 46 FC        inc word ptr [bp - 4]
E37E  C4 7E F8        les di, ptr [bp - 8]
E381  26 8A 45 01     mov al, byte ptr es:[di + 1]
E385  30 E4           xor ah, ah
E387  8B F8           mov di, ax
E389  D1 E7           shl di, 1
E38B  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
E38F  03 46 FE        add ax, word ptr [bp - 2]
E392  48              dec ax
E393  D1 E0           shl ax, 1
E395  C4 3E 27 A9     les di, ptr [0xa927]
E399  03 F8           add di, ax
E39B  26 FF 35        push word ptr es:[di]
E39E  FF 76 FC        push word ptr [bp - 4]
E3A1  B8 41 00        mov ax, 0x41
E3A4  50              push ax
E3A5  9A 37 2F 71 17  call far 1771:2F37
E3AA  8B 46 FE        mov ax, word ptr [bp - 2]
E3AD  8B 7E 04        mov di, word ptr [bp + 4]
E3B0  36 3B 45 F5     cmp ax, word ptr ss:[di - 0xb]
E3B4  75 21           jne 0xe3d7
E3B6  8B 46 FC        mov ax, word ptr [bp - 4]
E3B9  BA A0 00        mov dx, 0xa0
E3BC  F7 E2           mul dx
E3BE  C4 3E 6E A9     les di, ptr [0xa96e]
E3C2  03 F8           add di, ax
E3C4  81 C7 E0 FF     add di, 0xffe0
E3C8  06              push es
E3C9  57              push di
E3CA  B8 8F 00        mov ax, 0x8f
E3CD  50              push ax
E3CE  B8 0C 00        mov ax, 0xc
E3D1  50              push ax
E3D2  9A DB 00 4B 21  call far 214B:00DB
loc_E3D7:
E3D7  8B 46 FE        mov ax, word ptr [bp - 2]
E3DA  3B 46 F2        cmp ax, word ptr [bp - 0xe]
E3DD  75 99           jne 0xe378
loc_E3DF:
E3DF  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E3E4  75 1E           jne 0xe404
E3E6  BF 9C 26        mov di, 0x269c
E3E9  1E              push ds
E3EA  57              push di
E3EB  BF 6E A9        mov di, 0xa96e
E3EE  1E              push ds
E3EF  57              push di
E3F0  9A 29 03 4B 21  call far 214B:0329
E3F5  BF 8A 26        mov di, 0x268a
E3F8  1E              push ds
E3F9  57              push di
E3FA  BF 6E A9        mov di, 0xa96e
E3FD  1E              push ds
E3FE  57              push di
E3FF  9A 29 03 4B 21  call far 214B:0329
loc_E404:
E404  8B 7E 04        mov di, word ptr [bp + 4]
E407  36 FF 75 FB     push word ptr ss:[di - 5]
E40B  FF 76 04        push word ptr [bp + 4]
E40E  E8 BA F9        call 0xddcb
E411  50              push ax
E412  FF 76 04        push word ptr [bp + 4]
E415  E8 39 FA        call 0xde51
E418  89 C7           mov di, ax
E41A  8E C2           mov es, dx
E41C  26 FF 35        push word ptr es:[di]
E41F  9A BC 42 71 17  call far 1771:42BC
E424  C4 7E F8        les di, ptr [bp - 8]
E427  26 8A 45 01     mov al, byte ptr es:[di + 1]
E42B  30 E4           xor ah, ah
E42D  D1 E0           shl ax, 1
E42F  C4 7E F8        les di, ptr [bp - 8]
E432  03 F8           add di, ax
E434  26 8B 45 5E     mov ax, word ptr es:[di + 0x5e]
E438  05 02 00        add ax, 2
E43B  50              push ax
E43C  B8 41 00        mov ax, 0x41
E43F  50              push ax
E440  B8 0C 00        mov ax, 0xc
E443  50              push ax
E444  9A C5 13 4B 21  call far 214B:13C5
E449  89 EC           mov sp, bp
E44B  5D              pop bp
E44C  C2 02 00        ret 2

; ---- routine 0791:E44F  (found by: call, far)
sub_E44F:
E44F  55              push bp
E450  89 E5           mov bp, sp
E452  83 EC 12        sub sp, 0x12
E455  C4 3E 23 A9     les di, ptr [0xa923]
E459  89 7E EF        mov word ptr [bp - 0x11], di
E45C  8C 46 F1        mov word ptr [bp - 0xf], es
E45F  8B 46 06        mov ax, word ptr [bp + 6]
E462  BA BF 00        mov dx, 0xbf
E465  F7 E2           mul dx
E467  C4 3E 17 A9     les di, ptr [0xa917]
E46B  03 F8           add di, ax
E46D  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
E471  30 E4           xor ah, ah
E473  2D 80 00        sub ax, 0x80
E476  C4 7E EF        les di, ptr [bp - 0x11]
E479  26 88 45 01     mov byte ptr es:[di + 1], al
E47D  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
E482  75 0D           jne 0xe491
E484  C6 06 20 0C 00  mov byte ptr [0xc20], 0
E489  FF 76 06        push word ptr [bp + 6]
E48C  9A CC 52 71 17  call far 1771:52CC
loc_E491:
E491  C6 46 FF 00     mov byte ptr [bp - 1], 0
E495  C7 46 FB 01 00  mov word ptr [bp - 5], 1
E49A  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
E49F  74 11           je 0xe4b2
E4A1  A1 36 9B        mov ax, word ptr [0x9b36]
E4A4  3B 46 06        cmp ax, word ptr [bp + 6]
E4A7  74 04           je 0xe4ad
E4A9  B0 00           mov al, 0
E4AB  EB 02           jmp 0xe4af
loc_E4AD:
E4AD  B0 01           mov al, 1
loc_E4AF:
E4AF  88 46 FD        mov byte ptr [bp - 3], al
loc_E4B2:
E4B2  31 C0           xor ax, ax
E4B4  89 46 F5        mov word ptr [bp - 0xb], ax
loc_E4B7:
E4B7  83 7E FB 01     cmp word ptr [bp - 5], 1
E4BB  75 17           jne 0xe4d4
E4BD  FF 76 06        push word ptr [bp + 6]
E4C0  A0 20 0C        mov al, byte ptr [0xc20]
E4C3  98              cwde
E4C4  8B F8           mov di, ax
E4C6  8A 85 BC 0A     mov al, byte ptr [di + 0xabc]
E4CA  30 E4           xor ah, ah
E4CC  50              push ax
E4CD  9A 22 4E 71 17  call far 1771:4E22
E4D2  EB 04           jmp 0xe4d8
loc_E4D4:
E4D4  55              push bp
E4D5  E8 0E FE        call 0xe2e6
loc_E4D8:
E4D8  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E4DD  74 0F           je 0xe4ee
E4DF  BF F6 1A        mov di, 0x1af6
E4E2  1E              push ds
E4E3  57              push di
E4E4  BF 6E A9        mov di, 0xa96e
E4E7  1E              push ds
E4E8  57              push di
E4E9  9A 29 03 4B 21  call far 214B:0329
loc_E4EE:
E4EE  80 3E 6D 06 00  cmp byte ptr [0x66d], 0
E4F3  74 03           je 0xe4f8
E4F5  E9 A7 00        jmp 0xe59f
loc_E4F8:
E4F8  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E4FD  74 12           je 0xe511
E4FF  BF 68 25        mov di, 0x2568
E502  1E              push ds
E503  57              push di
E504  BF 6E A9        mov di, 0xa96e
E507  1E              push ds
E508  57              push di
E509  9A 29 03 4B 21  call far 214B:0329
E50E  E9 8E 00        jmp 0xe59f
loc_E511:
E511  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
E516  75 26           jne 0xe53e
E518  BF 42 1B        mov di, 0x1b42
E51B  1E              push ds
E51C  57              push di
E51D  BF 6E A9        mov di, 0xa96e
E520  1E              push ds
E521  57              push di
E522  9A 29 03 4B 21  call far 214B:0329
E527  83 7E FB 01     cmp word ptr [bp - 5], 1
E52B  75 0F           jne 0xe53c
E52D  BF E6 58        mov di, 0x58e6
E530  1E              push ds
E531  57              push di
E532  BF 6E A9        mov di, 0xa96e
E535  1E              push ds
E536  57              push di
E537  9A 29 03 4B 21  call far 214B:0329
loc_E53C:
E53C  EB 61           jmp 0xe59f
loc_E53E:
E53E  8A 46 FD        mov al, byte ptr [bp - 3]
E541  98              cwde
E542  8B F8           mov di, ax
E544  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
E549  75 11           jne 0xe55c
E54B  BF 38 25        mov di, 0x2538
E54E  1E              push ds
E54F  57              push di
E550  BF 6E A9        mov di, 0xa96e
E553  1E              push ds
E554  57              push di
E555  9A 29 03 4B 21  call far 214B:0329
E55A  EB 43           jmp 0xe59f
loc_E55C:
E55C  80 3E 41 9B 00  cmp byte ptr [0x9b41], 0
E561  74 06           je 0xe569
E563  55              push bp
E564  E8 39 FD        call 0xe2a0
E567  EB 36           jmp 0xe59f
loc_E569:
E569  80 3E 40 9B 00  cmp byte ptr [0x9b40], 0
E56E  75 11           jne 0xe581
E570  BF 60 47        mov di, 0x4760
E573  1E              push ds
E574  57              push di
E575  BF 6E A9        mov di, 0xa96e
E578  1E              push ds
E579  57              push di
E57A  9A 29 03 4B 21  call far 214B:0329
E57F  EB 1E           jmp 0xe59f
loc_E581:
E581  BF 12 48        mov di, 0x4812
E584  1E              push ds
E585  57              push di
E586  BF 6E A9        mov di, 0xa96e
E589  1E              push ds
E58A  57              push di
E58B  9A 29 03 4B 21  call far 214B:0329
E590  BF B2 4E        mov di, 0x4eb2
E593  1E              push ds
E594  57              push di
E595  BF 6E A9        mov di, 0xa96e
E598  1E              push ds
E599  57              push di
E59A  9A 29 03 4B 21  call far 214B:0329
loc_E59F:
E59F  80 7E FF 00     cmp byte ptr [bp - 1], 0
E5A3  74 60           je 0xe605
E5A5  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
E5AA  75 0F           jne 0xe5bb
E5AC  BF 72 26        mov di, 0x2672
E5AF  1E              push ds
E5B0  57              push di
E5B1  BF 6E A9        mov di, 0xa96e
E5B4  1E              push ds
E5B5  57              push di
E5B6  9A 29 03 4B 21  call far 214B:0329
loc_E5BB:
E5BB  83 7E F9 01     cmp word ptr [bp - 7], 1
E5BF  75 44           jne 0xe605
E5C1  83 7E FB 01     cmp word ptr [bp - 5], 1
E5C5  75 3E           jne 0xe605
E5C7  A1 1B 0C        mov ax, word ptr [0xc1b]
E5CA  3B 46 F7        cmp ax, word ptr [bp - 9]
E5CD  74 36           je 0xe605
E5CF  83 7E F7 0B     cmp word ptr [bp - 9], 0xb
E5D3  77 04           ja 0xe5d9
E5D5  B0 00           mov al, 0
E5D7  EB 02           jmp 0xe5db
loc_E5D9:
E5D9  B0 01           mov al, 1
loc_E5DB:
E5DB  30 E4           xor ah, ah
E5DD  8B D0           mov dx, ax
E5DF  8B 46 F7        mov ax, word ptr [bp - 9]
E5E2  05 02 00        add ax, 2
E5E5  03 C2           add ax, dx
E5E7  BA A0 00        mov dx, 0xa0
E5EA  F7 E2           mul dx
E5EC  C4 3E 6E A9     les di, ptr [0xa96e]
E5F0  03 F8           add di, ax
E5F2  81 C7 E0 FF     add di, 0xffe0
E5F6  06              push es
E5F7  57              push di
E5F8  B8 8F 00        mov ax, 0x8f
E5FB  50              push ax
E5FC  B8 0C 00        mov ax, 0xc
E5FF  50              push ax
E600  9A DB 00 4B 21  call far 214B:00DB
loc_E605:
E605  C4 3E 6E A9     les di, ptr [0xa96e]
E609  06              push es
E60A  57              push di
E60B  C4 3E 6A A9     les di, ptr [0xa96a]
E60F  06              push es
E610  57              push di
E611  B8 A0 0F        mov ax, 0xfa0
E614  50              push ax
E615  9A 5D 02 E4 23  call far 23E4:025D
E61A  9A DD 08 4B 21  call far 214B:08DD
E61F  C6 46 FE 00     mov byte ptr [bp - 2], 0
E623  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
E628  75 17           jne 0xe641
E62A  80 7E FF 00     cmp byte ptr [bp - 1], 0
E62E  75 11           jne 0xe641
E630  83 7E FB 01     cmp word ptr [bp - 5], 1
E634  75 06           jne 0xe63c
E636  C6 46 FE 01     mov byte ptr [bp - 2], 1
E63A  EB 05           jmp 0xe641
loc_E63C:
E63C  C6 06 76 A9 AE  mov byte ptr [0xa976], 0xae
loc_E641:
E641  80 7E FF 00     cmp byte ptr [bp - 1], 0
E645  74 13           je 0xe65a
E647  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
E64C  75 0C           jne 0xe65a
E64E  C6 46 FF 00     mov byte ptr [bp - 1], 0
E652  31 C0           xor ax, ax
E654  89 46 F5        mov word ptr [bp - 0xb], ax
E657  E9 7F 01        jmp 0xe7d9
loc_E65A:
E65A  A0 76 A9        mov al, byte ptr [0xa976]
E65D  50              push ax
E65E  9A B2 19 E4 23  call far 23E4:19B2
E663  3C 0D           cmp al, 0xd
E665  75 51           jne 0xe6b8
E667  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
E66C  75 06           jne 0xe674
E66E  55              push bp
E66F  E8 34 F8        call 0xdea6
E672  EB 41           jmp 0xe6b5
loc_E674:
E674  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E679  75 3A           jne 0xe6b5
E67B  80 3E 41 9B 00  cmp byte ptr [0x9b41], 0
E680  74 13           je 0xe695
E682  8A 46 FD        mov al, byte ptr [bp - 3]
E685  98              cwde
E686  8B F8           mov di, ax
E688  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
E68D  76 06           jbe 0xe695
E68F  55              push bp
E690  E8 8F F9        call 0xe022
E693  EB 20           jmp 0xe6b5
loc_E695:
E695  80 3E 40 9B 00  cmp byte ptr [0x9b40], 0
E69A  75 14           jne 0xe6b0
E69C  8A 46 FD        mov al, byte ptr [bp - 3]
E69F  98              cwde
E6A0  8B F8           mov di, ax
E6A2  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
E6A7  76 07           jbe 0xe6b0
E6A9  C6 06 40 9B 01  mov byte ptr [0x9b40], 1
E6AE  EB 05           jmp 0xe6b5
loc_E6B0:
E6B0  C6 06 40 9B 00  mov byte ptr [0x9b40], 0
loc_E6B5:
E6B5  E9 21 01        jmp 0xe7d9
loc_E6B8:
E6B8  3C AE           cmp al, 0xae
E6BA  74 04           je 0xe6c0
E6BC  3C AF           cmp al, 0xaf
E6BE  75 1C           jne 0xe6dc
loc_E6C0:
E6C0  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
E6C5  75 12           jne 0xe6d9
E6C7  83 7E FB 01     cmp word ptr [bp - 5], 1
E6CB  75 07           jne 0xe6d4
E6CD  C7 46 FB 02 00  mov word ptr [bp - 5], 2
E6D2  EB 05           jmp 0xe6d9
loc_E6D4:
E6D4  C7 46 FB 01 00  mov word ptr [bp - 5], 1
loc_E6D9:
E6D9  E9 FD 00        jmp 0xe7d9
loc_E6DC:
E6DC  3C A0           cmp al, 0xa0
E6DE  75 23           jne 0xe703
E6E0  FF 76 FB        push word ptr [bp - 5]
E6E3  55              push bp
E6E4  E8 40 F7        call 0xde27
E6E7  50              push ax
E6E8  55              push bp
E6E9  E8 65 F7        call 0xde51
E6EC  89 C7           mov di, ax
E6EE  8E C2           mov es, dx
E6F0  26 FF 35        push word ptr es:[di]
E6F3  B8 08 00        mov ax, 8
E6F6  50              push ax
E6F7  B8 02 00        mov ax, 2
E6FA  50              push ax
E6FB  9A 59 48 71 17  call far 1771:4859
E700  E9 D6 00        jmp 0xe7d9
loc_E703:
E703  3C 52           cmp al, 0x52
E705  74 04           je 0xe70b
E707  3C 43           cmp al, 0x43
E709  75 22           jne 0xe72d
loc_E70B:
E70B  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E710  75 18           jne 0xe72a
E712  FF 76 FB        push word ptr [bp - 5]
E715  55              push bp
E716  E8 0E F7        call 0xde27
E719  50              push ax
E71A  55              push bp
E71B  E8 33 F7        call 0xde51
E71E  89 C7           mov di, ax
E720  8E C2           mov es, dx
E722  26 FF 35        push word ptr es:[di]
E725  9A 52 49 71 17  call far 1771:4952
loc_E72A:
E72A  E9 AC 00        jmp 0xe7d9
loc_E72D:
E72D  3C 54           cmp al, 0x54
E72F  75 2E           jne 0xe75f
E731  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
E736  75 25           jne 0xe75d
E738  FF 76 FB        push word ptr [bp - 5]
E73B  55              push bp
E73C  E8 E8 F6        call 0xde27
E73F  50              push ax
E740  55              push bp
E741  E8 0D F7        call 0xde51
E744  89 C7           mov di, ax
E746  8E C2           mov es, dx
E748  26 FF 35        push word ptr es:[di]
E74B  83 7E FB 01     cmp word ptr [bp - 5], 1
E74F  74 04           je 0xe755
E751  B0 00           mov al, 0
E753  EB 02           jmp 0xe757
loc_E755:
E755  B0 01           mov al, 1
loc_E757:
E757  50              push ax
E758  9A 61 4B 71 17  call far 1771:4B61
loc_E75D:
E75D  EB 7A           jmp 0xe7d9
loc_E75F:
E75F  3C B6           cmp al, 0xb6
E761  75 27           jne 0xe78a
E763  83 7E FB 01     cmp word ptr [bp - 5], 1
E767  75 1F           jne 0xe788
E769  C4 7E EF        les di, ptr [bp - 0x11]
E76C  26 8A 45 01     mov al, byte ptr es:[di + 1]
E770  30 E4           xor ah, ah
E772  C4 7E EF        les di, ptr [bp - 0x11]
E775  03 F8           add di, ax
E777  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
E77C  75 0A           jne 0xe788
E77E  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
E783  75 03           jne 0xe788
E785  E8 F6 F4        call 0xdc7e
loc_E788:
E788  EB 4F           jmp 0xe7d9
loc_E78A:
E78A  83 7E FB 01     cmp word ptr [bp - 5], 1
E78E  75 10           jne 0xe7a0
E790  BF 1B 0C        mov di, 0xc1b
E793  1E              push ds
E794  57              push di
E795  B8 14 00        mov ax, 0x14
E798  50              push ax
E799  9A 07 15 4B 21  call far 214B:1507
E79E  EB 39           jmp 0xe7d9
loc_E7A0:
E7A0  C4 7E EF        les di, ptr [bp - 0x11]
E7A3  26 8A 45 01     mov al, byte ptr es:[di + 1]
E7A7  30 E4           xor ah, ah
E7A9  D1 E0           shl ax, 1
E7AB  C4 7E EF        les di, ptr [bp - 0x11]
E7AE  03 F8           add di, ax
E7B0  81 C7 5E 00     add di, 0x5e
E7B4  06              push es
E7B5  57              push di
E7B6  C4 7E EF        les di, ptr [bp - 0x11]
E7B9  26 8A 45 01     mov al, byte ptr es:[di + 1]
E7BD  30 E4           xor ah, ah
E7BF  D1 E0           shl ax, 1
E7C1  C4 7E EF        les di, ptr [bp - 0x11]
E7C4  03 F8           add di, ax
E7C6  81 C7 52 00     add di, 0x52
E7CA  06              push es
E7CB  57              push di
E7CC  B8 15 00        mov ax, 0x15
E7CF  50              push ax
E7D0  B8 50 00        mov ax, 0x50
E7D3  50              push ax
E7D4  9A B1 15 4B 21  call far 214B:15B1
loc_E7D9:
E7D9  80 7E FE 00     cmp byte ptr [bp - 2], 0
E7DD  75 03           jne 0xe7e2
E7DF  E9 D5 FC        jmp 0xe4b7
loc_E7E2:
E7E2  9A 32 55 71 17  call far 1771:5532
E7E7  89 EC           mov sp, bp
E7E9  5D              pop bp
E7EA  CA 02 00        retf 2
; data (not reached as code), 32 bytes
E7ED                  db 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; . ..............
E7FD                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

