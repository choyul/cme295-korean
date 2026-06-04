#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys, os, glob

WORK = "/Users/choyul/Documents/claude-연습"
# 디자인 템플릿: 승인본 Lecture 3 섹션3 (스타일·스크립트는 강의 무관, 재사용)
TEMPLATE = os.path.join(WORK, "Stanford CME295_Lecture 3", "섹션3_한국어교재.html")

# 변환할 강의 번호 (인자로 받음, 기본 3)
LEC = sys.argv[1] if len(sys.argv) > 1 else "3"
BASE = os.path.join(WORK, f"Stanford CME295_Lecture {LEC}")

tpl = open(TEMPLATE, encoding="utf-8").read()
TOP = tpl[:tpl.index('<div class="layout">')]
BOTTOM = '</div>\n\n' + tpl[tpl.index('<!-- KaTeX 자동 렌더 -->'):]

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(t):
    t = esc(t.strip())
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\((\d{1,2}:\d{2}(?::\d{2})?)\)', r'<span class="ts">\1</span>', t)
    return t

def render_flow(lines):
    out = []; i = 0; n = len(lines)
    while i < n:
        l = lines[i].rstrip()
        s = l.strip()
        if not s or s == '---':
            i += 1; continue
        if s.startswith('- '):
            items = []
            while i < n and lines[i].strip().startswith('- '):
                items.append(inline(lines[i].strip()[2:])); i += 1
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
        elif re.match(r'^\d+\.\s', s):
            items = []
            while i < n and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(inline(re.sub(r'^\d+\.\s', '', lines[i].strip()))); i += 1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
        else:
            out.append(f'<p>{inline(s)}</p>'); i += 1
    return '\n'.join(out)

def render_en(qlines):
    text = ' '.join(l.lstrip('> ').rstrip() for l in qlines if l.strip())
    return ('<details class="en"><summary><span class="chev">▸</span> 영문 원문 보기</summary>'
            f'<div class="en-body"><p>{inline(text)}</p></div></details>')

def render_note(qlines):
    text = ' '.join(l.lstrip('> ').rstrip() for l in qlines if l.strip())
    return f'<div class="callout note"><div class="c-title">⚠️ 참고</div><p>{inline(text)}</p></div>'

def render_terms(item_lines):
    dl = []; extras = []
    for l in item_lines:
        body = l.strip()[2:]
        m = re.match(r'\*\*(.+?)\*\*\s*[:：]\s*(.*)', body)
        if m:
            term, dfn = m.group(1), m.group(2)
            term_html = re.sub(r'\((.+?)\)', r'<span class="en-term">(\1)</span>', esc(term))
            dl.append(f'<dt>{term_html}</dt><dd>{inline(dfn)}</dd>')
        else:
            extras.append(f'<p style="margin:8px 0 2px;color:var(--ink-soft);font-size:15px;">{inline(body)}</p>')
    return ('<div class="terms"><span class="label">용어 설명</span><dl>'
            + ''.join(dl) + '</dl>' + ''.join(extras) + '</div>')

def render_table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    head = cells[0]; body = cells[2:]
    th = ''.join(f'<th>{inline(c)}</th>' for c in head)
    trs = []
    for r in body:
        tds = ''.join(f'<td>{inline(c)}</td>' for c in r)
        trs.append(f'<tr>{tds}</tr>')
    return ('<div class="table-wrap"><table><thead><tr>' + th + '</tr></thead><tbody>'
            + ''.join(trs) + '</tbody></table></div>')

toc_blocks = []

def render_body(body_lines):
    out = []; i = 0; n = len(body_lines); block_open = False
    while i < n:
        s = body_lines[i].strip()
        if s.startswith('### 블록'):
            if block_open: out.append('</div>')
            m = re.match(r'###\s*블록\s*(\d+)\s*[—\-]\s*(.*)', s)
            num, title = m.group(1), m.group(2)
            out.append(f'<div id="block{num}"><h3><span class="badge">블록 {num}</span>{inline(title)}</h3>')
            toc_blocks.append((f'block{num}', f'블록 {num} · {title}'))
            block_open = True; i += 1
        elif s == '**영문 원문**':
            i += 1; q = []
            while i < n and body_lines[i].strip().startswith('>'):
                q.append(body_lines[i]); i += 1
            out.append(render_en(q))
        elif s == '**한국어 번역**':
            i += 1; ko = []; notes = []
            while i < n:
                t = body_lines[i].strip()
                if t in ('**용어 설명**', '**영문 원문**') or t.startswith('### ') or t.startswith('## '):
                    break
                if t.startswith('>'):
                    q = []
                    while i < n and body_lines[i].strip().startswith('>'):
                        q.append(body_lines[i]); i += 1
                    notes.append(render_note(q)); continue
                ko.append(body_lines[i]); i += 1
            out.append('<div class="ko"><span class="label">한국어 번역</span>' + render_flow(ko) + '</div>')
            out.extend(notes)
        elif s == '**용어 설명**':
            i += 1; items = []
            while i < n:
                t = body_lines[i].strip()
                if t.startswith('- '):
                    items.append(body_lines[i]); i += 1
                elif not t:
                    i += 1
                else:
                    break
            out.append(render_terms(items))
        else:
            i += 1
    if block_open: out.append('</div>')
    return '\n'.join(out)

def sec_meta(title):
    for key, sid in [('강의 개요','overview'),('학습 목표','goals'),('본문','body'),
                     ('용어집','glossary'),('복습','review'),('부록','appendix')]:
        if key in title:
            return sid
    return re.sub(r'[^a-z0-9]+', '-', title.lower())[:20] or 'sec'

def convert(num):
    src = os.path.join(BASE, f"섹션{num}_한국어교재.md")
    md = open(src, encoding="utf-8").read()
    lines = md.split('\n')

    h1 = ''; chunks = []; cur = None
    for line in lines:
        if line.startswith('## '):
            if cur: chunks.append(cur)
            cur = [line[3:].strip(), []]
        elif cur is None:
            if line.startswith('# '): h1 = line[2:].strip()
        else:
            cur[1].append(line)
    if cur: chunks.append(cur)

    global toc_blocks; toc_blocks = []
    subtitle = ''; banner = ''; body_html = []; toc = []

    for title, blines in chunks:
        if title.startswith('섹션'):
            subtitle = title
            for l in blines:
                if l.strip().startswith('> 원문 출처'):
                    txt = l.strip().lstrip('> ').rstrip()
                    e = inline(txt).replace('원문 출처', '<b>원문 출처</b>', 1)
                    banner = f'<div class="source-banner"><span>📄</span><span>{e}</span></div>'
            continue
        sid = sec_meta(title)
        if sid == 'overview':
            body_html.append(f'<section id="overview"><h2>{esc(title)}</h2>{render_flow(blines)}</section>')
            toc.append((sid, title, False))
        elif sid == 'goals':
            body_html.append(f'<section id="goals"><h2>{esc(title)}</h2>{render_flow(blines)}</section>')
            toc.append((sid, title, False))
        elif sid == 'body':
            inner = render_body(blines)
            body_html.append(f'<section id="body"><h2>{esc(title)}</h2>{inner}</section>')
            toc.append((sid, title, False))
            for bid, blabel in toc_blocks:
                toc.append((bid, blabel, True))
        elif sid == 'glossary':
            tbl = [l for l in blines if l.strip().startswith('|')]
            body_html.append(f'<section id="glossary"><h2>{esc(title)}</h2>{render_table(tbl)}</section>')
            toc.append((sid, title, False))
        elif sid == 'review':
            body_html.append(f'<section id="review"><h2>{esc(title)}</h2>'
                             f'<div class="callout review"><div class="c-title">✏️ 스스로 점검</div>'
                             f'{render_flow(blines)}</div></section>')
            toc.append((sid, title, False))
        elif sid == 'appendix':
            m = re.match(r'(.*?)\s*(\(.*\))\s*$', title)
            if m:
                htitle = f'{esc(m.group(1))} <span style="font-size:14px;font-weight:500;color:var(--muted);">{esc(m.group(2))}</span>'
            else:
                htitle = esc(title)
            prac = []; nxt = ''
            i = 0
            while i < len(blines):
                t = blines[i].strip()
                if t.startswith('> 다음 섹션') or (t.startswith('>') and '다음 섹션' in t):
                    q = []
                    while i < len(blines) and blines[i].strip().startswith('>'):
                        q.append(blines[i]); i += 1
                    txt = ' '.join(x.lstrip('> ').rstrip() for x in q if x.strip())
                    txt = txt.replace('다음 섹션 예고:', '<strong>다음 섹션 예고</strong> ·').replace('다음 섹션 예고', '<strong>다음 섹션 예고</strong> ·', 1)
                    nxt = f'<div class="next">{inline_keepstrong(txt)}</div>'
                    continue
                prac.append(blines[i]); i += 1
            block = (f'<section id="appendix"><h2>{htitle}</h2>'
                     f'<div class="callout practice"><div class="c-title">💡 현장에서 써먹기</div>'
                     f'{render_flow(prac)}</div>{nxt}</section>')
            body_html.append(block)
            toc.append((sid, title, False))

    # nav
    toc_html = []
    for sid, label, sub in toc:
        cls = ' class="sub"' if sub else ''
        toc_html.append(f'<li><a{cls} href="#{sid}">{esc(label)}</a></li>')
    nav = ('<nav class="sidebar" id="sidebar">'
           f'<div class="toc-brand">Stanford CME295 · Lecture {LEC}</div>'
           f'<p class="toc-title">{esc(subtitle)}</p>'
           '<ul class="toc">' + ''.join(toc_html) + '</ul></nav>')

    article = (f'<h1>{esc(h1)}</h1><p class="subtitle">{esc(subtitle)}</p>'
               + banner + ''.join(body_html))

    page_title = f"CME295 Lecture {LEC} · {subtitle}"
    top = re.sub(r'<title>.*?</title>', f'<title>{esc(page_title)}</title>', TOP, count=1, flags=re.S)

    html = (top + '<div class="layout">\n  ' + nav
            + '\n  <main class="content"><article class="doc">'
            + article + '</article></main>\n' + BOTTOM)

    out = os.path.join(BASE, f"섹션{num}_한국어교재.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"OK 섹션{num}: blocks={len(toc_blocks)}, sections={sum(1 for _,_,s in toc if not s)} -> {os.path.basename(out)}")

def inline_keepstrong(t):
    # like inline but text already has <strong> tags we injected
    parts = re.split(r'(<strong>.*?</strong>)', t)
    res = []
    for p in parts:
        if p.startswith('<strong>'):
            res.append(p)
        else:
            res.append(inline(p))
    return ''.join(res)

nums = sorted(int(re.search(r'섹션(\d+)_', os.path.basename(p)).group(1))
              for p in glob.glob(os.path.join(BASE, "섹션*_한국어교재.md")))
print(f"Lecture {LEC} 변환 시작: 섹션 {nums}")
for num in nums:
    convert(num)
print("DONE")
