#!/usr/bin/env ruby

def main
    # Read all input from stdin
    input = $stdin.read
    
    # Record initial length
    initial_length = input.length
    
    # 1. Remove FASTA sequence descriptions and linefeeds
    cleaned = input.gsub(/>.*\n|\n/, '')
    
    # Record cleaned length
    cleaned_length = cleaned.length
    
    # 2. Count patterns
    patterns = [
        /agggtaaa|tttaccct/,
        /[cgt]gggtaaa|tttaccc[acg]/,
        /a[act]ggtaaa|tttacc[agt]t/,
        /ag[act]gtaaa|tttac[agt]ct/,
        /agg[act]taaa|ttta[agt]cct/,
        /aggg[acg]aaa|ttt[cgt]ccct/,
        /agggt[cgt]aa|tt[acg]accct/,
        /agggta[cgt]a|t[acg]taccct/,
        /agggtaa[cgt]|[acg]ttaccct/
    ]
    
    patterns.each do |pattern|
        count = cleaned.scan(pattern).length
        puts "#{pattern.source} #{count}"
    end
    
    # 3. Apply substitution patterns
    substitutions = [
        [/tHa[Nt]/, '<4>'],
        [/aND|caN|Ha[DS]|WaS/, '<3>'],
        [/a[NSt]|BY/, '<2>'],
        [/<[^>]*>/, '|'],
        [/\\|[^|][^|]*\\|/, '-']
    ]
    
    transformed = cleaned.dup
    substitutions.each do |pattern, replacement|
        transformed.gsub!(pattern, replacement)
    end
    
    # Record final length
    final_length = transformed.length
    
    # 4. Print lengths
    puts "\n#{initial_length}\n#{cleaned_length}\n#{final_length}"
end

main if __FILE__ == $PROGRAM_NAME