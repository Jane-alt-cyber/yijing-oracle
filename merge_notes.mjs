import ext0110 from '/Users/minimax/Desktop/files/tab-ext-01-10.js';
import ext1120 from '/Users/minimax/Desktop/files/tab-ext-11-20.js';
import ext2130 from '/Users/minimax/Desktop/files/tab-ext-21-30.js';
import ext3140 from '/Users/minimax/Desktop/files/tab-ext-31-40.js';
import ext4150 from '/Users/minimax/Desktop/files/tab-ext-41-50.js';
import ext5164 from '/Users/minimax/Desktop/files/tab-ext-51-64.js';
import { readFileSync, writeFileSync } from 'fs';

const NOTES = Object.assign({}, ext0110, ext1120, ext2130, ext3140, ext4150, ext5164);
console.log('NOTES covers entries:', Object.keys(NOTES).length);

const notesConst = 'const NOTES=' + JSON.stringify(NOTES) + ';';

let app = readFileSync('./src/App.jsx', 'utf8');

// 1. 删除 deepNote 辅助函数（整行）
const deepNoteLine = `\nconst deepNote=(n,topic)=>{const text=DEEP[n];if(!text)return null;const ps=text.split('\\n').filter(p=>p.trim().length>0);if(topic==='base')return ps.filter(p=>!p.includes('老子')&&!p.includes('金刚经')&&!(p.includes('养生')||p.includes('黄帝内经'))).slice(0,2).join('\\n');if(topic==='dao')return ps.find(p=>p.includes('老子'))||null;if(topic==='jin')return ps.find(p=>p.includes('金刚经'))||null;if(topic==='nei')return ps.find(p=>(p.includes('养生')||p.includes('黄帝内经'))&&!p.includes('老子')&&!p.includes('金刚经'))||null;return null;};`;
app = app.replace(deepNoteLine, '');

// 2. 插入 NOTES 对象（在 const TRI= 前）
app = app.replace('const TRI=', notesConst + '\nconst TRI=');

// 3. 替换 base tab 的 deepNote 调用
app = app.replace(
  `{deepNote(cur.n,'base')&&deepNote(cur.n,'base').split('\\n').map((p,i)=><p key={i} style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",marginBottom:"16px",textIndent:"2em"}}>{p}</p>)}`,
  `{NOTES[cur.n]?.meaning_ext&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",marginBottom:"16px",textIndent:"2em"}}>{NOTES[cur.n].meaning_ext}</p>}`
);

// 4. 替换 dao tab 的 deepNote 调用
app = app.replace(
  `{deepNote(cur.n,'dao')&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{deepNote(cur.n,'dao')}</p>}`,
  `{NOTES[cur.n]?.dao_insight&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{NOTES[cur.n].dao_insight}</p>}`
);

// 5. 替换 jin tab 的 deepNote 调用
app = app.replace(
  `{deepNote(cur.n,'jin')&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{deepNote(cur.n,'jin')}</p>}`,
  `{NOTES[cur.n]?.jin_insight&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{NOTES[cur.n].jin_insight}</p>}`
);

// 6. 替换 nei tab 的 deepNote 调用
app = app.replace(
  `{deepNote(cur.n,'nei')?<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{deepNote(cur.n,'nei')}</p>:<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036"}}>{cur.nei.a||cur.nei.advice}</p>}`,
  `{NOTES[cur.n]?.nei_insight&&<p style={{fontSize:"16px",lineHeight:2.2,color:"#4a4036",textIndent:"2em"}}>{NOTES[cur.n].nei_insight}</p>}`
);

writeFileSync('./src/App.jsx', app, 'utf8');
console.log('App.jsx updated successfully.');

// 验证：确认 deepNote 已删除，NOTES 已插入
if (app.includes('deepNote')) {
  console.warn('WARNING: deepNote still found in App.jsx — replacement may have missed something.');
} else {
  console.log('deepNote removed ✓');
}
if (app.includes('const NOTES=')) {
  console.log('NOTES inserted ✓');
} else {
  console.warn('WARNING: NOTES not found in App.jsx.');
}
