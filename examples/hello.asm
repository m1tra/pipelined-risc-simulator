.data
string:  .pstr 'Hello world'

.text
    addi r1, r0, string
    lbu  r2, [r1+0]
    addi r1, r1, 1
loop:
    lbu  r3, [r1+0]
    sb   r3, [r0+0x84]
    addi r1, r1, 1
    addi r2, r2, -1
    bne  r2, r0, loop
    halt