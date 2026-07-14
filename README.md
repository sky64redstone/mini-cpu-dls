# README

## Purpose of this assembler

This assembler is designed for a very specific custom CPU used in the Digital Logic Simulator by Sebastian Lague.
It targets a small ROM-driven 8-bit architecture with a 16-entry register file and a 16-bit instruction ROM.

The assembler is not meant for x86, ARM, RISC-V, or any general-purpose ISA.
It only understands the instruction format and execution model described in this document.

## Architecture overview

This CPU has the following properties:

* **ROM word width:** 16 bits
* **Program counter width:** 8 bits
* **Register width:** 8 bits
* **ALU width:** 8 bits
* **Immediate width:** 8 bits
* **Register count:** 16 registers
* **Instruction flow:** strictly sequential
* **Control flow instructions:** none
* **Memory access instructions:** none
* **Special registers:** none

The ROM stores 16-bit instruction words.
Every ROM entry is one instruction.
The CPU fetches instructions sequentially through an 8-bit program counter.

## Core execution model

The architecture is intentionally minimal.

1. The program counter points to a ROM address.
2. The CPU fetches the 16-bit instruction at that address.
3. The instruction is decoded.
4. The selected operation is executed.
5. The program counter increments by 1.
6. If the program counter overflows past `255`, it wraps around to `0`.

The same wraparound behavior applies to the 8-bit ALU.
If an arithmetic result exceeds `255`, the carry-out is ignored.
Examples:

* `255 + 1 = 0`
* `256 -> 0`
* `260 -> 4`

This is modulo-256 behavior.
There is no carry register exposed to assembly code.
There is no borrow register exposed to assembly code.

## Register file

The CPU has 16 general-purpose registers:

* `R0`
* `R1`
* `R2`
* `R3`
* `R4`
* `R5`
* `R6`
* `R7`
* `R8`
* `R9`
* `R10`
* `R11`
* `R12`
* `R13`
* `R14`
* `R15`

Each register is 8 bits wide.
All registers are normal registers.
No register is reserved.
No register has special zero semantics.
No register is read-only.
No register is hidden from the programmer.

### Register encoding

Registers are encoded with 4 bits:

| Register | Binary |
| -------: | :----: |
|       R0 | `0000` |
|       R1 | `0001` |
|       R2 | `0010` |
|       R3 | `0011` |
|       R4 | `0100` |
|       R5 | `0101` |
|       R6 | `0110` |
|       R7 | `0111` |
|       R8 | `1000` |
|       R9 | `1001` |
|      R10 | `1010` |
|      R11 | `1011` |
|      R12 | `1100` |
|      R13 | `1101` |
|      R14 | `1110` |
|      R15 | `1111` |

## Instruction format

Every instruction is exactly 16 bits wide.
The upper 8 bits and lower 8 bits have different meanings depending on the instruction type.

There are two instruction families:

* register-to-register ALU operations
* immediate load operations

## Register-to-register ALU instructions

### Semantics

Register ALU instructions always behave like this:

`regA = regA op regB`

That means:

* `regA` is the destination register
* `regA` is also the left operand
* `regB` is the right operand
* the result is written back into `regA`

Example:

`ADD R1, R2`

means:

`R1 = R1 + R2`

### Bit layout

A register ALU instruction uses this layout:

`[ regB | regA ] [ 0 | 000 | subtract | 0 | aluopcode ]`

More explicitly:

* upper 4 bits of the first byte: `regB`
* lower 4 bits of the first byte: `regA`
* top bit of the second byte: `0`, meaning register-ALU mode
* next 3 bits: reserved and set to `000`
* next bit: `subtract`
* next bit: reserved and set to `0`
* last 2 bits: `aluopcode`

### ALU opcode table

| Opcode | Operation |
| :----: | --------- |
|  `00`  | ADD / SUB |
|  `01`  | XOR       |
|  `10`  | AND       |
|  `11`  | OR        |

### Subtract bit

The subtract bit is used only with the ADD/SUB operation group.

* `subtract = 0` means addition
* `subtract = 1` means subtraction

In this architecture, subtraction is encoded as the same ALU group as addition, with the subtract bit set.

### Examples

`ADD R1, R2`

* `regB = R2 = 0010`
* `regA = R1 = 0001`
* `subtract = 0`
* `aluopcode = 00`

Binary:

`00100001 00000000`

`SUB R1, R2`

* `regB = R2 = 0010`
* `regA = R1 = 0001`
* `subtract = 1`
* `aluopcode = 00`

Binary:

`00100001 00001000`

`XOR R3, R4`

Binary:

`01000011 00000001`

`AND R5, R6`

Binary:

`01100101 00000010`

`OR R7, R8`

Binary:

`10000111 00000011`

## Immediate instructions

### Semantics

Immediate instructions load an 8-bit constant into a register.

`regA = immediate`

Example:

`MOV R3, 42`

means:

`R3 = 42`

### Bit layout

An immediate instruction uses this layout:

`[ immediate ] [ 1 | 000 | regA ]`

More explicitly:

* upper 8 bits: immediate value
* top bit of the second byte: `1`, meaning immediate mode
* next 3 bits: reserved and set to `000`
* last 4 bits: destination register `regA`

### Immediate range

Because the immediate field is 8 bits wide, the valid range is:

* `0` to `255`

The assembler should reject values outside that range.

### Example

`MOV R3, 42`

* immediate = `42 = 00101010`
* regA = `R3 = 0011`

Binary:

`00101010 10000011`

## Supported instructions

The current assembler is designed for these instructions only:

* `MOV Rn, imm`
* `ADD Rn, Rm`
* `SUB Rn, Rm`
* `XOR Rn, Rm`
* `AND Rn, Rm`
* `OR Rn, Rm`

### MOV

`MOV Rn, imm`

Loads an 8-bit immediate value into register `Rn`.

### ADD

`ADD Rn, Rm`

Computes `Rn = Rn + Rm`.

### SUB

`SUB Rn, Rm`

Computes `Rn = Rn - Rm`.

### XOR

`XOR Rn, Rm`

Computes `Rn = Rn ^ Rm`.

### AND

`AND Rn, Rm`

Computes `Rn = Rn & Rm`.

### OR

`OR Rn, Rm`

Computes `Rn = Rn | Rm`.

## Overflow behavior

All arithmetic is 8-bit.

If an operation produces a result larger than `255`, the high bits are discarded.

Examples:

* `250 + 10 = 4`
* `255 + 1 = 0`
* `200 + 100 = 44`

This behavior also applies to the program counter.
If the PC increments past `255`, it wraps to `0`.

## What this architecture does not include

This CPU does not currently include:

* jumps
* branches
* calls
* returns
* a stack
* RAM load/store instructions
* compare instructions as first-class opcodes
* interrupts
* privilege levels
* memory protection
* a dedicated halt instruction
* a carry flag visible to assembly code
* a borrow flag visible to assembly code

## ROM input format

The Digital Logic Simulator ROM is filled with 16-bit binary strings.
Each line corresponds to one ROM word.
Each line must contain exactly 16 bits.

Example empty ROM:

`0000000000000000`

Example program fragment:

`0000011110000001`
`0000101010000010`
`0010000100000000`

These lines can be pasted directly into the ROM component in binary mode.

## Assembler syntax

The assembler accepts one instruction per line.

Example:

`MOV R1, 5`
`ADD R1, R2`
`SUB R3, R4`

### Comments

Comments start with `;`.
Everything after `;` on a line is ignored.

Example:

`MOV R1, 5   ; load 5 into R1`

### Registers

Registers must be written as `R0` through `R15`.

Examples:

* `R0`
* `R1`
* `R10`
* `R15`

### Immediate values

Immediate values are 8-bit unsigned values.
The assembler may accept standard integer syntax such as decimal or prefixed formats, depending on the implementation.
The architectural limit remains `0` to `255`.

## Full instruction encoding summary

### Register ALU instruction

`[ regB | regA ] [ 0 | 000 | subtract | 0 | aluopcode ]`

### Immediate instruction

`[ immediate ] [ 1 | 000 | regA ]`

## Example program

Source:

`MOV R1, 5`
`MOV R2, 10`
`ADD R1, R2`
`SUB R1, R2`
`XOR R3, R4`
`AND R5, R6`
`OR R7, R8`

Binary output:

`0000010110000001`
`0000101010000010`
`0010000100000000`
`0010000100001000`
`0100001100000001`
`0110010100000010`
`1000011100000011`

## Compatibility note

This README describes the exact architecture that the assembler targets.
If the CPU design changes, especially in any of the following areas, the assembler must be updated:

* register count
* register width
* instruction width
* ROM format
* ALU encoding
* immediate encoding
* program counter width
* overflow behavior
* supported instructions

## Final summary

This assembler is intended for a small 8-bit CPU with:

* 16 general-purpose 8-bit registers
* 16-bit instructions stored in ROM
* an 8-bit program counter
* modulo-256 ALU behavior
* no visible carry handling
* no branches
* no memory access
* direct binary ROM output

It is a minimal assembler for a minimal architecture.

