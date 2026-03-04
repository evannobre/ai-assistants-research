static const unsigned char compl[256] = {
  ['A'] = 'T', ['a'] = 'T',
  ['C'] = 'G', ['c'] = 'G',
  ['G'] = 'C', ['g'] = 'C',
  ['T'] = 'A', ['t'] = 'A',
  ['U'] = 'A', ['u'] = 'A',
  ['M'] = 'K', ['m'] = 'K',
  ['R'] = 'Y', ['r'] = 'Y',
  ['W'] = 'W', ['w'] = 'W',
  ['S'] = 'S', ['s'] = 'S',
  ['Y'] = 'R', ['y'] = 'R',
  ['K'] = 'M', ['k'] = 'M',
  ['V'] = 'B', ['v'] = 'B',
  ['H'] = 'D', ['h'] = 'D',
  ['D'] = 'H', ['d'] = 'H',
  ['B'] = 'V', ['b'] = 'V',
  ['N'] = 'N', ['n'] = 'N'
  /* all other entries default to self or ‘N’ as you prefer */
};

open stdin for buffered reading
open stdout for buffered writing

allocate empty sequence_buffer
while (getline(line) from stdin) {
  if (line[0] == '>') {
    // header line: process any previous sequence first
    if (sequence_buffer not empty) {
      emit_reverse_complement(sequence_buffer)
      clear sequence_buffer
    }
    // write header unchanged
    write line + '\n' to stdout
  }
  else {
    // sequence line: strip trailing newline, append to buffer
    append(line, without newline) to sequence_buffer
  }
}
// after loop, process last sequence
if (sequence_buffer not empty) {
  emit_reverse_complement(sequence_buffer)
}
flush and close stdout

function emit_reverse_complement(buffer):
  let L = length(buffer)
  // output in lines of fixed width (e.g. 60 chars)
  const int LINE_WIDTH = 60
  // process from end → start
  for (i = L-1; i ≥ 0; --i) {
    c = buffer[i]
    rc = compl[(unsigned char)c]    // O(1) lookup
    write rc to stdout
    if ((L-1 - i + 1) % LINE_WIDTH == 0) {
      write '\n' to stdout
    }
  }
  // if last line didn’t end exactly on width
  if (L % LINE_WIDTH != 0) {
    write '\n'
  }
