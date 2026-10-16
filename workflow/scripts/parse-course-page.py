"""Read public course HTML as data; never execute scripts or download media."""
from html.parser import HTMLParser
from urllib.parse import urljoin
import json, sys

class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def nodes(self, tag=None):
        return [n for c in self.children if isinstance(c, Node)
                for n in ([c] if tag is None or c.tag == tag else []) + c.nodes(tag)]
    def text(self):
        return ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in self.children).split())

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.root = Node(); self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs); self.stack[-1].children.append(n)
        if tag not in {'br','img','hr','meta','link','input','wbr','source','area','base','embed','param','track','col'}:
            self.stack.append(n)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]; break
    def handle_data(self, text):
        self.stack[-1].children.append(text)

def summarize(node, base):
    def visible_links(n, hidden=False):
        hidden = hidden or 'w-condition-invisible' in n.attrs.get('class', '') or 'hidden' in n.attrs
        result = []
        if not hidden and n.tag == 'a' and n.attrs.get('href'):
            url = urljoin(base, n.attrs['href']).replace(' ', '%20')
            if url.startswith(('https://', 'http://')):
                result.append({'label': n.text(), 'url': url})
        for c in n.children:
            if isinstance(c, Node): result.extend(visible_links(c, hidden))
        return result
    return {'text': node.text(), 'links': visible_links(node),
            'headings': [n.text() for n in node.nodes() if n.tag in {'h1','h2','h3','h4','strong'}]}

if __name__ == '__main__':
    request = json.load(sys.stdin); p = Parser(); p.feed(request['html']); base = request['url']
    rows = []
    for tr in p.root.nodes('tr'):
        cells = [summarize(n, base) for n in tr.children if isinstance(n, Node) and n.tag in {'td','th'}]
        if cells: rows.append(cells)
    cards = [summarize(n, base) for n in p.root.nodes('div') if 'w-dyn-item' in n.attrs.get('class','').split()]
    result = summarize(p.root, base)
    result.update(rows=rows, cards=cards,
                  scripts=[urljoin(base,n.attrs['src']) for n in p.root.nodes('script') if n.attrs.get('src')])
    json.dump(result, sys.stdout, ensure_ascii=False)
