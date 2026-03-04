variants := []string{
    "agggtaaa|tttaccct",
    "[cgt]gggtaaa|tttaccc[acg]",
    "a[act]ggtaaa|tttacc[agt]t",
    "ag[act]gtaaa|tttac[agt]ct",
    "agg[act]taaa|ttta[agt]cct",
    "aggg[acg]aaa|ttt[cgt]ccct",
    "agggt[cgt]aa|tt[acg]accct",
    "agggta[cgt]a|t[acg]taccct",
    "agggtaa[cgt]|[acg]ttaccct",
}

replacements := []struct{ p, r string }{
    {"tHa[Nt]", "<4>"},
    {"aND|caN|Ha[DS]|WaS", "<3>"},
    {"a[NSt]|BY", "<2>"},
    {"<[^>]*>", "|"},
    {"\\|[^|][^|]*\\|", "-"},
}

// Pseudocode
for _, repl := range replacements {
    re := regexp.MustCompile(repl.p)
    sequenceForReplacement = re.ReplaceAll(sequenceForReplacement, []byte(repl.r))
}