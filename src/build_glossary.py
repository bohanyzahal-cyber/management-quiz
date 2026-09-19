"""בונה את מילון המושגים (מילון-מושגים.html) מקובצי src/glossary/L{n}.md.

הרצה: python build_glossary.py   (מתוך התיקייה הזו)

פורמט כל קובץ: שורות בסגנון
  - **English term / מונח בעברית** — הסבר כפי שניתן בכיתה
שורות אחרות (כותרות, הערות) מתעלמים מהן.
"""
import os, re, io, glob, sys, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE   = os.path.dirname(os.path.abspath(__file__))
REPO   = os.path.dirname(HERE)
COURSE = os.path.dirname(REPO)
GLOSS  = os.path.join(HERE, "glossary")
# כל עותק מקושר לבוחן שנמצא לצידו באותה תיקייה (שמות הקבצים שונים בין התיקיות)
TARGETS = [(os.path.join(REPO, "מילון-מושגים.html"), "index.html"),
           (os.path.join(COURSE, "מילון מושגים - שיטות וכלי ניהול מתקדמים.html"),
            "בוחן תרגול - שיטות וכלי ניהול מתקדמים.html")]

LNAME = {1:"מבוא לניהול (1)",2:"מבוא לניהול (2)",3:"תכנון (1)",4:"תכנון (2)",5:"ארגון (1)",6:"ארגון (2)",
         7:"מנהיגות",8:"בקרה",9:"ניהול צוות (1)",10:"ניהול צוות (2)",11:"חדשנות ושינוי",
         12:"תרבות ארגונית (1)",13:"תרבות ארגונית (2)"}

def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<i>\1</i>", s)
    return s

def parse(path):
    items = []
    for line in io.open(path, encoding="utf-8"):
        m = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*(.*)$", line.rstrip())
        if not m:
            continue
        term, rest = m.group(1).strip(), m.group(2).strip()
        rest = re.sub(r"^[—–-]\s*", "", rest)
        items.append((term, rest))
    return items

files = sorted(glob.glob(os.path.join(GLOSS, "L*.md")),
               key=lambda f: int(re.search(r"L(\d+)", os.path.basename(f)).group(1)))
sections, total = [], 0
for f in files:
    n = int(re.search(r"L(\d+)", os.path.basename(f)).group(1))
    items = parse(f)
    total += len(items)
    rows = []
    for term, rest in items:
        parts = [p.strip() for p in re.split(r"\s/\s", term, maxsplit=1)]
        en, he = (parts[0], parts[1]) if len(parts) == 2 else (term, "")
        rows.append('<div class="term" data-s="%s"><div class="t"><b>%s</b>%s</div><div class="d">%s</div></div>'
                    % (html.escape((term + " " + rest).lower(), quote=True),
                       md_inline(en), (' <span class="he">' + md_inline(he) + '</span>') if he else "",
                       md_inline(rest)))
    sections.append((n, len(items), "\n".join(rows)))
    print("שיעור %d: %d מושגים" % (n, len(items)))

nav = " · ".join('<a href="#l%d">שיעור %d</a>' % (n, n) for n, _, _ in sections)
body = "\n".join(
    '<section id="l%d"><h2>שיעור %d — %s <small>%d מושגים</small></h2>%s</section>' % (n, n, LNAME.get(n, ""), c, rows)
    for n, c, rows in sections)

page = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>מילון מושגים — שיטות וכלי ניהול מתקדמים</title>
<style>
:root{--bg:#f7f6f3;--surface:#fff;--surface2:#f1efe8;--text:#1f1f1d;--muted:#6b6b66;--border:#e3e1da;--accent:#0f766e;--accentSoft:#e2f2ef;--onAccent:#fff;}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a18;--surface:#242421;--surface2:#2f2f2c;--text:#ececea;--muted:#a3a39c;--border:#37372f;--accent:#5fd3c0;--accentSoft:#143d38;--onAccent:#0b1f1c;}}
html.dark{--bg:#1a1a18;--surface:#242421;--surface2:#2f2f2c;--text:#ececea;--muted:#a3a39c;--border:#37372f;--accent:#5fd3c0;--accentSoft:#143d38;--onAccent:#0b1f1c;}
html.light{--bg:#f7f6f3;--surface:#fff;--surface2:#f1efe8;--text:#1f1f1d;--muted:#6b6b66;--border:#e3e1da;--accent:#0f766e;--accentSoft:#e2f2ef;--onAccent:#fff;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:'Segoe UI',Arial,sans-serif;line-height:1.6;}
.wrap{max-width:860px;margin:0 auto;padding:22px 20px 60px;}
h1{font-size:23px;margin:0 0 4px;font-weight:650;}
.sub{color:var(--muted);font-size:13.5px;margin-bottom:14px;}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:2;}
input{flex:1;min-width:200px;padding:10px 14px;border-radius:10px;border:1px solid var(--border);background:var(--surface);color:var(--text);font:inherit;font-size:15px;}
input:focus{outline:2px solid var(--accent);border-color:var(--accent);}
.btn{background:var(--surface2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:8px 12px;font:inherit;font-size:13px;cursor:pointer;}
.nav{font-size:13px;color:var(--muted);margin-bottom:16px;line-height:2;}
.nav a{color:var(--accent);text-decoration:none;}
section{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 20px;margin-bottom:14px;}
h2{font-size:17px;margin:0 0 10px;color:var(--accent);}
h2 small{color:var(--muted);font-weight:400;font-size:12.5px;margin-right:6px;}
.term{padding:8px 0;border-top:1px solid var(--border);}
.term:first-of-type{border-top:0;}
.term .t{font-size:15px;}
.term .t b{color:var(--text);}
.term .he{color:var(--accent);font-weight:600;margin-right:6px;}
.term .d{font-size:13.5px;color:var(--muted);margin-top:2px;}
.term.hide,section.hide{display:none;}
.count{font-size:12.5px;color:var(--muted);}
a.back{color:var(--accent);font-size:13px;text-decoration:none;}
@media print{
  @page{size:A4;margin:11mm 10mm;}
  html,body{background:#fff!important;color:#000!important;}
  .bar,.nav,a.back{display:none!important;}
  .wrap{max-width:none;padding:0;column-count:2;column-gap:8mm;column-rule:1px solid #ccc;font-size:9pt;}
  h1{column-span:all;font-size:14pt;} .sub{column-span:all;}
  section{border:0;padding:0;margin:0 0 4mm;break-inside:avoid-column;}
  h2{font-size:11pt;color:#000;} .term{padding:2px 0;break-inside:avoid;}
  .term .t{font-size:9.5pt;} .term .d{font-size:8.6pt;color:#333;}
}
</style>
</head>
<body>
<div class="wrap">
<h1>מילון מושגים — שיטות וכלי ניהול מתקדמים</h1>
<div class="sub">__TOTAL__ מושגים מ-__N__ שיעורים · המונח באנגלית כפי שמופיע בשקפים, ההסבר בעברית כפי שניתן בכיתה · <a class="back" href="__QUIZ__">→ חזרה לבוחן התרגול</a></div>
<div class="bar">
  <input id="q" type="search" placeholder="חיפוש מונח (עברית או אנגלית)…" autocomplete="off">
  <span class="count" id="cnt"></span>
  <button class="btn" id="print">🖨 הדפסה</button>
  <button class="btn" id="theme">◐</button>
</div>
<div class="nav">__NAV__</div>
__BODY__
</div>
<script>
(function(){
  var q=document.getElementById('q'),cnt=document.getElementById('cnt');
  var terms=[].slice.call(document.querySelectorAll('.term')),secs=[].slice.call(document.querySelectorAll('section'));
  function run(){
    var s=q.value.trim().toLowerCase(),n=0;
    terms.forEach(function(t){var on=!s||t.getAttribute('data-s').indexOf(s)>=0;t.classList.toggle('hide',!on);if(on)n++;});
    secs.forEach(function(x){x.classList.toggle('hide',!x.querySelector('.term:not(.hide)'));});
    cnt.textContent=s?(n+' מתוך '+terms.length):'';
  }
  q.addEventListener('input',run);
  document.getElementById('print').onclick=function(){window.print();};
  var t=null;try{t=localStorage.getItem('amq_theme');}catch(e){}
  if(t)document.documentElement.className=t;
  document.getElementById('theme').onclick=function(){
    var cur=document.documentElement.className;
    var dark=cur==='dark'||(cur!=='light'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);
    var nx=dark?'light':'dark';document.documentElement.className=nx;
    try{localStorage.setItem('amq_theme',nx);}catch(e){}
  };
})();
</script>
</body>
</html>
"""
page = (page.replace("__TOTAL__", str(total)).replace("__N__", str(len(sections)))
            .replace("__NAV__", nav).replace("__BODY__", body))
for t, quiz in TARGETS:
    io.open(t, "w", encoding="utf-8").write(page.replace("__QUIZ__", html.escape(quiz, quote=True)))
    print("נכתב:", t)
print("סה\"כ מושגים:", total)
