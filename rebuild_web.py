import os

SRC = r"C:\Users\lkero\OneDrive\Desktop\SQLI\injecta\core\web.py"
DST = r"C:\Users\lkero\OneDrive\Desktop\SQLI\injecta\core\web_new.py"

# Read existing Python handler (keep all the API logic)
with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# Find the position of DASHBOARD_HTML assignment
marker = "DASHBOARD_HTML = "
idx = content.find(marker)
if idx == -1:
    print("ERROR: DASHBOARD_HTML marker not found")
    exit(1)

# Keep only Python handler code (before DASHBOARD_HTML)
python_code = content[:idx]

# New HTML dashboard - burgundy/gaming inspired
html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Injecta Intelligence</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}

:root{
  --bg-deep:#0d0303;
  --bg-body:#1a0808;
  --bg-card:rgba(45,15,15,0.6);
  --bg-card-hover:rgba(55,20,20,0.8);
  --bg-glass:rgba(139,0,0,0.08);
  --bg-glass-hover:rgba(139,0,0,0.15);
  --sidebar-bg:rgba(20,8,8,0.9);
  --topbar-bg:rgba(13,3,3,0.85);
  --border:rgba(139,0,0,0.15);
  --border-hover:rgba(139,0,0,0.3);
  --accent:#c41e3a;
  --accent2:#8b0000;
  --accent3:#dc143c;
  --purple:#7c3aed;
  --purple-dark:#5b21b6;
  --pink:#ec4899;
  --pink-glow:rgba(236,72,153,0.2);
  --red-glow:rgba(196,30,58,0.2);
  --text:#faf5f5;
  --text2:rgba(250,245,245,0.6);
  --text3:rgba(250,245,245,0.35);
  --radius-sm:12px;
  --radius-md:20px;
  --radius-lg:28px;
  --radius-xl:34px;
  --shadow:0 8px 40px rgba(0,0,0,0.5);
  --shadow-glow:0 8px 40px rgba(196,30,58,0.15);
  --font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  --transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}

body{
  font-family:var(--font);
  background:var(--bg-body);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(139,0,0,0.12) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(124,58,237,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(196,30,58,0.06) 0%, transparent 50%);
}

/* Layout */
.app{display:flex;min-height:100vh;position:relative}

/* Sidebar */
.sidebar{
  position:fixed;left:0;top:0;bottom:0;width:72px;
  background:var(--sidebar-bg);
  backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);
  border-right:1px solid var(--border);
  z-index:100;
  display:flex;flex-direction:column;align-items:center;
  padding:20px 0;gap:8px;
}
.sidebar-logo{
  width:44px;height:44px;border-radius:var(--radius-sm);
  background:linear-gradient(135deg,var(--accent),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.5px;
  box-shadow:0 4px 16px var(--red-glow);
  margin-bottom:24px;cursor:pointer;
}
.sidebar-logo span{color:rgba(255,255,255,0.6)}
.sidebar-nav{display:flex;flex-direction:column;gap:4px;flex:1}
.sidebar-btn{
  width:48px;height:48px;border-radius:var(--radius-sm);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;transition:var(--transition);
  color:var(--text3);border:none;background:transparent;
  position:relative;
}
.sidebar-btn:hover{color:var(--text);background:var(--bg-glass)}
.sidebar-btn.active{
  color:var(--accent);background:var(--red-glow);
  box-shadow:inset 0 0 20px rgba(196,30,58,0.1);
}
.sidebar-btn svg{width:20px;height:20px}
.sidebar-bottom{margin-top:auto;display:flex;flex-direction:column;gap:4px}
.sidebar-btn .badge{
  position:absolute;top:8px;right:8px;
  width:6px;height:6px;border-radius:50%;
  background:var(--pink);box-shadow:0 0 8px var(--pink-glow);
}

/* Top Bar */
.topbar{
  position:fixed;top:16px;left:88px;right:16px;height:52px;
  background:var(--topbar-bg);
  backdrop-filter:blur(24px);
  -webkit-backdrop-filter:blur(24px);
  border:1px solid var(--border);
  border-radius:var(--radius-lg);
  z-index:99;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;
  box-shadow:var(--shadow);
}
.topbar-left{display:flex;align-items:center;gap:16px}
.topbar-search{
  display:flex;align-items:center;gap:8px;
  padding:8px 16px;border-radius:20px;
  background:rgba(255,255,255,0.03);
  border:1px solid var(--border);
  color:var(--text2);font-size:13px;width:280px;
  font-family:var(--font);outline:none;transition:var(--transition);
}
.topbar-search:focus{border-color:var(--accent);background:rgba(255,255,255,0.05);color:var(--text)}
.topbar-search::placeholder{color:var(--text3)}
.topbar-right{display:flex;align-items:center;gap:12px}
.topbar-btn{
  width:36px;height:36px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;transition:var(--transition);
  color:var(--text2);border:none;background:var(--bg-glass);
  position:relative;
}
.topbar-btn:hover{background:var(--bg-glass-hover);color:var(--text)}
.topbar-btn svg{width:16px;height:16px}
.topbar-btn .dot{
  position:absolute;top:9px;right:9px;
  width:5px;height:5px;border-radius:50%;
  background:var(--pink);
}
.topbar-avatar{
  width:32px;height:32px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;color:#fff;cursor:pointer;
}

/* Main Content */
.main{
  margin-left:72px;margin-top:84px;padding:0 24px 24px;
  flex:1;max-width:calc(100% - 72px);
}
.main-inner{display:flex;gap:24px}
.main-left{flex:1;min-width:0}
.main-right{width:320px;flex-shrink:0;display:flex;flex-direction:column;gap:16px}

/* Hero Card */
.hero-card{
  background:linear-gradient(145deg, rgba(45,15,15,0.7), rgba(30,10,10,0.5));
  border:1px solid var(--border);
  border-radius:var(--radius-xl);
  padding:32px 36px;
  position:relative;overflow:hidden;
  margin-bottom:24px;
  box-shadow:var(--shadow);
}
.hero-card::before{
  content:'';position:absolute;top:-120px;right:-80px;
  width:400px;height:400px;
  background:radial-gradient(circle, rgba(196,30,58,0.08) 0%, transparent 70%);
  border-radius:50%;pointer-events:none;
}
.hero-card::after{
  content:'';position:absolute;bottom:-100px;left:-60px;
  width:300px;height:300px;
  background:radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%);
  border-radius:50%;pointer-events:none;
}
.hero-inner{display:flex;gap:40px;align-items:center;position:relative;z-index:1}
.hero-left{flex:1}
.hero-badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:4px 14px;border-radius:20px;
  font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;
  background:linear-gradient(135deg, rgba(196,30,58,0.15), rgba(124,58,237,0.1));
  color:var(--pink);border:1px solid rgba(236,72,153,0.15);
  margin-bottom:16px;
}
.hero-badge svg{width:12px;height:12px}
.hero-title{
  font-size:36px;font-weight:800;line-height:1.15;letter-spacing:-1px;
  margin-bottom:12px;
  background:linear-gradient(135deg, #fff 20%, var(--accent) 50%, var(--purple) 80%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.hero-desc{font-size:14px;color:var(--text2);line-height:1.6;max-width:480px;margin-bottom:20px}
.hero-actions{display:flex;gap:10px;flex-wrap:wrap}
.hero-btn{
  display:inline-flex;align-items:center;gap:8px;
  padding:12px 24px;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;border:none;
  font-family:var(--font);transition:var(--transition);
  text-decoration:none;
}
.hero-btn-primary{
  background:linear-gradient(135deg, var(--accent), var(--purple));
  color:#fff;box-shadow:0 4px 24px var(--red-glow);
}
.hero-btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 32px var(--red-glow)}
.hero-btn-secondary{
  background:var(--bg-glass);color:var(--text);
  border:1px solid var(--border);
}
.hero-btn-secondary:hover{background:var(--bg-glass-hover);border-color:var(--border-hover);transform:translateY(-2px)}
.hero-tags{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.hero-tag{
  padding:4px 12px;border-radius:8px;
  font-size:11px;font-weight:500;color:var(--text2);
  background:var(--bg-glass);border:1px solid var(--border);
}
.hero-visual{
  width:280px;height:220px;flex-shrink:0;
  position:relative;overflow:hidden;
  border-radius:var(--radius-md);
  background:linear-gradient(135deg, rgba(139,0,0,0.1), rgba(124,58,237,0.05));
  border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;
}
.hero-visual svg{width:180px;height:180px;opacity:0.6}

/* Stats Grid */
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.stat-card{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:var(--radius-md);
  padding:20px;
  transition:var(--transition);cursor:default;
  position:relative;overflow:hidden;
}
.stat-card:hover{background:var(--bg-card-hover);border-color:var(--border-hover);transform:translateY(-2px);box-shadow:var(--shadow)}
.stat-card .sc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.stat-card .sc-icon{
  width:36px;height:36px;border-radius:var(--radius-sm);
  display:flex;align-items:center;justify-content:center;
}
.stat-card .sc-icon.red{background:rgba(196,30,58,0.12);color:var(--accent)}
.stat-card .sc-icon.purple{background:rgba(124,58,237,0.12);color:var(--purple)}
.stat-card .sc-icon.pink{background:rgba(236,72,153,0.12);color:var(--pink)}
.stat-card .sc-icon.rose{background:rgba(220,20,60,0.12);color:var(--accent3)}
.stat-card .sc-icon svg{width:16px;height:16px}
.stat-card .sc-value{font-size:28px;font-weight:800;letter-spacing:-0.5px;margin-bottom:2px}
.stat-card .sc-label{font-size:12px;color:var(--text2)}
.stat-card .sc-trend{
  padding:2px 8px;border-radius:6px;font-size:10px;font-weight:600;
}
.stat-card .sc-trend.up{background:rgba(196,30,58,0.1);color:var(--accent)}
.stat-card .sc-trend.steady{background:rgba(124,58,237,0.1);color:var(--purple)}
.stat-card .sc-glow{
  position:absolute;top:-40px;right:-40px;
  width:100px;height:100px;border-radius:50%;filter:blur(40px);
  pointer-events:none;
}
.stat-card .sc-glow.red{background:rgba(196,30,58,0.08)}
.stat-card .sc-glow.purple{background:rgba(124,58,237,0.06)}
.stat-card .sc-glow.pink{background:rgba(236,72,153,0.06)}

/* Right Panel */
.right-card{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:var(--radius-md);
  padding:20px;
  transition:var(--transition);
}
.right-card:hover{border-color:var(--border-hover)}
.right-card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.right-card-title{font-size:13px;font-weight:600;letter-spacing:-0.2px}
.right-card-action{font-size:11px;color:var(--text3);cursor:pointer;transition:var(--transition)}
.right-card-action:hover{color:var(--accent)}

/* Circular Progress */
.circular-progress{
  width:160px;height:160px;margin:0 auto 16px;position:relative;
}
.circular-progress svg{transform:rotate(-90deg);width:160px;height:160px}
.circular-progress .bg{fill:none;stroke:rgba(255,255,255,0.04);stroke-width:8}
.circular-progress .fg{
  fill:none;stroke:url(#circGrad);stroke-width:8;
  stroke-linecap:round;
  stroke-dasharray:440;stroke-dashoffset:88;
  transition:stroke-dashoffset 1s ease;
}
.circular-progress .center{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  text-align:center;
}
.circular-progress .center .val{font-size:32px;font-weight:800;letter-spacing:-1px}
.circular-progress .center .lbl{font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:0.5px}

/* Metrics list inside right panel */
.metrics-list{display:flex;flex-direction:column;gap:10px}
.metric-item{display:flex;align-items:center;justify-content:space-between;font-size:12px}
.metric-item .mi-label{color:var(--text2)}
.metric-item .mi-value{font-weight:600;color:var(--text)}
.metric-item .mi-bar{
  flex:1;height:4px;border-radius:2px;
  background:rgba(255,255,255,0.04);margin:0 10px;overflow:hidden;
}
.metric-item .mi-bar .fill{
  height:100%;border-radius:2px;
  background:linear-gradient(90deg, var(--accent), var(--purple));
  transition:width 0.6s ease;
}

/* Activity */
.activity-list{display:flex;flex-direction:column;gap:10px}
.activity-item{
  display:flex;align-items:flex-start;gap:12px;
  padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);
}
.activity-item:last-child{border-bottom:none}
.activity-dot{
  width:8px;height:8px;border-radius:50%;margin-top:4px;flex-shrink:0;
}
.activity-dot.info{background:var(--accent)}
.activity-dot.ok{background:#34d399}
.activity-dot.warn{background:var(--pink)}
.activity-dot.purp{background:var(--purple)}
.activity-content{flex:1;min-width:0}
.activity-text{font-size:12px;color:var(--text);line-height:1.4}
.activity-time{font-size:10px;color:var(--text3);margin-top:2px}

/* Targets */
.target-item{
  display:flex;align-items:center;gap:12px;padding:8px 0;
  border-bottom:1px solid rgba(255,255,255,0.03);
}
.target-item:last-child{border-bottom:none}
.target-icon{
  width:32px;height:32px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  background:var(--bg-glass);flex-shrink:0;
}
.target-icon svg{width:14px;height:14px;color:var(--text2)}
.target-info{flex:1;min-width:0}
.target-name{font-size:12px;font-weight:600;color:var(--text)}
.target-status{font-size:10px;color:var(--text3);margin-top:1px}
.target-progress{width:60px;height:4px;border-radius:2px;background:rgba(255,255,255,0.04);overflow:hidden;flex-shrink:0}
.target-progress .fill{
  height:100%;border-radius:2px;
  background:linear-gradient(90deg, var(--accent), var(--purple));
  transition:width 0.6s ease;
}

/* Monitor / Console sections (tabbed content) */
.content-section{display:none}
.content-section.active{display:block}

.scan-workspace{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
.workspace-card{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:var(--radius-md);
  padding:24px;
}
.workspace-card-title{font-size:13px;font-weight:600;margin-bottom:16px}
.workspace-input-group{display:flex;gap:0;margin-bottom:12px}
.workspace-input{
  flex:1;padding:12px 16px;border-radius:var(--radius-sm) 0 0 var(--radius-sm);
  background:rgba(255,255,255,0.03);border:1px solid var(--border);
  border-right:none;color:var(--text);font-size:13px;
  font-family:var(--font);outline:none;transition:var(--transition);
}
.workspace-input:focus{background:rgba(255,255,255,0.05);border-color:var(--accent)}
.workspace-input::placeholder{color:var(--text3)}
.workspace-btn{
  padding:12px 24px;border-radius:0 var(--radius-sm) var(--radius-sm) 0;
  background:linear-gradient(135deg, var(--accent), var(--purple));
  color:#fff;font-size:13px;font-weight:600;border:none;cursor:pointer;
  font-family:var(--font);transition:var(--transition);white-space:nowrap;
}
.workspace-btn:hover{filter:brightness(1.15)}
.workspace-chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
.workspace-chip{
  display:flex;align-items:center;gap:6px;
  padding:6px 12px;border-radius:8px;
  background:var(--bg-glass);border:1px solid var(--border);
  cursor:pointer;transition:var(--transition);
  font-size:11px;font-weight:500;color:var(--text2);
}
.workspace-chip:hover{border-color:var(--border-hover);background:var(--bg-glass-hover)}
.workspace-chip.active{background:rgba(196,30,58,0.1);border-color:var(--accent);color:var(--accent)}
.workspace-chip .dot{width:5px;height:5px;border-radius:50%}
.workspace-chip .dot.on{background:var(--accent)}
.workspace-chip .dot.off{background:var(--text3)}

/* Monitor Terminal */
.monitor-box{
  background:rgba(0,0,0,0.3);border:1px solid var(--border);
  border-radius:var(--radius-md);overflow:hidden;margin-bottom:24px;
}
.monitor-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;background:rgba(255,255,255,0.02);
  border-bottom:1px solid var(--border);
}
.monitor-dots{display:flex;gap:6px}
.monitor-dot2{width:8px;height:8px;border-radius:50%}
.monitor-dot2.r{background:#f87171}
.monitor-dot2.y{background:#fbbf24}
.monitor-dot2.g{background:#34d399}
.monitor-title{font-size:11px;color:var(--text2)}
.monitor-body{
  padding:16px;font-family:'SF Mono','Fira Code','Consolas',monospace;
  font-size:11px;line-height:1.8;max-height:200px;overflow-y:auto;
}
.monitor-line{white-space:pre-wrap}
.monitor-line .ts{color:var(--text3)}
.monitor-line .ml-info{color:var(--accent)}
.monitor-line .ml-ok{color:#34d399}
.monitor-line .ml-warn{color:var(--pink)}
.monitor-line .ml-err{color:#f87171}

/* Results */
.results-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.result-card{
  background:rgba(45,15,15,0.4);border:1px solid var(--border);
  border-radius:var(--radius-sm);padding:16px;transition:var(--transition);
}
.result-card:hover{background:var(--bg-card);border-color:var(--border-hover)}
.result-card .rc-top{display:flex;justify-content:space-between;align-items:start;margin-bottom:8px}
.result-card .rc-title{font-size:13px;font-weight:600}
.result-card .rc-sev{
  padding:2px 10px;border-radius:6px;font-size:10px;font-weight:600;
  text-transform:uppercase;letter-spacing:0.3px;
}
.result-card .rc-sev.critical{background:rgba(248,113,113,0.12);color:#f87171}
.result-card .rc-sev.high{background:rgba(251,146,60,0.12);color:#fb923c}
.result-card .rc-sev.medium{background:rgba(251,191,36,0.12);color:#fbbf24}
.result-card .rc-sev.low{background:rgba(52,211,153,0.12);color:#34d399}
.result-card .rc-details{font-size:11px;color:var(--text2)}

/* File IO & Console panels */
.panel-input-group{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.panel-input{flex:1;padding:10px 14px;border-radius:10px;background:rgba(255,255,255,0.03);border:1px solid var(--border);color:var(--text);font-size:12px;font-family:var(--font);outline:none;min-width:150px}
.panel-input:focus{border-color:var(--accent)}
.panel-select{padding:10px 14px;border-radius:10px;background:rgba(255,255,255,0.03);border:1px solid var(--border);color:var(--text);font-size:12px;font-family:var(--font);outline:none;cursor:pointer}
.panel-select option{background:#1a0808;color:var(--text)}
.panel-label{font-size:10px;color:var(--text3);margin-bottom:4px;display:block}
.panel-textarea{width:100%;padding:10px;border-radius:10px;background:rgba(255,255,255,0.03);border:1px solid var(--border);color:var(--text);font-size:11px;font-family:monospace;outline:none;resize:vertical;margin-bottom:8px}
.panel-textarea:focus{border-color:var(--accent)}
.panel-output{font-size:11px;color:var(--text2);background:rgba(0,0,0,0.2);border-radius:10px;padding:12px;font-family:monospace;max-height:150px;overflow-y:auto;margin-top:8px}

/* Console inline */
.console-row{display:flex;gap:0;margin-top:8px}
.console-prompt{color:var(--pink);font-family:monospace;font-size:13px;padding:0 8px;display:flex;align-items:center;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-right:none;border-radius:10px 0 0 10px}
.console-input{flex:1;padding:10px 14px;border-radius:0;font-size:12px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-right:none;color:var(--text);font-family:monospace;outline:none}
.console-input:focus{background:rgba(255,255,255,0.04)}
.console-btn{padding:10px 20px;border-radius:0 10px 10px 0;background:linear-gradient(135deg,var(--accent),var(--purple));color:#fff;border:none;cursor:pointer;font-size:11px;font-weight:600;font-family:var(--font)}

/* Filters & Layout utils */
.flex{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.flex-1{flex:1}
.mb-2{margin-bottom:8px}
.mt-2{margin-top:8px}
.w-full{width:100%}
.gap-4{gap:16px}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.fade-up{animation:fadeUp 0.4s ease both}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}

/* Scrollbar */
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--border-hover)}

/* Tab nav inside content */
.content-tabs{display:flex;gap:2px;margin-bottom:20px;background:rgba(0,0,0,0.15);border-radius:var(--radius-sm);padding:3px;width:fit-content}
.content-tab{padding:8px 18px;border-radius:10px;font-size:12px;font-weight:500;cursor:pointer;transition:var(--transition);color:var(--text2);border:none;background:transparent;font-family:var(--font)}
.content-tab:hover{color:var(--text)}
.content-tab.active{background:var(--bg-card);color:var(--text);box-shadow:0 2px 8px rgba(0,0,0,0.2)}
</style>
</head>
<body>

<div class="app">

<!-- Sidebar -->
<div class="sidebar">
  <div class="sidebar-logo">I<span>n</span></div>
  <div class="sidebar-nav">
    <button class="sidebar-btn active" onclick="switchMainTab('scan')" title="Scan">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('files')" title="Files">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('console')" title="Console">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('history')" title="History">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('privesc')" title="Privesc">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('oob')" title="OOB Exfil">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('report')" title="Report">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('cms')" title="CMS Fingerprint">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('so')" title="Second Order">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('ws')" title="WebSocket">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3"/></svg>
    </button>
    <button class="sidebar-btn" onclick="switchMainTab('plugins')" title="Plugins">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    </button>
  </div>
  <div class="sidebar-bottom">
    <button class="sidebar-btn" title="Settings">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
    </button>
  </div>
</div>

<!-- Top Bar -->
<div class="topbar">
  <div class="topbar-left">
    <input class="topbar-search" id="globalSearch" placeholder="Search targets, databases..." onkeydown="if(event.key==='Enter')searchGlobal(this.value)"/>
  </div>
  <div class="topbar-right">
    <button class="topbar-btn" onclick="loadHistory()" title="Notifications"><span class="dot"></span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
    </button>
    <div class="topbar-avatar" title="Kael / Krynn Team">K</div>
  </div>
</div>

<!-- Main Content -->
<div class="main">
  <div class="main-inner">

    <!-- Left Column -->
    <div class="main-left">

      <!-- Content tabs: Scan / Files / Console / History -->
      <div class="content-tabs">
        <button class="content-tab active" onclick="switchSubTab('scan','sub-scan')">SQL Injection</button>
        <button class="content-tab" onclick="switchSubTab('scan','sub-nosql')">NoSQL</button>
        <button class="content-tab" onclick="switchSubTab('scan','sub-graphql')">GraphQL</button>
      </div>

      <!-- Scan Section (visible by default) -->
      <div class="content-section active" id="sub-scan">

        <!-- Hero Card -->
        <div class="hero-card fade-up">
          <div class="hero-inner">
            <div class="hero-left">
              <div class="hero-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                Intelligence Platform v1.0
              </div>
              <h1 class="hero-title">Injecta Intelligence Platform</h1>
              <p class="hero-desc">Automated SQL injection discovery and exploitation with WAF bypass, file IO, NoSQL and GraphQL intelligence.</p>
              <div class="hero-actions">
                <button class="hero-btn hero-btn-primary" onclick="startScan()">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  New Scan
                </button>
                <button class="hero-btn hero-btn-secondary" onclick="switchMainTab('files')">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                  File Operations
                </button>
              </div>
              <div class="hero-tags">
                <span class="hero-tag">MySQL</span>
                <span class="hero-tag">PostgreSQL</span>
                <span class="hero-tag">MSSQL</span>
                <span class="hero-tag">Oracle</span>
                <span class="hero-tag">SQLite</span>
              </div>
            </div>
            <div class="hero-visual">
              <svg viewBox="0 0 180 180" fill="none">
                <defs>
                  <linearGradient id="hg1" x1="0" y1="0" x2="180" y2="180"><stop stop-color="#c41e3a"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
                  <linearGradient id="hg2" x1="0" y1="0" x2="100" y2="100"><stop stop-color="#ec4899"/><stop offset="1" stop-color="#c41e3a"/></linearGradient>
                </defs>
                <rect x="10" y="40" width="160" height="100" rx="16" stroke="url(#hg1)" stroke-width="2" fill="rgba(196,30,58,0.06)"/>
                <ellipse cx="60" cy="70" rx="20" ry="24" fill="rgba(196,30,58,0.12)" stroke="url(#hg2)" stroke-width="1.5"/>
                <ellipse cx="120" cy="70" rx="20" ry="24" fill="rgba(124,58,237,0.1)" stroke="url(#hg1)" stroke-width="1.5"/>
                <ellipse cx="90" cy="115" rx="30" ry="14" fill="rgba(236,72,153,0.08)" stroke="url(#hg2)" stroke-width="1"/>
                <circle cx="60" cy="70" r="4" fill="var(--accent)" opacity="0.6"/>
                <circle cx="120" cy="70" r="4" fill="var(--purple)" opacity="0.6"/>
                <path d="M30 95 L50 95 L55 85 L65 105 L75 90 L85 100 L95 85 L105 100 L115 90 L150 110" stroke="var(--pink)" stroke-width="1.5" fill="none" opacity="0.4" stroke-linecap="round"/>
                <line x1="40" y1="135" x2="140" y2="135" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <line x1="50" y1="140" x2="130" y2="140" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
                <line x1="60" y1="145" x2="120" y2="145" stroke="rgba(255,255,255,0.02)" stroke-width="1"/>
                <text x="90" y="28" text-anchor="middle" fill="var(--text2)" font-size="10" font-family="Inter,sans-serif" opacity="0.5">CYBER INTELLIGENCE</text>
              </svg>
            </div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card fade-up" style="animation-delay:0.05s">
            <div class="sc-glow red"></div>
            <div class="sc-header">
              <div class="sc-icon red"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
              <span class="sc-trend up">+0%</span>
            </div>
            <div class="sc-value" id="statScans">0</div>
            <div class="sc-label">Scans Completed</div>
          </div>
          <div class="stat-card fade-up" style="animation-delay:0.1s">
            <div class="sc-glow purple"></div>
            <div class="sc-header">
              <div class="sc-icon purple"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
              <span class="sc-trend steady">--</span>
            </div>
            <div class="sc-value" id="statVulns">0</div>
            <div class="sc-label">Vulnerabilities</div>
          </div>
          <div class="stat-card fade-up" style="animation-delay:0.15s">
            <div class="sc-glow pink"></div>
            <div class="sc-header">
              <div class="sc-icon pink"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg></div>
              <span class="sc-trend steady">--</span>
            </div>
            <div class="sc-value" id="statDbs">0</div>
            <div class="sc-label">Databases</div>
          </div>
        </div>

        <!-- Scan Workspace -->
        <div class="scan-workspace">
          <div class="workspace-card">
            <div class="workspace-card-title">Target URL</div>
            <div class="workspace-input-group">
              <input class="workspace-input" id="targetUrl" placeholder="https://target.com/page.php?id=1"/>
              <button class="workspace-btn" onclick="startScan()">Launch Scan</button>
            </div>
            <div class="flex">
              <span class="hero-tag" style="cursor:pointer" onclick="document.getElementById('targetUrl').value='https://testphp.vulnweb.com/artists.php?artist=1'">TestPHP</span>
              <span class="hero-tag" style="cursor:pointer" onclick="document.getElementById('targetUrl').value='http://localhost/dvwa/vulnerabilities/sqli/?id=1'">DVWA</span>
            </div>
          </div>
          <div class="workspace-card">
            <div class="workspace-card-title">Techniques</div>
            <div class="workspace-chips">
              <label class="workspace-chip active"><span class="dot on"></span>Boolean</label>
              <label class="workspace-chip active"><span class="dot on"></span>Error</label>
              <label class="workspace-chip active"><span class="dot on"></span>UNION</label>
              <label class="workspace-chip active"><span class="dot on"></span>Time</label>
              <label class="workspace-chip"><span class="dot off"></span>Stacked</label>
              <label class="workspace-chip"><span class="dot off"></span>NoSQL</label>
              <label class="workspace-chip"><span class="dot off"></span>GraphQL</label>
            </div>
            <div class="flex">
              <select class="panel-select" style="font-size:11px"><option>Risk: Low</option><option selected>Risk: Medium</option><option>Risk: High</option></select>
              <select class="panel-select" style="font-size:11px"><option>Threads: 1</option><option selected>Threads: 5</option><option>Threads: 10</option></select>
            </div>
          </div>
        </div>

        <!-- Monitor -->
        <div class="monitor-box">
          <div class="monitor-header">
            <div class="monitor-dots"><span class="monitor-dot2 r"></span><span class="monitor-dot2 y"></span><span class="monitor-dot2 g"></span></div>
            <span class="monitor-title">injecta@terminal <span id="termStatus" style="color:var(--text3)">(idle)</span></span>
            <span class="monitor-title" style="font-size:10px;cursor:pointer" onclick="copyMonitor()">Copy</span>
          </div>
          <div class="monitor-body" id="monBody">
            <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Injecta ready. Enter a target URL and launch scan.</span></div>
          </div>
        </div>

        <!-- Results -->
        <div class="workspace-card" id="resultsCard" style="display:none">
          <div class="workspace-card-title">Scan Results</div>
          <div id="resultsContainer"></div>
        </div>

      </div>

      <!-- NoSQL sub-tab -->
      <div class="content-section" id="sub-nosql">
        <div class="workspace-card">
          <div class="workspace-card-title">NoSQL Injection</div>
          <div class="panel-input-group">
            <input class="panel-input" id="nosqlUrl" placeholder="https://api.target.com/users" style="flex:1"/>
            <button class="workspace-btn" onclick="runNosql()">Scan NoSQL</button>
          </div>
          <div class="panel-label">Target URL for NoSQL endpoint (MongoDB, CouchDB)</div>
          <div class="monitor-box" style="margin-top:12px;margin-bottom:0">
            <div class="monitor-body" id="nosqlBody" style="max-height:120px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- GraphQL sub-tab -->
      <div class="content-section" id="sub-graphql">
        <div class="workspace-card">
          <div class="workspace-card-title">GraphQL Intelligence</div>
          <div class="panel-input-group">
            <input class="panel-input" id="graphqlUrl" placeholder="https://api.target.com/graphql" style="flex:1"/>
            <button class="workspace-btn" onclick="runGraphql()">Discover</button>
          </div>
          <div class="panel-label">GraphQL endpoint discovery, introspection and injection testing</div>
          <div class="monitor-box" style="margin-top:12px;margin-bottom:0">
            <div class="monitor-body" id="graphqlBody" style="max-height:120px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Files Section -->
      <div class="content-section" id="sub-files">
        <div class="workspace-card">
          <div class="workspace-card-title">Post-Exploitation</div>
          <div class="panel-input-group">
            <div style="flex:2;min-width:160px">
              <div class="panel-label">File Path / Command</div>
              <input class="panel-input" id="filePath" placeholder="/etc/passwd" style="width:100%"/>
            </div>
            <div style="flex:1;min-width:100px">
              <div class="panel-label">Action</div>
              <select class="panel-select" id="fileAction" style="width:100%">
                <option value="read">Read File</option>
                <option value="write">Write File</option>
                <option value="os">OS Command</option>
              </select>
            </div>
            <div style="display:flex;align-items:flex-end">
              <button class="workspace-btn" onclick="execFileOp()" style="border-radius:10px">Execute</button>
            </div>
          </div>
          <div id="fileContentWrap" style="display:none;margin-bottom:8px">
            <div class="panel-label">Content to write</div>
            <textarea class="panel-textarea" id="fileContent" rows="2" placeholder="Write content here"></textarea>
          </div>
          <div class="panel-output" id="fileOutput"><span class="ts">[--:--:--]</span> File operation output will appear here.</div>
        </div>
      </div>

      <!-- Console Section -->
      <div class="content-section" id="sub-console">
        <div class="workspace-card">
          <div class="workspace-card-title">Interactive Console</div>
          <div class="monitor-box" style="margin-bottom:12px">
            <div class="monitor-body" id="conBody" style="max-height:300px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Interactive console ready. Type any command below.</span></div>
            </div>
          </div>
          <div class="console-row">
            <span class="console-prompt">$</span>
            <input class="console-input" id="conInput" placeholder="whoami / SELECT @@version / /etc/passwd" onkeydown="if(event.key==='Enter')runConsole()"/>
            <button class="console-btn" onclick="runConsole()">Run</button>
          </div>
        </div>
      </div>

      <!-- History Section -->
      <div class="content-section" id="sub-history">
        <div class="workspace-card">
          <div class="workspace-card-title">Scan History</div>
          <div id="historyContainer"><div style="color:var(--text3);font-size:12px;text-align:center;padding:20px">No scan history yet.</div></div>
        </div>
      </div>

      <!-- Privesc Section -->
      <div class="content-section" id="sub-privesc">
        <div class="workspace-card">
          <div class="workspace-card-title">Privilege Escalation</div>
          <div class="panel-label">Detect current user privileges and attempt escalation on the target.</div>
          <div class="workspace-input-group" style="margin-top:12px">
            <input class="workspace-input" id="privescTarget" placeholder="Target URL (uses main target if empty)"/>
            <button class="workspace-btn" onclick="runPrivesc()">Enumerate & Escalate</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-header">
              <span class="monitor-title">Privilege Output</span>
            </div>
            <div class="monitor-body" id="privescBody" style="max-height:200px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Click enumerate to start.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- OOB Section -->
      <div class="content-section" id="sub-oob">
        <div class="workspace-card">
          <div class="workspace-card-title">Out-of-Band Exfiltration</div>
          <div class="panel-label">Exfiltrate data via DNS or HTTP channels to your listener.</div>
          <div class="panel-input-group" style="margin-top:8px">
            <input class="panel-input" id="oobTarget" placeholder="Target URL" style="flex:1.5"/>
            <input class="panel-input" id="oobHost" placeholder="Listener host (IP/domain)" style="flex:1"/>
          </div>
          <div class="flex" style="margin-bottom:8px">
            <select class="panel-select" id="oobChannel">
              <option value="dns">DNS</option>
              <option value="http">HTTP</option>
            </select>
            <button class="workspace-btn" onclick="runOob()" style="border-radius:10px">Exfiltrate</button>
          </div>
          <div class="monitor-box">
            <div class="monitor-body" id="oobBody" style="max-height:150px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">OOB module ready.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Section -->
      <div class="content-section" id="sub-report">
        <div class="workspace-card">
          <div class="workspace-card-title">Report Generation</div>
          <div class="panel-label">Generate comprehensive HTML and JSON reports of scan findings.</div>
          <div class="workspace-input-group" style="margin-top:12px">
            <input class="workspace-input" id="reportTarget" placeholder="Target URL (uses main target if empty)"/>
            <button class="workspace-btn" onclick="runReport()">Generate Report</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-body" id="reportBody" style="max-height:150px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready to generate report.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- CMS Fingerprinting -->
      <div class="content-section" id="sub-cms">
        <div class="workspace-card">
          <div class="workspace-card-title">CMS Fingerprinting & Exploitation</div>
          <div class="panel-label">Detect CMS (WordPress, Joomla, Drupal, Magento) version and known exploits.</div>
          <div class="workspace-input-group" style="margin-top:12px">
            <input class="workspace-input" id="cmsTarget" placeholder="Target URL (uses main target if empty)"/>
            <button class="workspace-btn" onclick="runCms()">Fingerprint CMS</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-body" id="cmsBody" style="max-height:200px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready to scan.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Second-Order Injection -->
      <div class="content-section" id="sub-so">
        <div class="workspace-card">
          <div class="workspace-card-title">Second-Order Injection</div>
          <div class="panel-label">Detect stored SQL injection via forms, comments, registration, etc.</div>
          <div class="workspace-input-group" style="margin-top:12px">
            <input class="workspace-input" id="soTarget" placeholder="Target URL (uses main target if empty)"/>
            <button class="workspace-btn" onclick="runSecondOrder()">Scan</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-body" id="soBody" style="max-height:200px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- WebSocket Scanner -->
      <div class="content-section" id="sub-ws">
        <div class="workspace-card">
          <div class="workspace-card-title">WebSocket Security Scanner</div>
          <div class="panel-label">Discover WebSocket endpoints and test for injection vulnerabilities.</div>
          <div class="workspace-input-group" style="margin-top:12px">
            <input class="workspace-input" id="wsTarget" placeholder="Target URL (uses main target if empty)"/>
            <button class="workspace-btn" onclick="runWebSocket()">Scan WebSockets</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-body" id="wsBody" style="max-height:200px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Ready.</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Plugins -->
      <div class="content-section" id="sub-plugins">
        <div class="workspace-card">
          <div class="workspace-card-title">Custom Payload Plugins</div>
          <div class="panel-label">Load and manage custom plugins from the plugins/ directory.</div>
          <div class="flex" style="margin-top:12px">
            <button class="workspace-btn" onclick="runPlugins()" style="border-radius:10px">Discover & Load Plugins</button>
          </div>
          <div class="monitor-box" style="margin-top:12px">
            <div class="monitor-body" id="pluginsBody" style="max-height:200px">
              <div class="monitor-line"><span class="ts">[--:--:--]</span> <span class="ml-info">Plugin system ready.</span></div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Right Column -->
    <div class="main-right">

      <!-- Circular Progress -->
      <div class="right-card">
        <svg width="0" height="0"><defs><linearGradient id="circGrad" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#c41e3a"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs></svg>
        <div class="right-card-header">
          <span class="right-card-title">Scan Performance</span>
          <span class="right-card-action" onclick="resetMetrics()">Reset</span>
        </div>
        <div class="circular-progress">
          <svg viewBox="0 0 150 150">
            <circle class="bg" cx="75" cy="75" r="70"/>
            <circle class="fg" id="progressCircle" cx="75" cy="75" r="70"/>
          </svg>
          <div class="center">
            <div class="val" id="progressVal">0%</div>
            <div class="lbl">Success Rate</div>
          </div>
        </div>
        <div class="metrics-list">
          <div class="metric-item"><span class="mi-label">Vulnerabilities</span><div class="mi-bar"><div class="fill" style="width:0%" id="barVulns"></div></div><span class="mi-value" id="mValVulns">0</span></div>
          <div class="metric-item"><span class="mi-label">Databases</span><div class="mi-bar"><div class="fill" style="width:0%" id="barDbs"></div></div><span class="mi-value" id="mValDbs">0</span></div>
          <div class="metric-item"><span class="mi-label">Tables</span><div class="mi-bar"><div class="fill" style="width:0%" id="barTables"></div></div><span class="mi-value" id="mValTables">0</span></div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="right-card">
        <div class="right-card-header">
          <span class="right-card-title">Recent Activity</span>
          <span class="right-card-action" onclick="clearActivity()">Clear</span>
        </div>
        <div class="activity-list" id="activityList">
          <div class="activity-item">
            <span class="activity-dot info"></span>
            <div class="activity-content">
              <div class="activity-text">System initialized</div>
              <div class="activity-time">Just now</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Targets -->
      <div class="right-card">
        <div class="right-card-header">
          <span class="right-card-title">Targets</span>
          <span class="right-card-action">+ Add</span>
        </div>
        <div id="targetsList">
          <div style="color:var(--text3);font-size:11px;text-align:center;padding:12px 0">No targets configured. Launch a scan to begin.</div>
        </div>
      </div>

    </div>
  </div>
</div>

</div>

<svg width="0" height="0"><defs><linearGradient id="circGrad" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#c41e3a"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs></svg>

<script>
// Global state
var scanInterval = null;
var logInterval = null;
var lastLogIndex = 0;
var scanLogs = [];
var scanResults = {};
var activityItems = [];
var chartsInitialized = false;

// Utilities
function $(id){return document.getElementById(id)}

function log(msg, level){
  level=level||'info';var b=$('monBody');if(!b)return;
  var d=document.createElement('div');d.className='monitor-line';
  var t=new Date().toLocaleTimeString('en-US',{hour12:false});
  d.innerHTML='<span class="ts">['+t+']</span> <span class="ml-'+level+'">'+msg+'</span>';
  b.appendChild(d);b.scrollTop=b.scrollHeight;
  scanLogs.push({ts:t,msg:msg,level:level});
}

function addActivity(msg, type){
  type=type||'info';var al=$('activityList');
  if(!al)return;
  var d=document.createElement('div');d.className='activity-item';
  d.style.animation='fadeUp 0.3s ease';
  var t=new Date().toLocaleTimeString('en-US',{hour12:false});
  d.innerHTML='<span class="activity-dot '+type+'"></span><div class="activity-content"><div class="activity-text">'+msg+'</div><div class="activity-time">'+t+'</div></div>';
  al.insertBefore(d, al.firstChild);
  while(al.children.length>8)al.removeChild(al.lastChild);
}

function updateProgress(val){
  var circle=$('progressCircle');if(!circle)return;
  var dash=440-(440*val/100);
  circle.style.strokeDashoffset=dash;
  $('progressVal').textContent=Math.round(val)+'%';
}

function updateMetrics(data){
  if(!data)return;
  var v=data.params?data.params.length:0;
  var db=data.dbms?1:0;
  $('statScans').textContent=data.target?1:0;
  $('statVulns').textContent=v;
  $('statDbs').textContent=db;
  $('mValVulns').textContent=v;
  $('mValDbs').textContent=db;
  if(v>0){$('barVulns').style.width=Math.min(v*20,100)+'%'}
  if(db>0){$('barDbs').style.width=Math.min(db*50,100)+'%'}
  updateProgress(data.vulnerable?85:(data.target?30:0));
}

function resetMetrics(){
  $('progressCircle').style.strokeDashoffset=440;
  $('progressVal').textContent='0%';
  ['barVulns','barDbs','barTables'].forEach(function(id){$(id).style.width='0%'});
  ['mValVulns','mValDbs','mValTables'].forEach(function(id){$(id).textContent='0'});
}

function clearActivity(){
  $('activityList').innerHTML='<div class="activity-item"><span class="activity-dot info"></span><div class="activity-content"><div class="activity-text">Activity cleared</div><div class="activity-time">Just now</div></div></div>';
}

// Tab switching
function switchMainTab(tab){
  document.querySelectorAll('.sidebar-btn').forEach(function(b){b.classList.remove('active')});
  document.querySelectorAll('.content-section').forEach(function(s){s.classList.remove('active')});
  var subs={'scan':'sub-scan','files':'sub-files','console':'sub-console','history':'sub-history','nosql':'sub-nosql','graphql':'sub-graphql','privesc':'sub-privesc','oob':'sub-oob','report':'sub-report','cms':'sub-cms','so':'sub-so','ws':'sub-ws','plugins':'sub-plugins'};
  var target=subs[tab]||'sub-scan';
  var el=$(target);if(el)el.classList.add('active');
  var btn=document.querySelector('.sidebar-btn[onclick*="'+tab+'"]');
  if(btn)btn.classList.add('active');
  // Sync content tabs
  if(tab==='scan'){
    document.querySelectorAll('.content-tab').forEach(function(t,i){
      var maps={0:'sub-scan',1:'sub-nosql',2:'sub-graphql'};
      t.classList.toggle('active',i===0);
      var sec=$(maps[i]);if(sec)sec.style.display=i===0?'block':'none';
    });
  }
}

function switchSubTab(main, sub){
  // For sub-tabs within scan (SQLI, NoSQL, GraphQL)
  if(main==='scan'){
    document.querySelectorAll('.content-tab').forEach(function(t){t.classList.remove('active')});
    document.querySelectorAll('#sub-scan,#sub-nosql,#sub-graphql').forEach(function(s){s.classList.remove('active');s.style.display='none'});
    var idx={'sub-scan':0,'sub-nosql':1,'sub-graphql':2};
    var tabs=document.querySelectorAll('.content-tab');
    if(tabs[idx[sub]])tabs[idx[sub]].classList.add('active');
    var sec=$(sub);if(sec){sec.classList.add('active');sec.style.display='block'}
  }
}

document.querySelectorAll('.content-tab').forEach(function(t,i){
  t.addEventListener('click',function(){
    var maps={0:'sub-scan',1:'sub-nosql',2:'sub-graphql'};
    switchSubTab('scan',maps[i]);
  });
});

document.querySelectorAll('.workspace-chip').forEach(function(c){
  c.addEventListener('click',function(){
    this.classList.toggle('active');
    var d=this.querySelector('.dot');
    d.className='dot '+(this.classList.contains('active')?'on':'off');
  });
});

// Scan
async function startScan(){
  var u=$('targetUrl').value.trim();
  if(!u){log('Enter a target URL','err');return}
  log('Initiating scan: '+u,'info');
  addActivity('Scan started: '+u,'info');
  document.getElementById('termStatus').textContent='(scanning)';
  resetMetrics();lastLogIndex=0;
  if(logInterval)clearInterval(logInterval);
  logInterval=setInterval(pollLogs,800);
  try{
    var r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var d=await r.json();log('Scan ID: '+d.scan_id,'ok');
  }catch(e){log('Error: '+e.message,'err');document.getElementById('termStatus').textContent='(error)';return}
  if(scanInterval)clearInterval(scanInterval);
  scanInterval=setInterval(pollResults,2000);
}

async function pollResults(){
  try{
    var r=await(await fetch('/api/status')).json();
    if(r.status==='complete'){
      clearInterval(scanInterval);scanInterval=null;
      clearInterval(logInterval);logInterval=null;
      document.getElementById('termStatus').textContent='(complete)';
      log('Scan completed.','ok');
      addActivity('Scan completed','ok');
      scanResults=r.results||{};
      if(scanResults.vulnerable){
        updateMetrics(scanResults);
        $('resultsCard').style.display='block';
        var rc=$('resultsContainer');
        if(rc){
          var h='<div class="results-grid">';
          scanResults.params.forEach(function(p,i){
            var sev=p.confidence>=0.9?'critical':p.confidence>=0.7?'high':'medium';
            h+='<div class="result-card fade-up" style="animation-delay:'+(i*0.1)+'s"><div class="rc-top"><div class="rc-title">Injection #'+(i+1)+'</div><span class="rc-sev '+sev+'">'+sev+'</span></div>';
            h+='<div class="rc-details">Param: <strong style="color:var(--text)">'+p.param+'</strong> &middot; '+p.technique+' &middot; '+(p.confidence*100).toFixed(0)+'%';
            if(scanResults.dbms)h+=' &middot; <span style="color:var(--accent)">'+scanResults.dbms+'</span>';
            h+='</div></div>';
          });
          h+='</div>';
          rc.innerHTML=h;
        }
        log('DBMS: '+scanResults.dbms,'ok');
        addActivity('SQL injection found - '+scanResults.dbms,'ok');
      }else{
        $('resultsCard').style.display='block';
        $('resultsContainer').innerHTML='<div style="color:var(--text3);text-align:center;padding:12px;font-size:12px">Not vulnerable with current configuration.</div>';
      }
      updateTargetsList();
    }else if(r.status==='error'){
      clearInterval(scanInterval);scanInterval=null;
      clearInterval(logInterval);logInterval=null;
      document.getElementById('termStatus').textContent='(error)';
      log('Error: '+(r.results?.error||'unknown'),'err');
    }
  }catch(e){}
}

async function pollLogs(){
  try{
    var r=await(await fetch('/api/logs?since='+lastLogIndex)).json();
    if(r.logs&&r.logs.length){
      var b=$('monBody');if(!b)return;
      r.logs.forEach(function(l){
        var d=document.createElement('div');d.className='monitor-line';
        var level='info';
        if(l.includes('[+]'))level='ok';
        else if(l.includes('[!]'))level='warn';
        else if(l.includes('[-]'))level='err';
        d.innerHTML='<span class="ts"></span> <span class="ml-'+level+'">'+l.replace(/[[]\d+m/g,'')+'</span>';
        b.appendChild(d);
      });
      b.scrollTop=b.scrollHeight;
    }
    lastLogIndex=r.total||lastLogIndex;
  }catch(e){}
}

// File IO
$('fileAction').addEventListener('change',function(){
  $('fileContentWrap').style.display=this.value==='write'?'block':'none';
});

async function execFileOp(){
  var t=$('targetUrl').value.trim();
  if(!t){log('Set a target URL first','err');return}
  var p=$('filePath').value.trim();
  if(!p){log('Enter a file path','err');return}
  var a=$('fileAction').value;
  var ep,b;
  if(a==='read'){ep='/api/file-read';b={target:t,path:p}}
  else if(a==='write'){var c=$('fileContent').value||'test';ep='/api/file-write';b={target:t,path:p,content:c}}
  else{var c=$('fileContent').value.trim()||p;ep='/api/os-cmd';b={target:t,cmd:c}}
  $('fileOutput').innerHTML='Running...';log(a+' '+p,'info');
  addActivity('File '+a+': '+p,'warn');
  try{
    await fetch(ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.output||s.results?.file_content||(s.results?.results?s.results.results.join('\\n'):'')||'(empty)';
          $('fileOutput').innerHTML=r.replace(/</g,'&lt;');log(a+' complete','ok');
        }else if(s.status==='error'){clearInterval(po);$('fileOutput').innerHTML='Error: '+(s.results?.error||'')}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){log('Error: '+e.message,'err')}
}

// Console
async function runConsole(){
  var i=$('conInput'),c=i.value.trim();if(!c)return;i.value='';
  var t=$('targetUrl').value.trim();
  if(!t){log('Set a target URL','err');return}
  var cb=$('conBody');
  var d=document.createElement('div');d.className='monitor-line';
  d.innerHTML='<span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">$ '+c.replace(/</g,'&lt;')+'</span>';
  cb.appendChild(d);cb.scrollTop=cb.scrollHeight;
  try{
    await fetch('/api/os-cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:t,cmd:c})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          (s.results?.output||s.results?.file_content||(s.results?.results?s.results.results.join('\\n'):'')||'(no output)').split('\\n').forEach(function(l){
            var e=document.createElement('div');e.className='monitor-line';
            e.innerHTML='<span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">'+(l||' ').replace(/</g,'&lt;')+'</span>';
            cb.appendChild(e);cb.scrollTop=cb.scrollHeight;
          });
        }else if(s.status==='error'){clearInterval(po)}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// NoSQL
async function runNosql(){
  var u=$('nosqlUrl').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Enter a URL','err');return}
  var nb=$('nosqlBody');
  nb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Scanning NoSQL: '+u+'</span></div>';
  try{
    await fetch('/api/nosql',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.nosql||{};
          nb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Detected: '+r.detected+' | DB: '+(r.db_type||'none')+' | Vulnerable: '+r.vulnerable+'</span></div>';
          if(r.vulnerable)addActivity('NoSQL injection confirmed','warn');
        }else if(s.status==='error'){clearInterval(po);nb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// GraphQL
async function runGraphql(){
  var u=$('graphqlUrl').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Enter a URL','err');return}
  var gb=$('graphqlBody');
  gb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Discovering GraphQL: '+u+'</span></div>';
  try{
    await fetch('/api/graphql',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.graphql||{};
          var endpoints=r.endpoints?r.endpoints.join(', '):'none';
          var schema=r.schema_extracted?'Schema extracted':'No schema';
          gb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Found: '+r.found+' | Endpoints: '+endpoints+' | '+schema+'</span></div>';
          if(r.injection?.vulnerable)addActivity('GraphQL injection found','warn');
        }else if(s.status==='error'){clearInterval(po);gb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// History
async function loadHistory(){
  try{
    var r=await(await fetch('/api/history')).json();
    if(r.history&&r.history.length>0){
      var hc=$('historyContainer');
      if(hc){
        hc.innerHTML='<table style="width:100%;border-collapse:collapse;font-size:12px"><thead><tr style="color:var(--text3);text-align:left;font-size:11px"><th style="padding:8px">Time</th><th style="padding:8px">Target</th><th style="padding:8px">Status</th></tr></thead><tbody>'+
          r.history.slice().reverse().map(function(h){
            var c=h.status==='complete'?'var(--green)':h.status==='error'?'var(--red)':'var(--text2)';
            return '<tr style="border-top:1px solid rgba(255,255,255,0.03)"><td style="padding:8px;color:var(--text3)">'+h.timestamp+'</td><td style="padding:8px">'+h.target+'</td><td style="padding:8px;color:'+c+'">'+h.status+'</td></tr>';
          }).join('')+'</tbody></table>';
      }
    }
  }catch(e){}
}

// Targets list
function updateTargetsList(){
  var tl=$('targetsList');if(!tl)return;
  var u=$('targetUrl').value.trim();
  if(!u){tl.innerHTML='<div style="color:var(--text3);font-size:11px;text-align:center;padding:12px 0">No targets.</div>';return}
  var vuln=scanResults.vulnerable?'<span style="color:var(--green)">Vulnerable</span>':'<span style="color:var(--text3)">Scanned</span>';
  tl.innerHTML='<div class="target-item"><div class="target-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-9-9"/><path d="M12 2v10l6 6"/></svg></div><div class="target-info"><div class="target-name">'+u+'</div><div class="target-status">'+vuln+'</div></div><div class="target-progress"><div class="fill" style="width:'+(scanResults.vulnerable?85:30)+'%"></div></div></div>';
}

function copyMonitor(){
  var t=Array.from($('monBody').querySelectorAll('.monitor-line')).map(function(l){return l.textContent}).join('\\n');
  navigator.clipboard.writeText(t).then(function(){log('Terminal output copied.','ok')}).catch(function(){});
}

function searchGlobal(val){
  if(!val)return;
  var u=$('targetUrl');
  if(u)u.value=val;
  switchMainTab('scan');
}

// Privesc
async function runPrivesc(){
  var u=$('privescTarget').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Set a target URL','err');return}
  var pb=$('privescBody');
  pb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Enumerating privileges on '+u+'...</span></div>';
  addActivity('Privesc: '+u,'info');
  try{
    await fetch('/api/privesc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.privesc||{};
          var h='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">User: '+(r.user||'?')+' | Admin: '+(r.is_admin?'YES':'NO')+' | Privileges: '+(r.privileges?r.privileges.join(', '):'none')+'</span></div>';
          if(r.escalation?.success)h+='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-warn">Escalated via: '+r.escalation.technique+'</span></div>';
          if(r.escalation_paths&&r.escalation_paths.length)r.escalation_paths.forEach(function(p){
            h+='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">  -> '+p+'</span></div>';
          });
          pb.innerHTML=h;
          if(r.is_admin)addActivity('Admin access confirmed on '+u,'ok');
        }else if(s.status==='error'){clearInterval(po);pb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// OOB
async function runOob(){
  var u=$('oobTarget').value.trim()||$('targetUrl').value.trim();
  var h=$('oobHost').value.trim();
  if(!u){log('Set a target URL','err');return}
  if(!h){log('Enter a listener host','err');return}
  var ch=$('oobChannel').value;
  var ob=$('oobBody');
  ob.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">OOB '+ch.toUpperCase()+' to '+h+'...</span></div>';
  addActivity('OOB '+ch.toUpperCase()+': '+h,'warn');
  try{
    await fetch('/api/oob',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u,host:h,channel:ch})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.oob||{};
          ob.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Channel: '+(r.success?'ESTABLISHED':'FAILED')+' | Technique: '+(r.technique||'none')+'</span></div>';
          if(r.success)addActivity('OOB '+ch.toUpperCase()+' channel to '+h,'ok');
        }else if(s.status==='error'){clearInterval(po);ob.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// Report
async function runReport(){
  var u=$('reportTarget').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Set a target URL','err');return}
  var rb=$('reportBody');
  rb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Generating report for '+u+'...</span></div>';
  addActivity('Report generation: '+u,'info');
  try{
    await fetch('/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.report||{};
          var paths='',count=0;
          if(r.json){paths+='JSON: '+r.json;count++}
          if(r.html){paths+=(paths?' | ':'')+'HTML: '+r.html;count++}
          rb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">'+count+' report(s) generated:</span></div>'+
            '<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">'+paths+'</span></div>';
          addActivity('Reports generated for '+u,'ok');
        }else if(s.status==='error'){clearInterval(po);rb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// Init
async function runCms(){
  var u=$('cmsTarget').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Set a target URL','err');return}
  var cb=$('cmsBody');
  cb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Fingerprinting CMS on '+u+'...</span></div>';
  addActivity('CMS scan: '+u,'info');
  try{
    await fetch('/api/cms',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.cms||{};
          var h='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">CMS: '+(r.cms||'none')+' | Version: '+(r.version||'?')+' | Confidence: '+Math.round((r.confidence||0)*100)+'%</span></div>';
          if(r.exploits&&r.exploits.length)r.exploits.forEach(function(e){h+='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-warn">  -> '+e+'</span></div>'});
          cb.innerHTML=h;
          if(r.cms)addActivity('CMS detected: '+r.cms,'ok');
        }else if(s.status==='error'){clearInterval(po);cb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

async function runSecondOrder(){
  var u=$('soTarget').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Set a target URL','err');return}
  var sb=$('soBody');
  sb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Scanning second-order on '+u+'...</span></div>';
  addActivity('Second-order scan: '+u,'info');
  try{
    await fetch('/api/second-order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.second_order||{};
          sb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Detected: '+(r.detected||false)+' | Vulnerable: '+(r.vulnerable||false)+' | Vectors: '+(r.vectors?r.vectors.length:0)+'</span></div>';
          if(r.vulnerable)addActivity('Second-order injection found','warn');
        }else if(s.status==='error'){clearInterval(po);sb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

async function runWebSocket(){
  var u=$('wsTarget').value.trim()||$('targetUrl').value.trim();
  if(!u){log('Set a target URL','err');return}
  var wb=$('wsBody');
  wb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Scanning WebSockets on '+u+'...</span></div>';
  addActivity('WebSocket scan: '+u,'info');
  try{
    await fetch('/api/websocket',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:u})});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.websocket||{};
          var h='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Found: '+r.found+' | Endpoints: '+(r.endpoints?r.endpoints.length:0)+' | Vulnerable: '+r.vulnerable+'</span></div>';
          if(r.endpoints)r.endpoints.forEach(function(ep){h+='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">  '+ep+'</span></div>'});
          wb.innerHTML=h;
          if(r.found)addActivity('WebSocket endpoints found','info');
        }else if(s.status==='error'){clearInterval(po);wb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

async function runPlugins(){
  var pb=$('pluginsBody');
  pb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">Loading plugins...</span></div>';
  try{
    await fetch('/api/plugins',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    var po=setInterval(async function(){
      try{
        var s=await(await fetch('/api/status')).json();
        if(s.status==='complete'){
          clearInterval(po);
          var r=s.results?.plugins||{};
          var h='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-ok">Discovered: '+(r.discovered?r.discovered.length:0)+' | Loaded: '+(r.count||0)+'</span></div>';
          if(r.loaded&&r.loaded.length)r.loaded.forEach(function(n){h+='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-info">  Plugin: '+n+'</span></div>'});
          pb.innerHTML=h;
          if(r.count>0)addActivity(r.count+' plugin(s) loaded','ok');
        }else if(s.status==='error'){clearInterval(po);pb.innerHTML='<div class="monitor-line"><span class="ts">['+new Date().toLocaleTimeString('en-US',{hour12:false})+']</span> <span class="ml-err">'+(s.results?.error||'error')+'</span></div>'}
      }catch(ex){clearInterval(po)}
    },1000);
  }catch(e){}
}

// Init
loadHistory();
addActivity('Injecta platform initialized','info');
log('Injecta Intelligence Platform v1.0 loaded.','info');
</script>
</body>
</html>"""

# Write the new HTML with repr() for safe string embedding
full = python_code
full += "\n\nDASHBOARD_HTML = " + repr(html) + "\n\n"
full += '''
def start_web_server(config, logger):
    from http.server import HTTPServer
    handler = VoidAPIHandler
    handler.config_ref = config
    handler.logger_ref = logger
    handler.scan_status = "idle"
    server = HTTPServer(("0.0.0.0", config.web_port), handler)
    logger.info(f"Web dashboard: http://localhost:{config.web_port}")
    logger.info("API endpoints:")
    logger.info("  GET  /api/status    - scan status")
    logger.info("  POST /api/scan      - launch scan")
    logger.info("  POST /api/file-read  - read file")
    logger.info("  POST /api/file-write - write file")
    logger.info("  POST /api/os-cmd     - exec cmd")
    logger.info("  POST /api/nosql      - NoSQL scan")
    logger.info("  POST /api/graphql    - GraphQL scan")
    logger.info("  GET  /api/history    - scan history")
    logger.info("  GET  /api/logs       - live log stream")
    logger.info("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Web server stopped.")
        server.server_close()
'''

with open(DST, "w", encoding="utf-8") as f:
    f.write(full)

print(f"Written to {DST}")
print(f"Size: {os.path.getsize(DST)} bytes")
print(f"HTML len: {len(html)} chars")
