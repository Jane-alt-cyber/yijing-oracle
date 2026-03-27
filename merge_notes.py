"""
파일 내 중국어 텍스트의 " 가 JS 파싱을 방해하므로
Python으로 텍스트 파싱→JSON 변환→App.jsx 주입합니다.
"""
import json, re

FILES = [
    '/Users/minimax/Desktop/files/tab-ext-01-10.js',
    '/Users/minimax/Desktop/files/tab-ext-11-20.js',
    '/Users/minimax/Desktop/files/tab-ext-21-30.js',
    '/Users/minimax/Desktop/files/tab-ext-31-40.js',
    '/Users/minimax/Desktop/files/tab-ext-41-50.js',
    '/Users/minimax/Desktop/files/tab-ext-51-64.js',
]
FIELDS = ['meaning_ext', 'dao_insight', 'jin_insight', 'nei_insight']
APP_PATH = './src/App.jsx'

# ── Step 1: 텍스트 파싱으로 NOTES 구축 ──────────────────────────────────────

notes = {}
for fpath in FILES:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    current_num = None
    current_entry = {}

    for line in content.split('\n'):
        stripped = line.strip()

        # 卦 번호 라인: "1: {"
        num_match = re.match(r'^(\d+):\s*\{', stripped)
        if num_match:
            current_num = int(num_match.group(1))
            current_entry = {}
            continue

        # 필드 라인: "meaning_ext: "값","
        for field in FIELDS:
            if stripped.startswith(field + ':'):
                # 첫 번째 " 이후부터 마지막 " 이전까지 추출
                first_q = stripped.index('"', len(field) + 1)
                last_q = stripped.rindex('"')
                if first_q < last_q:
                    current_entry[field] = stripped[first_q + 1:last_q]
                break

        # 닫는 괄호
        if (stripped.startswith('},') or stripped == '}') and current_num is not None:
            if len(current_entry) == 4:
                notes[current_num] = current_entry
            current_num = None
            current_entry = {}

print(f'Parsed {len(notes)} hexagrams')
assert len(notes) == 64, f'Expected 64, got {len(notes)}'

# ── Step 2: NOTES JS 상수 직렬화 ────────────────────────────────────────────

notes_str = 'const NOTES=' + json.dumps(notes, ensure_ascii=False, separators=(',', ':')) + ';'

# ── Step 3: App.jsx 수정 ─────────────────────────────────────────────────────

with open(APP_PATH, 'r', encoding='utf-8') as f:
    app = f.read()

# 3a. deepNote 헬퍼 함수 삭제
deep_note_line = (
    "\nconst deepNote=(n,topic)=>{const text=DEEP[n];if(!text)return null;"
    "const ps=text.split('\\n').filter(p=>p.trim().length>0);"
    "if(topic==='base')return ps.filter(p=>!p.includes('老子')&&!p.includes('金刚经')"
    "&&!(p.includes('养生')||p.includes('黄帝内经'))).slice(0,2).join('\\n');"
    "if(topic==='dao')return ps.find(p=>p.includes('老子'))||null;"
    "if(topic==='jin')return ps.find(p=>p.includes('金刚经'))||null;"
    "if(topic==='nei')return ps.find(p=>(p.includes('养生')||p.includes('黄帝内经'))"
    "&&!p.includes('老子')&&!p.includes('金刚经'))||null;return null;};"
)
if deep_note_line in app:
    app = app.replace(deep_note_line, '')
    print('deepNote removed ✓')
else:
    print('WARNING: deepNote line not found verbatim — skipping removal')

# 3b. NOTES 삽입 (const TRI= 앞)
if 'const NOTES=' not in app:
    app = app.replace('const TRI=', notes_str + '\nconst TRI=')
    print('NOTES inserted ✓')
else:
    print('NOTES already present — skipping insert')

# 3c. base tab 교체
old_base = (
    "{deepNote(cur.n,'base')&&deepNote(cur.n,'base').split('\\n')"
    ".map((p,i)=><p key={i} style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",marginBottom:\"16px\",textIndent:\"2em\"}}>{p}</p>)}"
)
new_base = (
    "{NOTES[cur.n]?.meaning_ext&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",marginBottom:\"16px\",textIndent:\"2em\"}}>"
    "{NOTES[cur.n].meaning_ext}</p>}"
)
if old_base in app:
    app = app.replace(old_base, new_base)
    print('base tab ✓')
else:
    print('WARNING: base tab pattern not found')

# 3d. dao tab 교체
old_dao = (
    "{deepNote(cur.n,'dao')&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{deepNote(cur.n,'dao')}</p>}"
)
new_dao = (
    "{NOTES[cur.n]?.dao_insight&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{NOTES[cur.n].dao_insight}</p>}"
)
if old_dao in app:
    app = app.replace(old_dao, new_dao)
    print('dao tab ✓')
else:
    print('WARNING: dao tab pattern not found')

# 3e. jin tab 교체
old_jin = (
    "{deepNote(cur.n,'jin')&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{deepNote(cur.n,'jin')}</p>}"
)
new_jin = (
    "{NOTES[cur.n]?.jin_insight&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{NOTES[cur.n].jin_insight}</p>}"
)
if old_jin in app:
    app = app.replace(old_jin, new_jin)
    print('jin tab ✓')
else:
    print('WARNING: jin tab pattern not found')

# 3f. nei tab 교체
old_nei = (
    "{deepNote(cur.n,'nei')?<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{deepNote(cur.n,'nei')}</p>"
    ":<p style={{fontSize:\"16px\",lineHeight:2.2,color:\"#4a4036\"}}>"
    "{cur.nei.a||cur.nei.advice}</p>}"
)
new_nei = (
    "{NOTES[cur.n]?.nei_insight&&<p style={{fontSize:\"16px\",lineHeight:2.2,"
    "color:\"#4a4036\",textIndent:\"2em\"}}>{NOTES[cur.n].nei_insight}</p>}"
)
if old_nei in app:
    app = app.replace(old_nei, new_nei)
    print('nei tab ✓')
else:
    print('WARNING: nei tab pattern not found')

with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(app)

print('\nApp.jsx written.')
print('deepNote remaining:', app.count('deepNote'))
print('NOTES present:', 'const NOTES=' in app)
