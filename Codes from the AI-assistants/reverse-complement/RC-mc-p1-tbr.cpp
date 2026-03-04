#include <bits/stdc++.h>
using namespace std;
int main(int argc, char** argv){
  unordered_map<char,char> m{{'A','T'},{'T','A'},{'C','G'},{'G','C'},
                             {'a','t'},{'t','a'},{'c','g'},{'g','c'}};
  ifstream in(argv[1]); string line, seq;
  while(getline(in,line)){
    if(line.size() && line[0]=='>'){
      if(!seq.empty()){ reverse(seq.begin(), seq.end()); cout<<seq<<"\n"; seq.clear(); }
      cout<<line<<"\n";
    } else seq += line;
  }
  if(!seq.empty()){ reverse(seq.begin(), seq.end()); cout<<seq<<"\n"; }
}
