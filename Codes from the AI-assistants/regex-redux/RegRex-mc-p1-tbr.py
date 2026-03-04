from collections import deque, namedtuple

# Fragment for Thompson construction
Fragment = namedtuple('Fragment', ['start', 'accept'])

class ThompsonNFA:
    def __init__(self):
        self.next_state = 0
        self.trans = {}  # state -> list of (symbol, next_state)
    
    def _new_state(self):
        s = self.next_state
        self.next_state += 1
        self.trans[s] = []
        return s
    
    def _add_edge(self, a, symbol, b):
        self.trans[a].append((symbol, b))
    
    # Tokenize and insert explicit concatenation operator '·'
    def _tokenize(self, regex):
        tokens = []
        prev = None
        for ch in regex:
            if prev is not None:
                # if prev was literal, ')' or '*' and current is literal or '(' -> concat
                if (prev not in ['|', '('] and ch not in ['|', ')', '*']):
                    tokens.append('·')
            tokens.append(ch)
            prev = ch
        return tokens
    
    # Shunting-yard to postfix (RPN)
    def _to_postfix(self, tokens):
        prec = {'*': 3, '·': 2, '|': 1}
        output = []
        stack = []
        for t in tokens:
            if t == '(':
                stack.append(t)
            elif t == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # pop '('
            elif t in prec:
                if t == '*':
                    # unary, right-associative; push directly but pop higher prec
                    while stack and stack[-1] != '(' and prec.get(stack[-1],0) > prec[t]:
                        output.append(stack.pop())
                    stack.append(t)
                else:
                    while stack and stack[-1] != '(' and prec.get(stack[-1],0) >= prec[t]:
                        output.append(stack.pop())
                    stack.append(t)
            else:
                # literal or '.'
                output.append(t)
        while stack:
            output.append(stack.pop())
        return output
    
    # Build NFA from postfix
    def build_from_regex(self, regex):
        tokens = self._tokenize(regex)
        postfix = self._to_postfix(tokens)
        stack = []
        for tok in postfix:
            if tok == '*':
                frag = stack.pop()
                s = self._new_state()
                t = self._new_state()
                self._add_edge(s, None, frag.start)
                self._add_edge(s, None, t)
                self._add_edge(frag.accept, None, frag.start)
                self._add_edge(frag.accept, None, t)
                stack.append(Fragment(s, t))
            elif tok == '·':
                b = stack.pop()
                a = stack.pop()
                self._add_edge(a.accept, None, b.start)
                stack.append(Fragment(a.start, b.accept))
            elif tok == '|':
                b = stack.pop()
                a = stack.pop()
                s = self._new_state()
                t = self._new_state()
                self._add_edge(s, None, a.start)
                self._add_edge(s, None, b.start)
                self._add_edge(a.accept, None, t)
                self._add_edge(b.accept, None, t)
                stack.append(Fragment(s, t))
            else:
                # literal or wildcard '.'
                s = self._new_state()
                t = self._new_state()
                self._add_edge(s, tok, t)
                stack.append(Fragment(s, t))
        if len(stack) != 1:
            raise ValueError("Invalid regex")
        frag = stack.pop()
        self.start = frag.start
        self.accept = frag.accept
        return self
    
    # epsilon-closure
    def _closure(self, states):
        stack = deque(states)
        seen = set(states)
        while stack:
            s = stack.popleft()
            for sym, nxt in self.trans.get(s, ()):
                if sym is None and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen
    
    # move on a character c (consider '.' wildcard)
    def _move(self, states, c):
        res = set()
        for s in states:
            for sym, nxt in self.trans.get(s, ()):
                if sym is not None and (sym == c or sym == '.'):
                    res.add(nxt)
        return res
    
    # match entire string (full-match)
    def matches(self, s):
        cur = self._closure({self.start})
        for ch in s:
            cur = self._closure(self._move(cur, ch))
            if not cur:
                return False
        return self.accept in cur

# Example usage
if __name__ == "__main__":
    # regex examples: (a|b)*abb
    regex = "(a|b)*abb"
    nfa = ThompsonNFA().build_from_regex(regex)
    tests = ["abb", "aabb", "ababb", "ab", "aab"]
    for t in tests:
        print(t, nfa.matches(t))
