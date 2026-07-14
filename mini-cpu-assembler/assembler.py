import re
import sys


ALU = {
  "ADD": 0b00,
  "SUB": 0b00,
  "XOR": 0b01,
  "AND": 0b10,
  "OR":  0b11,
}


def parse_register(token):
  token = token.upper()

  if not token.startswith("R"):
    raise ValueError(f"Ungültiges Register '{token}'")

  number = int(token[1:])

  if number < 0 or number > 15:
    raise ValueError(f"Register außerhalb des Bereichs: {token}")

  return number


def assemble_instruction(line):
  line = line.split(";")[0].strip()

  if line == "":
    return None

  line = line.replace(",", " ")
  parts = line.split()

  op = parts[0].upper()

  if op == "MOV":
    if len(parts) != 3:
      raise ValueError("MOV erwartet: MOV Rn, imm")

    reg = parse_register(parts[1])
    imm = int(parts[2], 0)

    if imm < 0 or imm > 255:
      raise ValueError("Immediate muss zwischen 0 und 255 liegen")

    upper = imm
    lower = 0b10000000 | reg

    instruction = (upper << 8) | lower
    return instruction

  if op not in ALU:
    raise ValueError(f"Unbekannte Instruktion '{op}'")

  if len(parts) != 3:
    raise ValueError(f"{op} erwartet zwei Register")

  regA = parse_register(parts[1])
  regB = parse_register(parts[2])

  upper = (regB << 4) | regA

  subtract = 1 if op == "SUB" else 0

  lower = (
    (subtract << 3)
    | ALU[op]
  )

  instruction = (upper << 8) | lower
  return instruction


def assemble(source):
  output = []

  for lineno, line in enumerate(source.splitlines(), start=1):
    try:
      inst = assemble_instruction(line)
      if inst is not None:
        output.append(f"{inst:016b}")
    except Exception as e:
      print(f"Fehler in Zeile {lineno}: {e}")
      sys.exit(1)

  return output


def main():
  if len(sys.argv) != 2:
    print("Verwendung:")
    print("python assembler.py programm.asm")
    return

  with open(sys.argv[1], "r") as f:
    source = f.read()

  binary = assemble(source)

  for line in binary:
    print(line)


if __name__ == "__main__":
  main()
