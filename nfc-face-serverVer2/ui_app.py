from flask import Flask, render_template_string, request, jsonify
import requests as req

app = Flask(__name__)
API = "http://localhost:5001"
def proxy(method, path, **kw):
    try:
        r = getattr(req, method)(f"{API}{path}", timeout=30, **kw)
        return r.json(), r.status_code
    except req.exceptions.ConnectionError:
        return {"error": "face_server.py not reachable — is it running?"}, 503
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/scan")
def get_scan():
    d, c = proxy("get", "/current-scan")
    return jsonify(d), c

@app.route("/api/scan", methods=["DELETE"])
def clear_scan():
    d, c = proxy("delete", "/current-scan")
    return jsonify(d), c

@app.route("/api/user/<uid>")
def get_user(uid):
    d, c = proxy("get", f"/user/{uid}")
    return jsonify(d), c

@app.route("/api/user", methods=["POST"])
def create_user():
    d, c = proxy("post", "/user", json=request.get_json())
    return jsonify(d), c

@app.route("/api/user/<uid>", methods=["DELETE"])
def delete_user(uid):
    d, c = proxy("delete", f"/user/{uid}")
    return jsonify(d), c

@app.route("/api/user/<uid>/face", methods=["DELETE"])
def delete_face(uid):
    d, c = proxy("delete", f"/delete-face/{uid}")
    return jsonify(d), c
@app.route("/api/user/<uid>/profile", methods=["PATCH"])
def update_profile(uid):
    d, c = proxy("patch", f"/user/{uid}/profile", json=request.get_json())
    return jsonify(d), c

@app.route("/api/users")
def get_users():
    d, c = proxy("get", "/users")
    return jsonify(d), c

@app.route("/api/equipment")
def get_equipment():
    d, c = proxy("get", "/equipment")
    return jsonify(d), c

@app.route("/api/equipment/<tag>")
def get_equipment_item(tag):
    d, c = proxy("get", f"/equipment/{tag}")
    return jsonify(d), c

@app.route("/api/equipment", methods=["POST"])
def add_equipment():
    d, c = proxy("post", "/equipment", json=request.get_json())
    return jsonify(d), c

@app.route("/api/equipment/<tag>", methods=["DELETE"])
def del_equipment(tag):
    d, c = proxy("delete", f"/equipment/{tag}")
    return jsonify(d), c
@app.route("/api/checkout/<tag>", methods=["POST"])
def checkout(tag):
    d, c = proxy("patch", f"/equipment/{tag}/checkout", json=request.get_json())
    return jsonify(d), c

@app.route("/api/return/<tag>", methods=["POST"])
def ret(tag):
    d, c = proxy("patch", f"/equipment/{tag}/return", json=request.get_json())
    return jsonify(d), c

@app.route("/api/admin-return/<tag>", methods=["POST"])
def admin_ret(tag):
    d, c = proxy("patch", f"/equipment/{tag}/admin-return", json=request.get_json())
    return jsonify(d), c
@app.route("/api/verify-face", methods=["POST"])
def verify_face():
    d, c = proxy("post", "/verify-face", json=request.get_json())
    return jsonify(d), c

@app.route("/api/register-face", methods=["POST"])
def register_face():
    d, c = proxy("post", "/register-face", json=request.get_json())
    return jsonify(d), c

@app.route("/api/history")
def history():
    d, c = proxy("get", "/history")
    return jsonify(d), c

@app.route("/api/history/user/<uid>")
def user_history(uid):
    d, c = proxy("get", f"/history/user/{uid}")
    return jsonify(d), c

@app.route("/api/stats/summary")
def stats():
    d, c = proxy("get", "/stats/summary")
    return jsonify(d), c

@app.route("/api/hot-items")
def hot_items():
    d, c = proxy("get", "/stats/hot-items")
    return jsonify(d), c

@app.route("/api/email/reminder", methods=["POST"])
def reminder():
    d, c = proxy("post", "/email/reminder", json=request.get_json())
    return jsonify(d), c

@app.route("/api/email/manual", methods=["POST"])
def manual_email():
    d, c = proxy("post", "/email/manual", json=request.get_json())
    return jsonify(d), c


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NFC Lend</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--surface:#1a1d24;--card:#22252f;--border:#2e3240;
  --text:#e8eaf0;--muted:#7a8094;--accent:#4d90f0;--green:#34c77b;
  --red:#ef4565;--amber:#f5a623;--purple:#9b6dff;
  --r:10px;--font:system-ui,-apple-system,sans-serif
}
body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh}
input,select,textarea{width:100%;background:var(--surface);border:1px solid var(--border);
  border-radius:8px;padding:10px 13px;color:var(--text);font-family:var(--font);
  font-size:14px;outline:none;transition:border-color .15s}
input[type=password]{letter-spacing:3px}
input:focus,textarea:focus,select:focus{border-color:var(--accent)}
select option{background:var(--surface)}
textarea{resize:vertical;min-height:80px}
label{display:block;font-size:12px;color:var(--muted);margin-bottom:5px;
  font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.fg{margin-bottom:14px}
.btn{display:inline-flex;align-items:center;justify-content:center;
  gap:6px;padding:11px 20px;border-radius:8px;font-family:var(--font);
  font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .15s}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{filter:brightness(1.1)}
.btn-danger{background:rgba(239,69,101,.12);color:var(--red);border:1px solid rgba(239,69,101,.3)}
.btn-danger:hover{background:rgba(239,69,101,.22)}
.btn-ghost{background:rgba(255,255,255,.05);color:var(--text);border:1px solid var(--border)}
.btn-ghost:hover{background:rgba(255,255,255,.09)}
.btn-green{background:rgba(52,199,123,.12);color:var(--green);border:1px solid rgba(52,199,123,.3)}
.btn-green:hover{background:rgba(52,199,123,.22)}
.btn-amber{background:rgba(245,166,35,.12);color:var(--amber);border:1px solid rgba(245,166,35,.3)}
.btn-amber:hover{background:rgba(245,166,35,.22)}
.btn-full{width:100%}
.btn-sm{padding:6px 12px;font-size:12px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:22px}
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:700}
.bg{background:rgba(52,199,123,.12);color:var(--green)}
.br{background:rgba(239,69,101,.12);color:var(--red)}
.ba{background:rgba(245,166,35,.12);color:var(--amber)}
.bb{background:rgba(77,144,240,.12);color:var(--accent)}
.bm{background:rgba(122,128,148,.12);color:var(--muted)}
.tw{overflow:auto;border-radius:var(--r);border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{background:var(--surface);color:var(--muted);font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.6px;padding:9px 13px;text-align:left;
  border-bottom:1px solid var(--border)}
tbody tr{border-bottom:1px solid var(--border)}
tbody tr:last-child{border-bottom:none}
tbody tr:hover{background:rgba(255,255,255,.02)}
td{padding:10px 13px;font-size:13px}
.mono{font-family:monospace;font-size:12px;color:var(--muted)}

.screen{display:none;min-height:100vh}
.screen.on{display:flex}
.center{flex-direction:column;align-items:center;justify-content:center;padding:32px 20px}
.box{width:100%;max-width:440px}
.logo{font-size:16px;font-weight:700;color:var(--muted);text-align:center;
  margin-bottom:36px;letter-spacing:1px}
.logo b{color:var(--accent)}
.title{font-size:26px;font-weight:700;text-align:center;margin-bottom:8px}
.sub{font-size:14px;color:var(--muted);text-align:center;margin-bottom:28px}

.pulse{animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.spin{width:42px;height:42px;border:3px solid var(--border);
  border-top-color:var(--accent);border-radius:50%;
  animation:spin 1s linear infinite;margin:0 auto 20px}
@keyframes spin{to{transform:rotate(360deg)}}
.icon-big{font-size:64px;text-align:center;margin-bottom:20px}
.chip{display:flex;align-items:center;gap:12px;
  background:rgba(77,144,240,.1);border:1px solid rgba(77,144,240,.2);
  border-radius:10px;padding:12px 16px;margin-bottom:22px}
.avatar{width:40px;height:40px;background:var(--accent);border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:17px;flex-shrink:0;color:#fff}
.chip-name{font-weight:700;font-size:15px}
.chip-sub{font-size:12px;color:var(--muted)}

.menu-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px}
.menu-btn{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:18px;text-align:center;cursor:pointer;transition:all .15s;font-family:var(--font)}
.menu-btn:hover{border-color:var(--accent);background:rgba(77,144,240,.05)}
.menu-icon{font-size:26px;margin-bottom:6px}
.menu-label{font-size:13px;font-weight:700;color:var(--text);display:block}
.menu-sub{font-size:11px;color:var(--muted);margin-top:2px}

.eq-item{background:var(--surface);border:1px solid var(--border);border-radius:9px;
  padding:13px 15px;display:flex;align-items:center;justify-content:space-between;
  margin-bottom:8px;cursor:pointer;transition:all .15s}
.eq-item:hover{border-color:var(--accent)}
.eq-item.rented{opacity:.5;cursor:not-allowed}
.eq-item.rented:hover{border-color:var(--border)}
.eq-name{font-weight:700;font-size:14px}
.eq-cat{font-size:12px;color:var(--muted);margin-top:2px}

.rating-row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.rn{width:44px;height:44px;background:var(--surface);border:2px solid var(--border);
  border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;
  transition:all .15s;display:flex;align-items:center;justify-content:center;color:var(--muted)}
.rn:hover{border-color:var(--accent);color:var(--text)}
.rn.sel{border-color:var(--amber);background:rgba(245,166,35,.12);color:var(--amber)}

.err-msg{color:var(--red);font-size:13px;margin-bottom:12px;display:none}
.ok-msg{color:var(--green);font-size:13px;margin-bottom:12px;display:none}

#admin-wrap{flex-direction:row}
#admin-nav{width:200px;min-height:100vh;background:var(--surface);
  border-right:1px solid var(--border);padding:22px 0;
  display:flex;flex-direction:column;flex-shrink:0}
#admin-body{flex:1;padding:26px;overflow:auto}
.nav-logo{padding:0 18px 22px;font-size:15px;font-weight:700}
.nav-logo b{color:var(--accent)}
.nav-link{display:block;padding:9px 18px;color:var(--muted);font-size:13px;
  font-weight:600;border-radius:8px;margin:1px 8px;cursor:pointer;transition:all .15s}
.nav-link:hover{background:var(--card);color:var(--text)}
.nav-link.on{background:rgba(77,144,240,.12);color:var(--accent)}
.nav-foot{margin-top:auto;padding:14px 10px 0}
.asec{display:none}
.asec.on{display:block}
.sec-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{font-size:17px;font-weight:700}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:15px}
.stat-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
.stat-val{font-size:26px;font-weight:700;font-family:monospace}
.blue{color:var(--accent)}.green{color:var(--green)}.red{color:var(--red)}.amber{color:var(--amber)}
.hot-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}
.hot-row:last-child{border-bottom:none}
.hot-name{flex:1;font-size:13px;font-weight:600}
.hot-bar-bg{flex:2;height:7px;background:var(--border);border-radius:4px;overflow:hidden}
.hot-bar{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--accent),var(--purple))}
.hot-ct{font-family:monospace;font-size:11px;color:var(--muted);min-width:55px;text-align:right}
.sinput{padding:7px 11px;border-radius:7px;background:var(--surface);
  border:1px solid var(--border);color:var(--text);font-family:var(--font);
  font-size:13px;width:190px;outline:none}
.sinput:focus{border-color:var(--accent)}
#toast{position:fixed;bottom:22px;right:22px;background:var(--card);
  border:1px solid var(--border);border-radius:9px;padding:11px 17px;
  font-size:13px;z-index:999;opacity:0;transform:translateY(6px);
  transition:all .22s;pointer-events:none}
#toast.on{opacity:1;transform:translateY(0)}
#toast.ok{border-color:var(--green);color:var(--green)}
#toast.er{border-color:var(--red);color:var(--red)}
.fl{display:flex}.ic{align-items:center}.g8{gap:8px}
.sign-out-btn{position:fixed;top:16px;right:16px;z-index:50;display:none}
.sign-out-btn.on{display:block}

/* Modal overlay */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;
  display:flex;align-items:center;justify-content:center;padding:20px}
.modal-overlay.hidden{display:none}
.modal-box{background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  width:100%;max-width:540px;max-height:80vh;display:flex;flex-direction:column}
.modal-hdr{padding:18px 22px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between}
.modal-title{font-weight:700;font-size:16px}
.modal-body{padding:22px;overflow-y:auto;flex:1;font-size:13px;line-height:1.7;color:var(--muted)}
.modal-body h3{color:var(--text);font-size:14px;margin:16px 0 6px}
.modal-body p{margin-bottom:10px}
.modal-foot{padding:14px 22px;border-top:1px solid var(--border);display:flex;gap:10px;justify-content:flex-end}
</style>
</head>
<body>

<button class="btn btn-ghost btn-sm sign-out-btn" id="global-signout" onclick="signOut()">Sign out</button>

<!-- Terms of Service Modal -->
<div class="modal-overlay hidden" id="tos-modal">
  <div class="modal-box">
    <div class="modal-hdr">
      <div class="modal-title">NFCLend — Terms of Service</div>
    </div>
    <div class="modal-body">
      <p><strong>Last updated: January 2025</strong></p>
      <p>Please read these Terms of Service ("Terms") carefully before creating an account with NFCLend ("the Service"). By registering, you agree to be bound by these Terms.</p>

      <h3>1. Eligibility</h3>
      <p>You must be a current member of the organization operating this Service to use it. Accounts are non-transferable and linked to your issued NFC card. Use of another person's NFC card is strictly prohibited.</p>

      <h3>2. Equipment Lending</h3>
      <p>Items are made available for temporary use only. You are responsible for all equipment from the time of checkout until it is returned and confirmed by the system. You may only have one item checked out at a time unless otherwise permitted by an administrator.</p>

      <h3>3. Care of Equipment</h3>
      <p>You agree to treat all borrowed equipment with reasonable care and return it in the same condition it was received. Any damage, loss, or theft must be reported to an administrator immediately. You may be held liable for the cost of repair or replacement of damaged or lost items.</p>

      <h3>4. Returns</h3>
      <p>Equipment must be returned promptly. Failure to return items in a timely manner may result in suspension of lending privileges and notification to relevant administrators. You will receive email confirmations for checkouts and returns.</p>

      <h3>5. Biometric Data (Face Recognition)</h3>
      <p>This Service collects and stores facial image data for the purpose of identity verification during equipment checkout. This data is stored locally on the system and is not shared with third parties. By completing face registration, you consent to this collection. You may request deletion of your facial data at any time by contacting an administrator or through your account settings.</p>

      <h3>6. Account Security</h3>
      <p>You are responsible for maintaining the confidentiality of your password and NFC card. Report any lost or stolen cards to an administrator immediately. NFCLend is not liable for unauthorized use of your account prior to notification.</p>

      <h3>7. Account Termination</h3>
      <p>Administrators may suspend or terminate your account for violations of these Terms, misuse of equipment, or other conduct detrimental to the Service. You may also delete your own account at any time, provided you have no items currently checked out. Deletion anonymizes your account but transaction history may be retained for record-keeping purposes.</p>

      <h3>8. Privacy</h3>
      <p>Your name, email address, and NFC card ID are stored to operate the Service. Email addresses may be used to send transactional notifications (checkout confirmations, return confirmations, and reminders). We do not sell or share your personal information with third parties except as required by law.</p>

      <h3>9. Limitation of Liability</h3>
      <p>NFCLend and its operators are not liable for any indirect, incidental, or consequential damages arising from your use of the Service. The Service is provided "as is" without warranties of any kind.</p>

      <h3>10. Changes to Terms</h3>
      <p>These Terms may be updated periodically. Continued use of the Service after changes constitutes acceptance of the revised Terms. Material changes will be communicated by administrators.</p>

      <h3>11. Contact</h3>
      <p>Questions about these Terms should be directed to your system administrator.</p>
    </div>
    <div class="modal-foot">
      <button class="btn btn-ghost" onclick="declineToS()">Decline</button>
      <button class="btn btn-primary" onclick="acceptToS()">I Agree — Continue</button>
    </div>
  </div>
</div>

<!-- idle -->
<div class="screen center on" id="screen-idle">
  <div class="box" style="text-align:center">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="icon-big pulse">📡</div>
    <div class="title">Scan your card</div>
    <div class="sub">Hold your NFC card to the reader to begin</div>
    <div class="mono" id="idle-status" style="margin-top:30px">Waiting for scan...</div>
  </div>
</div>

<!-- new user register form -->
<div class="screen center" id="screen-register">
  <div class="box">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">Create Account</div>
    <div class="sub">New card — fill in your details</div>
    <div class="card">
      <div class="fg"><label>Full Name</label><input id="rg-name" autocomplete="off"></div>
      <div class="fg"><label>Email</label><input id="rg-email" type="email"></div>
      <div class="fg"><label>Password</label><input id="rg-pw" type="password"></div>
      <div class="err-msg" id="rg-err"></div>
      <div style="display:flex;gap:10px;margin-top:4px">
        <button class="btn btn-ghost btn-full" onclick="signOut()">Cancel</button>
        <button class="btn btn-primary btn-full" onclick="showToS()">Review Terms &amp; Continue</button>
      </div>
    </div>
  </div>
</div>

<!-- face capture spinner -->
<div class="screen center" id="screen-face-capture">
  <div class="box" style="text-align:center">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title" id="fc-title">Face Registration</div>
    <div class="sub" id="fc-sub">Look directly at the Mac camera and stay still</div>
    <div class="card" style="text-align:center">
      <div class="spin"></div>
      <div style="font-weight:600;margin-bottom:6px" id="fc-msg">Capturing your face...</div>
      <div style="font-size:12px;color:var(--muted)">This takes about 10 seconds</div>
    </div>
  </div>
</div>
<!-- password screen -->
<div class="screen center" id="screen-password">
  <div class="box">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="card">
      <div class="chip">
        <div class="avatar" id="pw-av">?</div>
        <div>
          <div class="chip-name" id="pw-name">Loading...</div>
          <div class="chip-sub">Enter your password</div>
        </div>
      </div>
      <div class="fg"><label>Password</label>
        <input id="pw-input" type="password" onkeydown="if(event.key==='Enter')submitPassword()">
      </div>
      <div class="err-msg" id="pw-err">Incorrect password. Try again.</div>
      <div style="display:flex;gap:10px">
        <button class="btn btn-ghost btn-full" onclick="signOut()">Cancel</button>
        <button class="btn btn-primary btn-full" onclick="submitPassword()">Sign In</button>
      </div>
    </div>
  </div>
</div>
<!-- face verify spinner -->
<div class="screen center" id="screen-face-verify">
  <div class="box" style="text-align:center">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">Face Verification</div>
    <div class="sub">Look directly at the Mac camera</div>
    <div class="card" style="text-align:center">
      <div class="spin"></div>
      <div style="font-weight:600;margin-bottom:6px" id="fv-msg">Verifying...</div>
      <div style="font-size:12px;color:var(--muted)" id="fv-attempt"></div>
    </div>
    <div style="margin-top:14px">
      <button class="btn btn-ghost btn-sm" id="fv-skip-btn" onclick="skipFace()" style="display:none">
        Skip — use password only
      </button>
    </div>
  </div>
</div>

<!-- user home -->
<div class="screen center" id="screen-user-home">
  <div class="box">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="chip">
      <div class="avatar" id="uh-av">?</div>
      <div>
        <div class="chip-name" id="uh-name">User</div>
        <div class="chip-sub" id="uh-email"></div>
      </div>
    </div>
    <div id="uh-renting-notice" style="display:none;padding:10px 14px;background:rgba(245,166,35,.08);
      border:1px solid rgba(245,166,35,.25);border-radius:9px;font-size:13px;
      color:var(--amber);margin-bottom:16px"></div>
    <div class="menu-grid">
      <button class="menu-btn" onclick="startRent()">
        <div class="menu-icon">📦</div>
        <span class="menu-label">Rent Item</span>
        <div class="menu-sub">Browse catalog</div>
      </button>
      <button class="menu-btn" onclick="startReturn()">
        <div class="menu-icon">↩️</div>
        <span class="menu-label">Return Item</span>
        <div class="menu-sub">Scan item to return</div>
      </button>
      <button class="menu-btn" onclick="loadUserHistory()">
        <div class="menu-icon">📋</div>
        <span class="menu-label">My History</span>
        <div class="menu-sub">Past rentals</div>
      </button>
      <button class="menu-btn" onclick="openAccount()">
        <div class="menu-icon">👤</div>
        <span class="menu-label">Account</span>
        <div class="menu-sub">Settings</div>
      </button>
    </div>
  </div>
</div>

<!-- equipment list -->
<div class="screen center" id="screen-equip-list">
  <div class="box" style="max-width:520px">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">Equipment Catalog</div>
    <div class="sub">Select an available item to rent</div>
    <div id="equip-list-container"></div>
    <button class="btn btn-ghost btn-full" style="margin-top:12px" onclick="showScreen('user-home')">Back</button>
  </div>
</div>

<!-- scan to rent -->
<div class="screen center" id="screen-scan-rent">
  <div class="box" style="text-align:center">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="icon-big pulse">🏷️</div>
    <div class="title">Scan Item</div>
    <div class="sub">Hold the NFC tag of <strong id="sr-item-name">the item</strong> to the reader to confirm</div>
    <div class="mono" style="margin-top:20px">Waiting for item scan...</div>
    <button class="btn btn-ghost btn-sm" style="margin-top:20px" onclick="showScreen('equip-list');startPoll()">Back</button>
  </div>
</div>

<!-- scan to return -->
<div class="screen center" id="screen-scan-return">
  <div class="box" style="text-align:center">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="icon-big pulse">🔄</div>
    <div class="title">Scan Item to Return</div>
    <div class="sub">Hold the item's NFC tag to the reader</div>
    <div class="mono" style="margin-top:20px">Waiting for item scan...</div>
    <button class="btn btn-ghost btn-sm" style="margin-top:20px" onclick="showScreen('user-home');stopPoll()">Back</button>
  </div>
</div>

<!-- return form -->
<div class="screen center" id="screen-return-form">
  <div class="box">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">Return Item</div>
    <div class="sub">Complete return for <strong id="rf-item-name">item</strong></div>
    <div class="card">
      <div class="fg">
        <label>Rating (1–10)</label>
        <div class="rating-row" id="rating-row"></div>
        <div style="font-size:12px;color:var(--muted)" id="rating-display">None selected — skip</div>
      </div>
      <div class="fg" style="margin-top:14px">
        <label>Condition Report <span style="color:var(--red)">*</span></label>
        <textarea id="rf-condition" placeholder="Describe the condition: Good / Minor wear / Damaged — add any notes..."></textarea>
      </div>
      <div class="err-msg" id="rf-err">Please fill in the condition report.</div>
      <div style="display:flex;gap:10px;margin-top:6px">
        <button class="btn btn-ghost btn-full" onclick="showScreen('user-home')">Cancel</button>
        <button class="btn btn-green btn-full" onclick="confirmReturn()">Confirm Return</button>
      </div>
    </div>
  </div>
</div>

<!-- user history -->
<div class="screen center" id="screen-history">
  <div class="box" style="max-width:640px">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">My Rental History</div>
    <div style="margin-top:16px" id="hist-container"></div>
    <button class="btn btn-ghost btn-full" style="margin-top:14px" onclick="showScreen('user-home')">Back</button>
  </div>
</div>
<!-- account -->
<div class="screen center" id="screen-account">
  <div class="box" style="max-width:500px">
    <div class="logo">NFC<b>Lend</b></div>
    <div class="title">My Account</div>

    <!-- Info display -->
    <div class="card" style="margin-bottom:14px">
      <div style="margin-bottom:12px">
        <div style="font-size:11px;color:var(--muted);margin-bottom:3px">NAME</div>
        <div style="font-weight:700" id="acc-name">—</div>
      </div>
      <div style="margin-bottom:12px">
        <div style="font-size:11px;color:var(--muted);margin-bottom:3px">EMAIL</div>
        <div id="acc-email">—</div>
      </div>
      <div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:3px">NFC ID</div>
        <div class="mono" id="acc-nfc">—</div>
      </div>
    </div>

    <!-- Edit profile -->
    <div class="card" style="margin-bottom:14px">
      <div style="font-weight:700;margin-bottom:14px">Edit Profile</div>
      <div class="fg"><label>New Name <span style="color:var(--muted)">(leave blank to keep current)</span></label>
        <input id="edit-name" autocomplete="off" placeholder="Username (must be unique)">
      </div>
      <div class="fg"><label>New Email <span style="color:var(--muted)">(leave blank to keep current)</span></label>
        <input id="edit-email" type="email">
      </div>
      <div class="fg"><label>New Password <span style="color:var(--muted)">(leave blank to keep current)</span></label>
        <input id="edit-pw" type="password">
      </div>
      <div class="err-msg" id="edit-err"></div>
      <div class="ok-msg" id="edit-ok">Profile updated!</div>
      <button class="btn btn-primary btn-full" onclick="saveProfile()">Save Changes</button>
    </div>

    <!-- Delete account -->
    <div class="card" style="margin-bottom:14px">
      <div style="font-size:13px;color:var(--muted);margin-bottom:12px">
        Delete your account permanently. You must return any rented items first.
        Transaction history is retained for record-keeping.
      </div>
      <button class="btn btn-danger btn-full" onclick="deleteSelfAccount()">Delete My Account</button>
    </div>

    <button class="btn btn-ghost btn-full" onclick="showScreen('user-home')">Back</button>
  </div>
</div>

<!-- admin dashboard -->
<div class="screen" id="screen-admin">
  <nav id="admin-nav">
    <div class="nav-logo">NFC<b>Lend</b></div>
    <a class="nav-link on" id="nav-overview" onclick="adminTab('overview')">📊 Overview</a>
    <a class="nav-link" id="nav-users" onclick="adminTab('users')">👥 Users</a>
    <a class="nav-link" id="nav-equipment" onclick="adminTab('equipment')">📦 Equipment</a>
    <a class="nav-link" id="nav-history" onclick="adminTab('history')">📋 History</a>
    <a class="nav-link" id="nav-emails" onclick="adminTab('emails')">✉️ Emails</a>
    <a class="nav-link" id="nav-hot" onclick="adminTab('hot')">🔥 Hot Items</a>
    <a class="nav-link" id="nav-admin-return" onclick="adminTab('admin-return')">↩️ Return Item</a>
    <div class="nav-foot">
      <div style="font-size:11px;color:var(--muted);padding:0 10px;margin-bottom:8px">
        Admin: <strong id="admin-name-lbl">—</strong>
      </div>
      <button class="btn btn-danger btn-full btn-sm" onclick="signOut()">Sign Out</button>
    </div>
  </nav>
  <div id="admin-body">

    <!-- overview -->
    <div class="asec on" id="asec-overview">
      <div class="sec-hdr"><div class="sec-title">Dashboard</div></div>
      <div class="stat-grid">
        <div class="stat"><div class="stat-lbl">Users</div><div class="stat-val blue" id="sv-users">—</div></div>
        <div class="stat"><div class="stat-lbl">Equipment</div><div class="stat-val green" id="sv-equip">—</div></div>
        <div class="stat"><div class="stat-lbl">Currently Rented</div><div class="stat-val amber" id="sv-rented">—</div></div>
        <div class="stat"><div class="stat-lbl">Total Transactions</div><div class="stat-val" id="sv-tx">—</div></div>
      </div>
      <div class="card">
        <div class="sec-hdr"><div class="sec-title">Recent Transactions</div></div>
        <div class="tw"><table>
          <thead><tr><th>Item</th><th>User</th><th>Checked Out</th><th>Returned</th><th>Rating</th><th>Condition</th></tr></thead>
          <tbody id="ov-tbody"></tbody>
        </table></div>
      </div>
    </div>

    <!-- users -->
    <div class="asec" id="asec-users">
      <div class="sec-hdr">
        <div class="sec-title">Users</div>
        <input class="sinput" placeholder="Search..." oninput="filterAUsers(this.value)">
      </div>
      <div class="tw"><table>
        <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>NFC ID</th><th>Renting</th><th>Actions</th></tr></thead>
        <tbody id="au-tbody"></tbody>
      </table></div>
    </div>

    <!-- equipment -->
    <div class="asec" id="asec-equipment">
      <div class="sec-hdr">
        <div class="sec-title">Equipment</div>
        <div class="fl ic g8">
          <input class="sinput" placeholder="Search..." oninput="filterAEquip(this.value)">
          <button class="btn btn-primary btn-sm" onclick="openAddEquip()">+ Add</button>
        </div>
      </div>
      <div id="add-equip-form" style="display:none;margin-bottom:16px" class="card">
        <div style="font-weight:700;margin-bottom:8px">Add New Equipment</div>
        <div style="font-size:12px;color:var(--amber);margin-bottom:14px;
          background:rgba(245,166,35,.08);border:1px solid rgba(245,166,35,.2);
          border-radius:7px;padding:8px 11px;" id="ae-scan-hint">
          📡 Scan the item's NFC tag on the reader to autofill the ID, or type it manually below.
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px">
          <div class="fg" style="margin-bottom:0"><label>NFC Tag ID</label>
            <input id="ae-tag" placeholder="Scan or type tag ID">
          </div>
          <div class="fg" style="margin-bottom:0"><label>Item Name</label><input id="ae-name"></div>
          <div class="fg" style="margin-bottom:0"><label>Category</label><input id="ae-cat"></div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-ghost btn-sm" onclick="closeAddEquip()">Cancel</button>
          <button class="btn btn-primary btn-sm" onclick="submitAddEquip()">Add Item</button>
        </div>
      </div>
      <div class="tw"><table>
        <thead><tr><th>Name</th><th>Category</th><th>Status</th><th>NFC Tag</th><th>Avg Rating</th><th>Rentals</th><th>Actions</th></tr></thead>
        <tbody id="ae-tbody"></tbody>
      </table></div>
    </div>

    <!-- history -->
    <div class="asec" id="asec-history">
      <div class="sec-hdr">
        <div class="sec-title">Rental History</div>
        <input class="sinput" placeholder="Search..." oninput="filterAHistory(this.value)">
      </div>
      <div class="tw"><table>
        <thead><tr><th>Item</th><th>Category</th><th>User</th><th>Checked Out</th><th>Returned</th><th>Rating</th><th>Condition</th></tr></thead>
        <tbody id="ah-tbody"></tbody>
      </table></div>
    </div>

    <!-- emails -->
    <div class="asec" id="asec-emails">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
        <div class="card">
          <div style="font-weight:700;margin-bottom:16px">Send Reminder</div>
          <div class="fg">
            <label>Select User</label>
            <select id="em-user-select" onchange="autofillReminderUser()">
              <option value="">— Select a user —</option>
            </select>
          </div>
          <div class="fg"><label>User Name</label><input id="em-name"></div>
          <div class="fg"><label>User Email</label><input id="em-email" type="email"></div>
          <div class="fg"><label>Item They Have</label><input id="em-item" placeholder="Auto-filled if user has an item"></div>
          <button class="btn btn-primary" onclick="sendReminder()">Send Reminder</button>
        </div>
        <div class="card">
          <div style="font-weight:700;margin-bottom:16px">Custom Email</div>
          <div class="fg"><label>To Email</label><input id="cm-to" type="email"></div>
          <div class="fg"><label>Subject</label><input id="cm-sub"></div>
          <div class="fg"><label>Message</label><textarea id="cm-body"></textarea></div>
          <button class="btn btn-primary" onclick="sendManual()">Send Email</button>
        </div>
      </div>
    </div>

    <!-- admin return on behalf -->
    <div class="asec" id="asec-admin-return">
      <div class="sec-hdr"><div class="sec-title">Return Item on Behalf of User</div></div>
      <div class="card" style="max-width:520px">
        <p style="font-size:13px;color:var(--muted);margin-bottom:18px">
          Scan the item's NFC tag, or select a user with a rented item below, then confirm the return.
        </p>

        <!-- Option A: scan -->
        <div style="margin-bottom:18px">
          <div style="font-weight:700;font-size:13px;margin-bottom:10px">Option A — Scan Item Tag</div>
          <div style="background:rgba(77,144,240,.08);border:1px solid rgba(77,144,240,.2);
            border-radius:8px;padding:12px 14px;font-size:13px;color:var(--accent)" id="ar-scan-status">
            📡 Waiting for scan... (open this tab and scan the tag)
          </div>
          <div id="ar-scanned-info" style="display:none;margin-top:10px;
            background:rgba(52,199,123,.06);border:1px solid rgba(52,199,123,.2);
            border-radius:8px;padding:12px 14px;font-size:13px">
          </div>
        </div>

        <!-- Option B: select user -->
        <div style="margin-bottom:18px">
          <div style="font-weight:700;font-size:13px;margin-bottom:10px">Option B — Select a User</div>
          <select id="ar-user-select" onchange="selectAdminReturnUser()" style="margin-bottom:10px">
            <option value="">— Users with items out —</option>
          </select>
          <div id="ar-selected-info" style="display:none;
            background:rgba(52,199,123,.06);border:1px solid rgba(52,199,123,.2);
            border-radius:8px;padding:12px 14px;font-size:13px">
          </div>
        </div>

        <div class="fg">
          <label>Condition Report <span style="color:var(--muted)">(optional)</span></label>
          <textarea id="ar-condition" placeholder="Returned by admin / condition notes...">Returned by admin</textarea>
        </div>
        <div class="err-msg" id="ar-err"></div>
        <button class="btn btn-amber btn-full" id="ar-confirm-btn" onclick="confirmAdminReturn()" disabled
          style="opacity:.5;cursor:not-allowed">
          Confirm Return
        </button>
      </div>
    </div>

    <!-- hot items -->
    <div class="asec" id="asec-hot">
      <div class="sec-hdr"><div class="sec-title">Equipment Popularity</div></div>
      <div class="card" style="margin-bottom:16px">
        <div id="hot-bars"></div>
      </div>
      <div class="tw"><table>
        <thead><tr><th>Item</th><th>Category</th><th>Total Rentals</th><th>Avg Rating</th><th>Status</th></tr></thead>
        <tbody id="hot-tbody"></tbody>
      </table></div>
    </div>

  </div>
</div>

<div id="toast"></div>

<script>
const $ = id => document.getElementById(id)

let S = {
  uid: null,
  user: null,
  pendingEquip: null,
  faceAttempts: 0,
  selectedRating: null,
  pollTimer: null,
  waitEquip: false,
  rentOrReturn: null,
  tosAccepted: false,

  adminReturnTag: null,
  adminReturnPollTimer: null,
  adminReturnPollMode: false, 
}

let _aUsers = [], _aEquip = [], _aHist = []

function toast(msg, ok=true) {
  const t = $('toast')
  t.textContent = msg
  t.className = 'on ' + (ok ? 'ok' : 'er')
  clearTimeout(t._t)
  t._t = setTimeout(() => t.className = '', 3000)
}

function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('on'))
  $('screen-' + name).classList.add('on')
  const showSignOut = !['idle','register','face-capture','password','face-verify'].includes(name)
  $('global-signout').className = 'btn btn-ghost btn-sm sign-out-btn' + (showSignOut ? ' on' : '')
  if (name === 'admin') $('global-signout').style.display = 'none'
  else $('global-signout').style.display = ''
}

function signOut() {
  stopPoll()
  stopAdminReturnPoll()
  S = {uid:null,user:null,pendingEquip:null,faceAttempts:0,
       selectedRating:null,pollTimer:null,waitEquip:false,rentOrReturn:null,
       tosAccepted:false,adminReturnTag:null,adminReturnPollTimer:null,adminReturnPollMode:false}
  showScreen('idle')
  startPoll()
}

function showToS() {
  const name = $('rg-name').value.trim()
  const email = $('rg-email').value.trim()
  const pw = $('rg-pw').value
  const err = $('rg-err')
  if (!name || !email || !pw) {
    err.textContent = 'Name, email, and password are required.'
    err.style.display = 'block'
    return
  }
  err.style.display = 'none'
  $('tos-modal').classList.remove('hidden')
}
function acceptToS() {
  S.tosAccepted = true
  $('tos-modal').classList.add('hidden')
  submitRegister()
}
function declineToS() {
  $('tos-modal').classList.add('hidden')
  toast('You must accept the Terms of Service to create an account.', false)
}
function startPoll() {
  stopPoll()
  S.pollTimer = setInterval(pollScan, 1500)
}
function stopPoll() {
  clearInterval(S.pollTimer)
  S.pollTimer = null
}

async function pollScan() {
  const active = document.querySelector('.screen.on')
  if (!active) return
  const id = active.id.replace('screen-', '')
  const wantUser = id === 'idle'
  const wantEquip = id === 'scan-rent' || id === 'scan-return'
  if (!wantUser && !wantEquip) return
  try {
    const r = await fetch('/api/scan').then(r => r.json())
    if (!r.uid) return
    await fetch('/api/scan', {method: 'DELETE'})
    if (wantUser) await handleUserScan(r.uid)
    else if (wantEquip) await handleEquipScan(r.uid)
  } catch(e) {}
}

let _equipFormPollTimer = null

function startEquipFormPoll() {
  clearInterval(_equipFormPollTimer)
  _equipFormPollTimer = setInterval(async () => {
    if ($('add-equip-form').style.display === 'none') return
    try {
      const r = await fetch('/api/scan').then(r => r.json())
      if (!r.uid) return
      const userCheck = await fetch(`/api/user/${r.uid}`).then(r => r.json())
      if (userCheck.found) return //ignore if its a person's card
      await fetch('/api/scan', {method: 'DELETE'})
      $('ae-tag').value = r.uid
      $('ae-scan-hint').textContent = 'Tag autofilled from scan: ' + r.uid
      $('ae-scan-hint').style.background = 'rgba(52,199,123,.08)'
      $('ae-scan-hint').style.borderColor = 'rgba(52,199,123,.3)'
      $('ae-scan-hint').style.color = 'var(--green)'
      toast('Tag autofilled: ' + r.uid)
    } catch(e) {}
  }, 1200)
}

function stopEquipFormPoll() {
  clearInterval(_equipFormPollTimer)
  _equipFormPollTimer = null
}

function startAdminReturnPoll() {
  stopAdminReturnPoll()
  S.adminReturnPollTimer = setInterval(async () => {
    const active = document.querySelector('.screen.on')
    if (!active || active.id !== 'screen-admin') { stopAdminReturnPoll(); return }
    if (!$('asec-admin-return').classList.contains('on')) return
    try {
      const r = await fetch('/api/scan').then(r => r.json())
      if (!r.uid) return
      await fetch('/api/scan', {method: 'DELETE'})
      await handleAdminReturnScan(r.uid)
    } catch(e) {}
  }, 1200)
}

function stopAdminReturnPoll() {
  clearInterval(S.adminReturnPollTimer)
  S.adminReturnPollTimer = null
}

async function handleAdminReturnScan(uid) {
  const eqCheck = await fetch(`/api/equipment/${uid}`).then(r => r.json())
  if (eqCheck.found) {
    const item = eqCheck.item
    if (item.status !== 'rented') {
      $('ar-scan-status').textContent = 'That item (' + item.name + ') is not currently rented out.'
      $('ar-scanned-info').style.display = 'none'
      S.adminReturnTag = null
      enableAdminReturnBtn(false)
      return
    }
    S.adminReturnTag = uid
    $('ar-scan-status').textContent = 'Scanned: ' + item.name
    $('ar-scanned-info').style.display = 'block'
    $('ar-scanned-info').innerHTML = `<strong>${item.name}</strong> — currently rented out<br>
      <span style="color:var(--muted);font-size:12px">Tag: ${uid}</span>`
    $('ar-user-select').value = ''
    $('ar-selected-info').style.display = 'none'
    enableAdminReturnBtn(true)
  } else {
    $('ar-scan-status').textContent = 'Unknown tag scanned: ' + uid
  }
}

function enableAdminReturnBtn(on) {
  const btn = $('ar-confirm-btn')
  btn.disabled = !on
  btn.style.opacity = on ? '1' : '.5'
  btn.style.cursor = on ? 'pointer' : 'not-allowed'
}
async function loadAdminReturnUsers() {
  const users = await fetch('/api/users').then(r => r.json())
  const sel = $('ar-user-select')
  sel.innerHTML = '<option value="">— Users with items out —</option>'
  const renting = users.filter(u => u.rented_item_uid)
  if (!renting.length) {
    sel.innerHTML = '<option value="">No users have items out</option>'
    return
  }
  renting.forEach(u => {
    const opt = document.createElement('option')
    opt.value = u.rented_item_uid
    opt.textContent = `${u.name} → ${u.rented_item_uid}`
    sel.appendChild(opt)
  })
}

async function selectAdminReturnUser() {
  const tag = $('ar-user-select').value
  if (!tag) {
    $('ar-selected-info').style.display = 'none'
    if (!S.adminReturnTag) enableAdminReturnBtn(false)
    return
  }
  const eq = await fetch(`/api/equipment/${tag}`).then(r => r.json())
  const itemName = eq.found ? eq.item.name : tag
  S.adminReturnTag = tag
  $('ar-scanned-info').style.display = 'none'
  $('ar-scan-status').textContent = '📡 Waiting for scan...'
  $('ar-selected-info').style.display = 'block'
  $('ar-selected-info').innerHTML = `<strong>${itemName}</strong> selected for return`
  enableAdminReturnBtn(true)
}

async function confirmAdminReturn() {
  if (!S.adminReturnTag) return
  const condition = $('ar-condition').value.trim() || 'Returned by admin'
  const r = await fetch(`/api/admin-return/${S.adminReturnTag}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({condition_report: condition})
  }).then(r => r.json())
  if (r.success) {
    toast(`Returned "${r.item_name}" for ${r.user_name}`)
    if (r.user_email) {
      fetch('/api/email/return-confirmation', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({email: r.user_email, user_name: r.user_name,
          item_name: r.item_name, rating: null})
      })
    }
    S.adminReturnTag = null
    $('ar-scan-status').textContent = '📡 Waiting for scan...'
    $('ar-scanned-info').style.display = 'none'
    $('ar-user-select').value = ''
    $('ar-selected-info').style.display = 'none'
    $('ar-condition').value = 'Returned by admin'
    $('ar-err').style.display = 'none'
    enableAdminReturnBtn(false)
    loadAdminReturnUsers()
  } else {
    $('ar-err').textContent = r.error || 'Return failed'
    $('ar-err').style.display = 'block'
  }
}

//user scan
async function handleUserScan(uid) {
  stopPoll()
  S.uid = uid
  try {
    const data = await fetch(`/api/user/${uid}`).then(r => r.json())
    if (data.found) {
      S.user = data.user
      $('pw-name').textContent = S.user.name + (S.user.role === 'admin' ? ' (Admin)' : '')
      $('pw-av').textContent = S.user.name[0].toUpperCase()
      $('pw-err').style.display = 'none'
      $('pw-input').value = ''
      showScreen('password')
      setTimeout(() => $('pw-input').focus(), 80)
    } else {
      S.user = null
      $('rg-name').value = ''
      $('rg-email').value = ''
      $('rg-pw').value = ''
      $('rg-err').style.display = 'none'
      showScreen('register')
    }
  } catch(e) {
    toast('Server error', false)
    signOut()
  }
}

async function submitPassword() {
  const pw = $('pw-input').value
  if (!pw) return
  if (pw !== S.user.password) {
    $('pw-err').style.display = 'block'
    $('pw-input').value = ''
    $('pw-input').focus()
    return
  }
  $('pw-err').style.display = 'none'
  if (S.user.role === 'admin') {
    $('admin-name-lbl').textContent = S.user.name
    showScreen('admin')
    loadAdminOverview()
    return
  }
  S.faceAttempts = 0
  doFaceVerify()
}

async function doFaceVerify() {
  S.faceAttempts++
  $('fv-msg').textContent = 'Look at the Mac camera...'
  $('fv-attempt').textContent = `Attempt ${S.faceAttempts} of 3`
  $('fv-skip-btn').style.display = 'none'
  showScreen('face-verify')
  try {
    const r = await fetch('/api/verify-face', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({user_id: S.uid, frames: 8})
    }).then(r => r.json())

    if (r.verified) {
      goToUserHome()
    } else if (r.message && r.message.includes('No registered face')) {
      goToUserHome()
    } else if (S.faceAttempts < 3) {
      $('fv-msg').innerHTML = 'Not verified. <button class="btn btn-ghost btn-sm" onclick="doFaceVerify()" style="margin-left:8px">Retry</button>'
      $('fv-attempt').textContent = `Attempt ${S.faceAttempts} of 3 — align your face and click retry`
    } else {
      $('fv-msg').textContent = 'Face verification failed after 3 attempts.'
      $('fv-attempt').textContent = ''
      $('fv-skip-btn').style.display = 'inline-flex'
    }
  } catch(e) {
    $('fv-msg').textContent = 'Camera error.'
    $('fv-skip-btn').style.display = 'inline-flex'
  }
}

function skipFace() {
  goToUserHome()
}

function goToUserHome() {
  $('uh-name').textContent = S.user.name
  $('uh-av').textContent = S.user.name[0].toUpperCase()
  $('uh-email').textContent = S.user.email || ''
  const notice = $('uh-renting-notice')
  if (S.user.rented_item_uid) {
    notice.style.display = 'block'
    notice.textContent = 'You currently have an item checked out. Please return it before renting another.'
  } else {
    notice.style.display = 'none'
  }
  showScreen('user-home')
}

//registration stuff
async function submitRegister() {
  if (!S.tosAccepted) { showToS(); return }
  const name = $('rg-name').value.trim()
  const email = $('rg-email').value.trim()
  const pw = $('rg-pw').value
  $('fc-title').textContent = 'Face Registration'
  $('fc-sub').textContent = 'Look directly at the Mac camera and stay still'
  $('fc-msg').textContent = 'Capturing your face...'
  showScreen('face-capture')
  try {
    const faceR = await fetch('/api/register-face', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({user_id: S.uid, frames: 15})
    }).then(r => r.json())
    if (!faceR.success) {
      toast('Face registration failed — try again', false)
      showScreen('register')
      return
    }
    const userR = await fetch('/api/user', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({nfc_id: S.uid, name, email, password: pw})
    }).then(r => r.json())
    if (!userR.success) {
      toast('Account creation failed: ' + (userR.error || 'unknown'), false)
      showScreen('register')
      return
    }
    const fresh = await fetch(`/api/user/${S.uid}`).then(r => r.json())
    S.user = fresh.user
    toast('Account created!')
    goToUserHome()
  } catch(e) {
    toast('Error during registration', false)
    signOut()
  }
}

//rent stuff
async function startRent() {
  if (S.user.rented_item_uid) { toast('Return your current item first', false); return }
  S.rentOrReturn = 'rent'
  showScreen('equip-list')
  const items = await fetch('/api/equipment').then(r => r.json())
  const c = $('equip-list-container')
  c.innerHTML = ''
  items.forEach(item => {
    const avail = item.status === 'available'
    const div = document.createElement('div')
    div.className = 'eq-item' + (avail ? '' : ' rented')
    div.innerHTML = `
      <div>
        <div class="eq-name">${item.name}</div>
        <div class="eq-cat">${item.category || ''} ${item.avg_rating > 0 ? '· ⭐ ' + Number(item.avg_rating).toFixed(1) : ''}</div>
      </div>
      <span class="badge ${avail ? 'bg' : 'br'}">${avail ? 'Available' : 'Rented'}</span>
    `
    if (avail) {
      div.onclick = () => {
        S.pendingEquip = item
        $('sr-item-name').textContent = item.name
        showScreen('scan-rent')
        startPoll()
      }
    }
    c.appendChild(div)
  })
}
function startReturn() {
  if (!S.user.rented_item_uid) { toast('You have no item to return', false); return }
  S.rentOrReturn = 'return'
  showScreen('scan-return')
  startPoll()
}

//equipment scan 
async function handleEquipScan(uid) {
  stopPoll()
  const eq = await fetch(`/api/equipment/${uid}`).then(r => r.json())
  if (!eq.found) { toast('Unknown item scanned', false); startPoll(); return }

  if (S.rentOrReturn === 'rent') {
    if (eq.item.nfc_tag !== S.pendingEquip.nfc_tag) {
      toast(`Wrong item scanned — expected ${S.pendingEquip.name}`, false)
      startPoll()
      return
    }
    if (eq.item.status !== 'available') { toast('Item already rented out', false); showScreen('equip-list'); return }
    const r = await fetch(`/api/checkout/${uid}`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({user_nfc: S.uid})
    }).then(r => r.json())
    if (r.success) {
      S.user.rented_item_uid = uid
      toast('Rented successfully!')
      if (S.user.email) {
        fetch('/api/email/rental-confirmation', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({email: S.user.email, user_name: S.user.name, item_name: eq.item.name})
        })
      }
      goToUserHome()
    } else {
      toast('Checkout failed: ' + (r.error || ''), false)
      showScreen('user-home')
    }

  } else if (S.rentOrReturn === 'return') {
    if (S.user.rented_item_uid !== uid) {
      toast('That item is not assigned to you', false)
      startPoll()
      return
    }
    S.pendingEquip = eq.item
    S.selectedRating = null
    buildRatingRow()
    $('rf-item-name').textContent = eq.item.name
    $('rf-condition').value = ''
    $('rf-err').style.display = 'none'
    showScreen('return-form')
  }
}

function buildRatingRow() {
  const row = $('rating-row')
  row.innerHTML = ''
  for (let i = 1; i <= 10; i++) {
    const b = document.createElement('button')
    b.className = 'rn'
    b.textContent = i
    b.onclick = () => selectRating(i)
    row.appendChild(b)
  }
  $('rating-display').textContent = 'None selected — skip'
}

function selectRating(n) {
  S.selectedRating = n
  document.querySelectorAll('.rn').forEach((b, i) => b.classList.toggle('sel', i === n - 1))
  $('rating-display').textContent = `${n} / 10`
}

async function confirmReturn() {
  const condition = $('rf-condition').value.trim()
  if (!condition) { $('rf-err').style.display = 'block'; return }
  $('rf-err').style.display = 'none'
  const r = await fetch(`/api/return/${S.pendingEquip.nfc_tag}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      user_nfc: S.uid,
      rating: S.selectedRating,
      condition_report: condition
    })
  }).then(r => r.json())
  if (r.success) {
    S.user.rented_item_uid = null
    toast('Returned successfully!')
    if (S.user.email) {
      fetch('/api/email/return-confirmation', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          email: S.user.email, user_name: S.user.name,
          item_name: S.pendingEquip.name, rating: S.selectedRating
        })
      })
    }
    S.pendingEquip = null
    S.selectedRating = null
    goToUserHome()
  } else {
    toast('Return failed: ' + (r.error || ''), false)
  }
}

//user history
async function loadUserHistory() {
  showScreen('history')
  const hist = await fetch(`/api/history/user/${S.uid}`).then(r => r.json())
  const c = $('hist-container')
  if (!hist.length) {
    c.innerHTML = '<div style="text-align:center;color:var(--muted);padding:40px">No rental history yet.</div>'
    return
  }
  c.innerHTML = ''
  hist.forEach(h => {
    const div = document.createElement('div')
    div.style.cssText = 'background:var(--card);border:1px solid var(--border);border-radius:9px;padding:13px 15px;margin-bottom:10px'
    const ret = h.return_time ? fmt(h.return_time) : '<span class="badge ba">Still out</span>'
    const rating = h.rating ? `${h.rating}/10` : '—'
    const cond = h.condition_report || '—'
    div.innerHTML = `
      <div style="font-weight:700;margin-bottom:5px">${h.item_name}</div>
      <div style="font-size:12px;color:var(--muted)">
        Out: ${fmt(h.checkout_time)} · Returned: ${ret} · Rating: ${rating}
      </div>
      <div style="font-size:12px;color:var(--muted);margin-top:3px">Condition: ${cond}</div>
    `
    c.appendChild(div)
  })
}

function openAccount() {
  $('acc-name').textContent = S.user.name || '—'
  $('acc-email').textContent = S.user.email || '—'
  $('acc-nfc').textContent = S.uid || '—'
  $('edit-name').value = ''
  $('edit-email').value = ''
  $('edit-pw').value = ''
  $('edit-err').style.display = 'none'
  $('edit-ok').style.display = 'none'
  showScreen('account')
}

async function saveProfile() {
  const newName = $('edit-name').value.trim()
  const newEmail = $('edit-email').value.trim()
  const newPw = $('edit-pw').value
  const errEl = $('edit-err')
  const okEl = $('edit-ok')
  errEl.style.display = 'none'
  okEl.style.display = 'none'
  if (!newName && !newEmail && !newPw) {
    errEl.textContent = 'Enter at least one field to update.'
    errEl.style.display = 'block'
    return
  }
  const body = {}
  if (newName) body.name = newName
  if (newEmail) body.email = newEmail
  if (newPw) body.password = newPw
  const r = await fetch(`/api/user/${S.uid}/profile`, {
    method: 'PATCH',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  }).then(r => r.json())
  if (r.success) {
    S.user = r.user
    $('acc-name').textContent = S.user.name
    $('acc-email').textContent = S.user.email || '—'
    $('uh-name').textContent = S.user.name
    $('uh-av').textContent = S.user.name[0].toUpperCase()
    $('uh-email').textContent = S.user.email || ''
    $('edit-name').value = ''
    $('edit-email').value = ''
    $('edit-pw').value = ''
    okEl.style.display = 'block'
    toast('Profile updated!')
  } else {
    errEl.textContent = r.error || 'Update failed.'
    errEl.style.display = 'block'
  }
}

async function deleteSelfAccount() {
  if (S.user.rented_item_uid) {
    toast('Return your rented item first', false)
    return
  }
  const fresh = await fetch(`/api/user/${S.uid}`).then(r => r.json())
  if (fresh.found && fresh.user.rented_item_uid) {
    toast('Return your rented item first', false)
    return
  }
  if (!confirm(`Delete account for "${S.user.name}"? This cannot be undone.`)) return
  const r = await fetch(`/api/user/${S.uid}`, {method:'DELETE'}).then(r=>r.json())
  if (r.success) { toast('Account deleted'); signOut() }
  else toast(r.error || 'Failed', false)
}

//admin options
function adminTab(name) {
  document.querySelectorAll('.asec').forEach(s => s.classList.remove('on'))
  document.querySelectorAll('.nav-link').forEach(a => a.classList.remove('on'))
  $('asec-' + name).classList.add('on')
  $('nav-' + name).classList.add('on')
  stopAdminReturnPoll()
  stopEquipFormPoll()
  if (name === 'overview') loadAdminOverview()
  else if (name === 'users') loadAdminUsers()
  else if (name === 'equipment') loadAdminEquip()
  else if (name === 'history') loadAdminHistory()
  else if (name === 'hot') loadHot()
  else if (name === 'emails') loadEmailUsers()
  else if (name === 'admin-return') { loadAdminReturnUsers(); startAdminReturnPoll() }
}

async function loadAdminOverview() {
  try {
    const [sum, hist] = await Promise.all([
      fetch('/api/stats/summary').then(r => r.json()),
      fetch('/api/history').then(r => r.json())
    ])
    $('sv-users').textContent = sum.users ?? '—'
    $('sv-equip').textContent = sum.equipment_total ?? '—'
    $('sv-rented').textContent = sum.equipment_rented ?? '—'
    $('sv-tx').textContent = sum.total_transactions ?? '—'
    const tbody = $('ov-tbody')
    tbody.innerHTML = ''
    const rows = Array.isArray(hist) ? hist.slice(0, 15) : []
    rows.forEach(r => {
      const tr = document.createElement('tr')
      tr.innerHTML = `
        <td style="font-weight:700">${r.item_name}</td>
        <td>${r.user_name}</td>
        <td class="mono">${fmt(r.checkout_time)}</td>
        <td class="mono">${r.return_time ? fmt(r.return_time) : '<span class="badge ba">Out</span>'}</td>
        <td>${r.rating ? r.rating + '/10' : '—'}</td>
        <td style="max-width:180px;font-size:12px;color:var(--muted)">${r.condition_report || '—'}</td>
      `
      tbody.appendChild(tr)
    })
    if (!rows.length) tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px">No transactions yet</td></tr>'
  } catch(e) {}
}

async function loadAdminUsers() {
  _aUsers = await fetch('/api/users').then(r => r.json())
  renderAUsers(_aUsers)
}
function renderAUsers(users) {
  const tbody = $('au-tbody')
  tbody.innerHTML = ''
  users.forEach(u => {
    const renting = u.rented_item_uid ? '<span class="badge ba">Yes</span>' : '<span class="badge bm">No</span>'
    const tr = document.createElement('tr')
    tr.innerHTML = `
      <td style="font-weight:700">${u.name}</td>
      <td class="mono">${u.email || '—'}</td>
      <td><span class="badge ${u.role==='admin'?'bb':'bm'}">${u.role||'student'}</span></td>
      <td class="mono">${u.nfc_id}</td>
      <td>${renting}</td>
      <td style="display:flex;gap:6px;flex-wrap:wrap">
        <button class="btn btn-danger btn-sm" onclick="adminDelFace('${u.nfc_id}')">Del Face</button>
        ${u.role!=='admin'?`<button class="btn btn-danger btn-sm" onclick="adminDelUser('${u.nfc_id}','${u.name}')">Delete</button>`:''}
      </td>
    `
    tbody.appendChild(tr)
  })
  if (!users.length) tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px">No users</td></tr>'
}
function filterAUsers(q) {
  q = q.toLowerCase()
  renderAUsers(_aUsers.filter(u => u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q)))
}
async function adminDelUser(uid, name) {
  if (!confirm(`Delete user "${name}"? Their transaction history will be preserved.`)) return
  const r = await fetch(`/api/user/${uid}`, {method:'DELETE'}).then(r=>r.json())
  if (r.success) { toast('User deleted'); loadAdminUsers() }
  else toast(r.error || 'Failed', false)
}
async function adminDelFace(uid) {
  if (!confirm('Delete face data for this user?')) return
  const r = await fetch(`/api/user/${uid}/face`, {method:'DELETE'}).then(r=>r.json())
  if (r.success) toast('Face data deleted')
  else toast(r.error || 'Failed', false)
}

async function loadAdminEquip() {
  _aEquip = await fetch('/api/equipment').then(r => r.json())
  renderAEquip(_aEquip)
}
function renderAEquip(items) {
  const tbody = $('ae-tbody')
  tbody.innerHTML = ''
  items.forEach(i => {
    const tr = document.createElement('tr')
    tr.innerHTML = `
      <td style="font-weight:700">${i.name}</td>
      <td><span class="badge bm">${i.category||'—'}</span></td>
      <td><span class="badge ${i.status==='available'?'bg':'br'}">${i.status==='available'?'Available':'Rented'}</span></td>
      <td class="mono">${i.nfc_tag}</td>
      <td>${i.avg_rating > 0 ? Number(i.avg_rating).toFixed(1)+'/10' : '—'}</td>
      <td class="mono">${i.rating_count||0}</td>
      <td>${i.status==='available'?`<button class="btn btn-danger btn-sm" onclick="adminDelEquip('${i.nfc_tag}','${i.name}')">Delete</button>`:'<span style="color:var(--muted);font-size:12px">In use</span>'}</td>
    `
    tbody.appendChild(tr)
  })
  if (!items.length) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:20px">No equipment</td></tr>'
}
function filterAEquip(q) {
  q = q.toLowerCase()
  renderAEquip(_aEquip.filter(i => i.name?.toLowerCase().includes(q) || i.category?.toLowerCase().includes(q)))
}
function openAddEquip() {
  $('add-equip-form').style.display = 'block'
  $('ae-tag').value = ''
  $('ae-name').value = ''
  $('ae-cat').value = ''
  $('ae-scan-hint').textContent = '📡 Scan the item\'s NFC tag on the reader to autofill the ID, or type it manually below.'
  $('ae-scan-hint').style.background = 'rgba(245,166,35,.08)'
  $('ae-scan-hint').style.borderColor = 'rgba(245,166,35,.2)'
  $('ae-scan-hint').style.color = 'var(--amber)'
  startEquipFormPoll()
}
function closeAddEquip() {
  $('add-equip-form').style.display = 'none'
  stopEquipFormPoll()
}
async function submitAddEquip() {
  const body = {nfc_tag: $('ae-tag').value.trim(), name: $('ae-name').value.trim(), category: $('ae-cat').value.trim()}
  if (!body.nfc_tag || !body.name) { toast('NFC tag and name required', false); return }
  const r = await fetch('/api/equipment', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json())
  if (r.success) { toast('Equipment added'); closeAddEquip(); loadAdminEquip() }
  else toast(r.error || 'Failed', false)
}
async function adminDelEquip(tag, name) {
  if (!confirm(`Delete "${name}"? Rental history will be preserved.`)) return
  const r = await fetch(`/api/equipment/${tag}`, {method:'DELETE'}).then(r=>r.json())
  if (r.success) { toast('Deleted'); loadAdminEquip() }
  else toast(r.error || 'Failed', false)
}

async function loadAdminHistory() {
  _aHist = await fetch('/api/history').then(r => r.json())
  renderAHistory(_aHist)
}
function renderAHistory(rows) {
  const tbody = $('ah-tbody')
  tbody.innerHTML = ''
  rows.forEach(r => {
    const tr = document.createElement('tr')
    tr.innerHTML = `
      <td style="font-weight:700">${r.item_name}</td>
      <td><span class="badge bm">${r.item_category||'—'}</span></td>
      <td>${r.user_name}</td>
      <td class="mono">${fmt(r.checkout_time)}</td>
      <td class="mono">${r.return_time?fmt(r.return_time):'<span class="badge ba">Out</span>'}</td>
      <td>${r.rating?r.rating+'/10':'—'}</td>
      <td style="max-width:160px;font-size:12px;color:var(--muted)">${r.condition_report||'—'}</td>
    `
    tbody.appendChild(tr)
  })
  if (!rows.length) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:20px">No history</td></tr>'
}
function filterAHistory(q) {
  q = q.toLowerCase()
  renderAHistory(_aHist.filter(r => r.item_name?.toLowerCase().includes(q) || r.user_name?.toLowerCase().includes(q)))
}

async function loadEmailUsers() {
  const users = await fetch('/api/users').then(r => r.json())
  const sel = $('em-user-select')
  sel.innerHTML = '<option value="">— Select a user —</option>'
  users.filter(u => u.role !== 'admin').forEach(u => {
    const opt = document.createElement('option')
    opt.value = JSON.stringify({name: u.name, email: u.email, item: u.rented_item_uid || ''})
    opt.textContent = u.name + (u.rented_item_uid ? ' (has item out)' : '')
    sel.appendChild(opt)
  })
}

async function autofillReminderUser() {
  const val = $('em-user-select').value
  if (!val) return
  const data = JSON.parse(val)
  $('em-name').value = data.name
  $('em-email').value = data.email
  //if they have an item look it up for the name
  if (data.item) {
    const eq = await fetch(`/api/equipment/${data.item}`).then(r => r.json())
    $('em-item').value = eq.found ? eq.item.name : data.item
  } else {
    $('em-item').value = ''
  }
}

async function loadHot() {
  const data = await fetch('/api/hot-items').then(r => r.json())
  const max = Math.max(...data.map(d => d.total_rentals), 1)
  const hotIds = data.slice(0, 3).map(d => d.name)
  $('hot-bars').innerHTML = data.slice(0, 10).map(item => `
    <div class="hot-row">
      <div class="hot-name">${item.name} ${hotIds.includes(item.name) && item.total_rentals > 0 ? '<span class="badge ba" style="font-size:10px">🔥 Hot</span>' : ''}</div>
      <div class="hot-bar-bg"><div class="hot-bar" style="width:${Math.round(item.total_rentals/max*100)}%"></div></div>
      <div class="hot-ct">${item.total_rentals} rentals</div>
    </div>
  `).join('') || '<div style="color:var(--muted);font-size:13px">No rental data yet</div>'
  const tbody = $('hot-tbody')
  tbody.innerHTML = data.map(i => `
    <tr>
      <td style="font-weight:700">${i.name} ${hotIds.includes(i.name) && i.total_rentals > 0 ? '🔥' : ''}</td>
      <td><span class="badge bm">${i.category||'—'}</span></td>
      <td class="mono">${i.total_rentals}</td>
      <td>${i.avg_rating > 0 ? Number(i.avg_rating).toFixed(1)+'/10' : '—'}</td>
      <td><span class="badge ${i.status==='available'?'bg':'br'}">${i.status}</span></td>
    </tr>
  `).join('') || '<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px">No data</td></tr>'
}

async function sendReminder() {
  const body = {user_name: $('em-name').value.trim(), email: $('em-email').value.trim(), item_name: $('em-item').value.trim()}
  if (!body.email || !body.user_name || !body.item_name) { toast('Fill all fields', false); return }
  const r = await fetch('/api/email/reminder', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json())
  if (r.success) toast('Reminder sent!')
  else toast('Failed to send', false)
}
async function sendManual() {
  const body = {to_email: $('cm-to').value.trim(), subject: $('cm-sub').value.trim(), body: $('cm-body').value.trim()}
  if (!body.to_email || !body.body) { toast('Email and message required', false); return }
  const r = await fetch('/api/email/manual', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json())
  if (r.success) toast('Email sent!')
  else toast('Failed', false)
}

function fmt(dt) {
  if (!dt) return '—'
  const d = new Date(dt)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})
}

startPoll()
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


if __name__ == "__main__":
    print("NFC Lend UI running at http://localhost:8080")
    print("Make sure face_server.py is running on port 5001")
    app.run(host="0.0.0.0", port=8080, debug=False)
