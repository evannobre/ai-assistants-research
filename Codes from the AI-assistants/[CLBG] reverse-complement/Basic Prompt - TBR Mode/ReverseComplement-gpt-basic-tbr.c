#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_BUF 8192
#define INIT_SEQ 1024
#define OUT_WIDTH 60

int main(void){
    static unsigned char comp[256];
    // 1. build complement table
    for(int i=0;i<256;i++) comp[i]=i;
    #define SET(a,b) comp[(unsigned char)a]=b; comp[(unsigned char)tolower(a)]=tolower(b)
    SET('A','T'); SET('C','G'); SET('G','C'); SET('T','A'); SET('U','A');
    SET('M','K'); SET('R','Y'); SET('W','W'); SET('S','S'); SET('Y','R');
    SET('K','M'); SET('V','B'); SET('H','D'); SET('D','H'); SET('B','V'); SET('N','N');
    // 2. buffers
    char *seq = malloc(INIT_SEQ), line[LINE_BUF];
    size_t cap=INIT_SEQ, len=0;
    // 3. read lines
    while(fgets(line, LINE_BUF, stdin)){
        if(line[0] == '>'){
            // flush any pending seq
            if(len){
                // reverse-complement
                for(size_t i=len, col=0; i>0; ){
                    unsigned char base = seq[--i];
                    putchar(comp[base]);
                    if(++col == OUT_WIDTH){ putchar('\n'); col=0;}
                }
                putchar('\n');
                len = 0;
            }
            // output header
            fputs(line, stdout);
        } else {
            // strip newline
            char *p = line + strlen(line);
            if(p>line && (p[-1]=='\n' || p[-1]=='\r')) *--p = 0;
            // append, growing if needed
            size_t need = strlen(line);
            if(len + need >= cap){
                while(len + need >= cap) cap *= 2;
                seq = realloc(seq, cap);
            }
            memcpy(seq + len, line, need);
            len += need;
        }
    }
    // flush last seq
    if(len){
        for(size_t i=len, col=0; i>0; ){
            unsigned char base = seq[--i];
            putchar(comp[base]);
            if(++col == OUT_WIDTH){ putchar('\n'); col=0;}
        }
        putchar('\n');
    }
    free(seq);
    return 0;
}
