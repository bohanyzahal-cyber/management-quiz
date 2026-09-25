"""בונה את index.html מהתבנית + בנקי השאלות.

הרצה:  python build.py      (מתוך התיקייה הזו)
כותב גם ל-management-quiz/index.html וגם לעותק הנוח בתיקיית הקורס.

סכמת שאלה (בקובצי bank*.js):
  {l:5, t:"נושא", s:"מקור", q:"השאלה", o:["א","ב","ג","ד"], c:1, e:"הסבר"}
  l = מספר השיעור (1-13), c = אינדקס התשובה הנכונה לפני הערבוב.
מבחן המוכנות (ready.js, var READY=[...]) באותה סכמה, מחוץ לבנק: הוא לא מופיע בתרגול
ובהדפסה, ולכן נבדק גם שאין בו שאלה שדומה לשאלה מהבנק.
"""
import os, sys, re, glob, json, subprocess, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE   = os.path.dirname(os.path.abspath(__file__))
REPO   = os.path.dirname(HERE)                     # .../management-quiz
COURSE = os.path.dirname(REPO)                     # תיקיית הקורס

# (קובץ יעד, המילון שלצידו, דף הנגן של הפודקאסט) — כל קישור יחסי לתיקייה של
# הקובץ עצמו, ובתיקיית הקורס שמות הקבצים והנתיבים שונים
TARGETS = [
    (os.path.join(REPO, "index.html"), "מילון-מושגים.html", "podcast/index.html"),
    (os.path.join(COURSE, "בוחן תרגול - שיטות וכלי ניהול מתקדמים.html"),
     "מילון מושגים - שיטות וכלי ניהול מתקדמים.html", "management-quiz/podcast/index.html"),
]

def bank_files():
    """מיון מספרי — מיון לקסיקוגרפי היה שם את bank10 לפני bank2."""
    fs = glob.glob(os.path.join(HERE, "bank*.js"))
    return sorted(fs, key=lambda f: int(re.search(r"bank(\d+)", os.path.basename(f)).group(1)))

tpl  = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
bank = "\n".join(open(f, encoding="utf-8").read() for f in bank_files())
READY_JS = os.path.join(HERE, "ready.js")
ready = open(READY_JS, encoding="utf-8").read() if os.path.exists(READY_JS) else "var READY=[];"
html = tpl.replace("/*__BANK__*/", bank).replace("/*__READY__*/", ready)

# קישורים לעזרים נוספים (מילון מושגים, פודקאסט) — כל אחד מוצג רק אם הקובץ קיים
def aids_for(gloss_name, podcast_href):
    items = []
    if os.path.exists(os.path.join(REPO, "מילון-מושגים.html")):
        items.append('<a class="aid" href="' + gloss_name.replace('"', "&quot;") + '" target="_blank" rel="noopener">'
                     '<i>📖</i><span><b>מילון מושגים</b> · כל המונחים באנגלית ובעברית, לפי שיעור — לשינון לפני המבחן</span></a>')
    if os.path.exists(os.path.join(REPO, "podcast", "index.html")):
        items.append('<a class="aid" href="' + podcast_href + '" target="_blank" rel="noopener">'
                     '<i>🎧</i><span><b>פודקאסט</b> · פרק לכל נושא, עם שאלות לדרך — להאזנה בדרכים</span></a>')
    return ('<div class="aids">' + "".join(items) + "</div>") if items else ""

for t, gloss_name, podcast_href in TARGETS:
    open(t, "w", encoding="utf-8").write(html.replace("<!--AIDS-->", aids_for(gloss_name, podcast_href)))
    print("נכתב:", t)
html = html.replace("<!--AIDS-->", aids_for(TARGETS[0][1], TARGETS[0][2]))
print("גודל: %.0f KB" % (len(html) / 1024))

# ---------- סטטיסטיקה ----------
objs = re.findall(r'\{l:(\d+),t:"(.*?)",s:"(.*?)",q:', bank)
objs = [(int(l), t.replace('\\"', '"'), s.replace('\\"', '"')) for l, t, s in objs]
print("\nשאלות:", len(objs))

lects, topics, srcs = {}, {}, {}
for l, t, s in objs:
    lects[l]  = lects.get(l, 0) + 1
    topics[t] = topics.get(t, 0) + 1
    srcs[s]   = srcs.get(s, 0) + 1
print("\nלפי שיעור:")
for k in sorted(lects):
    print("  שיעור %-3d %3d" % (k, lects[k]))
print("לפי נושא:")
for k, v in sorted(topics.items(), key=lambda x: -x[1]):
    print("  %-34s %3d" % (k, v))
print("לפי מקור:")
for k, v in sorted(srcs.items(), key=lambda x: -x[1]):
    print("  %-16s %3d" % (k, v))
ready_l = [int(x) for x in re.findall(r'\{l:(\d+),t:"', ready)]
print("מבחן מוכנות: %d שאלות" % len(ready_l))

cs = re.findall(r',c:(\d),e:"', bank)
dist = {}
for c in cs:
    dist[c] = dist.get(c, 0) + 1
print("\nפיזור אינדקס התשובה הנכונה במקור:", dict(sorted(dist.items())))
if len(cs) != len(objs):
    print("!! אזהרה: לא כל השאלות נותחו (%d מתוך %d)" % (len(cs), len(objs)))

# ---------- עדכון אוטומטי של ה-README ----------
def update_readme():
    path = os.path.join(REPO, "README.md")
    if not os.path.exists(path):
        return
    txt = open(path, encoding="utf-8").read()
    start, end = "<!-- STATS:START", "<!-- STATS:END -->"
    i, j = txt.find(start), txt.find(end)
    if i < 0 or j < 0:
        return
    LNAME = {1:"מבוא לניהול (1)",2:"מבוא לניהול (2)",3:"תכנון (1)",4:"תכנון (2)",5:"ארגון (1)",6:"ארגון (2)",
             7:"מנהיגות",8:"בקרה",9:"ניהול צוות (1)",10:"ניהול צוות (2)",11:"שינוי ותקשורת",
             12:"תרבות ארגונית (1)",13:"תרבות ארגונית (2)"}
    lines = ["| שיעור | נושא | שאלות |", "|---|---|---|"]
    for k in sorted(lects):
        lines.append("| %d | %s | %d |" % (k, LNAME.get(k, ""), lects[k]))
    src_line = " · ".join("%s (%d)" % (k, v) for k, v in sorted(srcs.items(), key=lambda x: -x[1]))
    if ready_l:
        src_line += "\n\n**מבחן מוכנות:** %d שאלות נוספות משיעורים %d–%d, מחוץ לבנק (לא מופיעות בתרגול ובהדפסה)" % (
            len(ready_l), min(ready_l), max(ready_l))
    top_line = " · ".join("%s (%d)" % (k, v) for k, v in topics.items())
    block = (
        "<!-- STATS:START — נוצר אוטומטית על ידי src/build.py, אין לערוך ידנית -->\n"
        "**%d שאלות** בפורמט המבחן — רב-ברירתי (אמריקאי), 4 תשובות לשאלה.\n\n"
        "%s\n\n"
        "**לפי מקור:** %s\n\n"
        "**נושאים:** %s\n"
        % (len(objs), "\n".join(lines), src_line, top_line)
    )
    open(path, "w", encoding="utf-8").write(txt[:i] + block + txt[j:])
    print("עודכן:", path)

update_readme()

# ---------- בדיקות מבנה ----------
STRUCT = r"""
const fs=require('fs');
eval(fs.readFileSync(process.argv[2],'utf8'));
/* דפוסים תלויי-מיקום: האפליקציה מערבבת את סדר האפשרויות בכל סבב,
   ולכן מסיח כמו "כל התשובות נכונות" או "תשובות א'+ב'" נשבר. */
const POS=/כל התשובות נכונות|כל ההיגדים נכונים|כל הנ["״']ל|תשובות? א['׳']\s*(\+|ו)|א['׳']\s*(\+|ו-?)\s*ב['׳']|אף תשובה אינה|כל האמור לעיל|אף אחת מהתשובות|כל האפשרויות/;
const err=[], seen={};
BANK.forEach((q,i)=>{
  const at=`#${i} ${(q.q||'').slice(0,40)}`;
  if(typeof q.l!=='number'||q.l<1||q.l>13)  err.push(at+' — מספר שיעור חסר/שגוי');
  if(!q.t||!q.s||!q.q||!q.e)             err.push(at+' — שדה חסר');
  if(!Array.isArray(q.o)||q.o.length!==4) err.push(at+' — אין בדיוק 4 אפשרויות');
  else if(new Set(q.o).size!==4)          err.push(at+' — אפשרות כפולה');
  if(typeof q.c!=='number'||q.c<0||q.c>3) err.push(at+' — c מחוץ לתחום');
  if((q.o||[]).some(o=>POS.test(o)))      err.push(at+' — מסיח תלוי-מיקום');
  (q.o||[]).forEach((o)=>{
    const w=String(o).split(/\s+/);
    for(let k=0;k+1<w.length;k++){
      if(w[k].length>=4 && w[k]===w[k+1]) { err.push(at+' — מילה כפולה ברצף: "'+w[k]+'"'); break; }
      if(k+3<w.length && w[k].length>=4 && w[k]===w[k+3] && w[k+1]===w[k+4]) {
        err.push(at+' — ביטוי חוזר: "'+w.slice(k,k+2).join(' ')+'"'); break;
      }
    }
  });
  if((q.e||'').length<40)                 err.push(at+' — הסבר קצר מדי');
  if(seen[q.q]!==undefined)               err.push(at+' — שאלה כפולה (גם ב-#'+seen[q.q]+')');
  else seen[q.q]=i;
});

/* מפתח תשובה שגוי: c מצביע על מסיח בעוד ההסבר מתאר אפשרות אחרת.
   מדד רועש — לכן זו התראה לבדיקה ידנית ולא שגיאה. */
const STOP=new Set(('של את על אל כי גם רק אם לא זה זו אלה הוא היא הם הן אני אתה אנחנו יש אין כל כמו אבל או אז מה מי איך למה כאשר לאחר לפני בתוך בין עם ללא אשר היה היו יהיה להיות אינו אינה אינם מפני מכיוון בגלל כדי לכן ולכן אלא אף כך יותר פחות מאוד ממש בדרך כלל למשל דוגמה בהרצאה המרצה שהוא שהיא ניתן צריך יכול אפשר בפועל בלבד כמובן עדיין זאת אותו אותה אותם לפי השקף במצגת בשיעור').split(' '));
const stem=w=>w.replace(/^(כש|לכ|מה|שה|וה|וב|ול|ומ|ו|ה|ב|ל|מ|ש|כ)/,'');
const toks=s=>{const o=new Set();String(s).split(/[^\wא-ת]+/).forEach(w=>{
  if(w.length>=4 && !STOP.has(w)) o.add(stem(w));});return o;};
const key=[];
BANK.forEach((q,i)=>{
  if(!q.e||!Array.isArray(q.o)) return;
  const E=toks(q.e);
  const sc=q.o.map(o=>{const O=toks(o);let n=0;O.forEach(x=>{if(E.has(x))n++;});
                       return O.size? n/Math.sqrt(O.size):0;});
  const best=sc.indexOf(Math.max(...sc));
  if(best!==q.c && sc[best]-sc[q.c] > 1.5)
    key.push('#'+i+' מסומן '+q.c+' אך ההסבר מתאים ל-'+best+' — '+(q.q||'').slice(0,44));
});
console.log(JSON.stringify({n:BANK.length,err,key}));
"""

try:
    with tempfile.TemporaryDirectory() as td:
        jsf = os.path.join(td, "all.js")
        open(jsf, "w", encoding="utf-8").write(bank)
        chk = os.path.join(td, "struct.js")
        open(chk, "w", encoding="utf-8").write(STRUCT)
        r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise RuntimeError((r.stderr or "")[:300])
        s = json.loads(r.stdout.strip())
        print("\nבדיקות מבנה (%d שאלות):" % s["n"])
        if s["err"]:
            for e in s["err"][:40]:
                print("  !!", e)
            if len(s["err"]) > 40:
                print("  ... ועוד %d" % (len(s["err"]) - 40))
        else:
            print("  תקין — ללא כפילויות, שדות חסרים או מסיחים תלויי-מיקום.")
        for k in s.get("key", []):
            print("  !! מפתח תשובה:", k)
        if ready_l:
            open(jsf, "w", encoding="utf-8").write(ready.replace("var READY", "var BANK", 1))
            r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                raise RuntimeError((r.stderr or "")[:300])
            s = json.loads(r.stdout.strip())
            print("\nבדיקות מבנה — מבחן מוכנות (%d שאלות):" % s["n"])
            for e in s["err"]:
                print("  !!", e)
            for k in s.get("key", []):
                print("  !! מפתח תשובה:", k)
            if not s["err"]:
                print("  תקין.")
except Exception as e:
    print("\n(בדיקות המבנה דילגו — נדרש node:", e, ")")

# ---------- מבחן המוכנות לא חוזר על שאלות מהבנק ----------
# אם שאלה במבחן המוכנות דומה לשאלה שכבר תורגלה, הציון שוב מודד זיכרון ולא שליטה בחומר.
def stems(js):
    return [x.replace('\\"', '"') for x in re.findall(r'q:"((?:[^"\\]|\\.)*)"', js)]

def words(t):
    out = set()
    for w in re.findall(r"[\wא-ת']+", t):
        w = re.sub(r"^(וכש|כש|וה|וב|ול|ומ|ה|ב|ל|מ|ש|ו|כ)(?=[א-ת]{3})", "", w)
        if len(w) >= 3:
            out.add(w)
    return out

if ready_l:
    bank_stems = [(x, words(x)) for x in stems(bank)]
    close = []
    for rq in stems(ready):
        rw = words(rq)
        best, bq = 0.0, ""
        for bq_, bw in bank_stems:
            if not rw or not bw:
                continue
            j = len(rw & bw) / len(rw | bw)
            if j > best:
                best, bq = j, bq_
        if best >= 0.45:
            close.append((best, rq, bq))
    print("\nמבחן מוכנות מול הבנק:")
    if close:
        for j, rq, bq in sorted(close, reverse=True):
            print("  !! דומה (%.2f): %s\n       בבנק: %s" % (j, rq[:70], bq[:70]))
    else:
        print("  תקין — אין שאלה שדומה לשאלה מהבנק.")

# ---------- בדיקת "תל האורך" ----------
# כשכותבים שאלות בכמות, התשובה הנכונה יוצאת כמעט תמיד הארוכה ביותר,
# ואז אפשר לענות נכון בלי לקרוא. זו בדיקה שהבעיה לא חזרה.
CHECK = r"""
const fs=require('fs');
eval(fs.readFileSync(process.argv[2],'utf8'));
const n=BANK.length, rank=[0,0,0,0];
let long=0, short=0, outlierHit=0;
const outliers=[];
BANK.forEach((q,qi)=>{
  const L=q.o.map(o=>o.length), max=Math.max(...L), min=Math.min(...L);
  if(L.indexOf(max)===q.c) long++;
  if(L.indexOf(min)===q.c) short++;
  rank[L.map((l,i)=>[l,i]).sort((a,b)=>b[0]-a[0]).map(x=>x[1]).indexOf(q.c)]++;
  const d=L.filter((_,i)=>i!==q.c), avg=d.reduce((a,b)=>a+b,0)/d.length;
  const gap=(L[q.c]-avg)/avg;
  if(Math.abs(gap)>=0.40) outliers.push({i:qi,q:q.q.slice(0,42),pct:Math.round(gap*100)});
  const mean=L.reduce((a,b)=>a+b,0)/4;
  const far=L.map((l,i)=>[Math.abs(l-mean),i]).sort((a,b)=>b[0]-a[0])[0][1];
  if(far===q.c) outlierHit++;
});
console.log(JSON.stringify({n,long,short,rank,outliers,outlierHit}));
"""
def length_stats(js_text, td, tag):
    jsf = os.path.join(td, "b_%s.js" % tag)
    prefix = "" if js_text.lstrip().startswith("var BANK") else "var BANK=[];\n"
    open(jsf, "w", encoding="utf-8").write(prefix + js_text)
    chk = os.path.join(td, "check.js")
    if not os.path.exists(chk):
        open(chk, "w", encoding="utf-8").write(CHECK)
    r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or "")[:200])
    return json.loads(r.stdout.strip())

def report(s, label, indent="  "):
    n = s["n"]
    if not n:
        return False
    pct = lambda x: int(round(x / n * 100))
    flag = "  <-- !!" if max(pct(s["long"]), pct(s["short"])) > 45 else ""
    print("%s%-14s n=%-4d ארוכה=%3d%%  קצרה=%3d%%  (פיזור %s)%s"
          % (indent, label, n, pct(s["long"]), pct(s["short"]),
             "/".join("%d" % pct(x) for x in s["rank"]), flag))
    return bool(flag)

try:
    with tempfile.TemporaryDirectory() as td:
        print("\nבדיקת אורך התשובות (כדי שלא ניתן יהיה לענות בלי לקרוא) — [מקרי ≈ 25%, אחיד = 25/25/25/25]:")
        bad_files = []
        for f in bank_files():
            name = os.path.basename(f)
            txt = open(f, encoding="utf-8").read()
            if report(length_stats(txt, td, name), name):
                bad_files.append(name)
        if ready_l:
            if report(length_stats(ready.replace("var READY", "var BANK", 1), td, "ready"), "ready.js"):
                bad_files.append("ready.js")
        print("  " + "-" * 58)
        all_stats = length_stats(bank, td, "all")
        report(all_stats, "סה\"כ")
        out = all_stats.get("outliers", [])
        n_all = all_stats["n"]
        hit = all_stats.get("outlierHit", 0)
        pct_hit = int(round(hit / n_all * 100)) if n_all else 0
        longish = sum(1 for o in out if o["pct"] > 0)
        print("\n  חריגות אורך (פער מממוצע המסיחים, לא דירוג):")
        print("    %d שאלות חורגות ב-40%% ומעלה — %d ארוכות מדי, %d קצרות מדי"
              % (len(out), longish, len(out) - longish))
        print("    אסטרטגיית \"בחר את החורגת ביותר\": %d%%%s"
              % (pct_hit, "   <-- !!" if pct_hit > 45 else "   (מקרי 25%)"))
        if "--outliers" in sys.argv:
            for o in out:
                print("      #%d %+d%%  %s" % (o["i"], o["pct"], o["q"]))
        if bad_files:
            print("  !! חריגה ב:", ", ".join(bad_files),
                  "— אפשר לצבור שם מעל 45% בלי לקרוא. הארך (או קצר) מסיחים בקובץ החורג.")
        else:
            print("  תקין — אף אסטרטגיה עיוורת אינה עוברת 45% באף קובץ.")
except Exception as e:
    print("\n(בדיקת האורך דילגה — נדרש node:", e, ")")
