#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════
# 🖥️ Ultimate Engine License Server
# ═══════════════════════════════════════════════════════════════════
from flask import Flask, jsonify, request, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "licenses.json")
ADMIN_PASSWORD = "admin1234"  # ← غيّر كلمة السر!

# ═══════════════════════════════════════════════════════════════════
# 📂 قراءة / كتابة قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"version": 1, "keys": {}, "banned_devices": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    data["updated"] = int(datetime.now().timestamp())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════════════════════════
# 📖 Endpoint للعبة - تسحب التراخيص
# ═══════════════════════════════════════════════════════════════════
@app.route("/licenses.json", methods=["GET"])
def get_licenses():
    return jsonify(load_data())

# ═══════════════════════════════════════════════════════════════════
# 📊 لوحة التحكم - الصفحة الرئيسية
# ═══════════════════════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def dashboard():
    return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم Ultimate Engine</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #eee;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #0ff; margin-bottom: 20px; text-align: center; }
        .card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(0,255,255,0.3);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h2 { color: #0ff; margin-bottom: 15px; font-size: 18px; }
        input, select, button, textarea {
            background: #0a0a1a;
            border: 1px solid #0ff;
            color: #eee;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            box-shadow: 0 0 10px #0ff;
        }
        button {
            background: #0ff;
            color: #000;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        button:hover { background: #0cc; transform: scale(1.02); }
        button.danger { background: #f44; color: #fff; }
        button.danger:hover { background: #d22; }
        button.success { background: #4f4; color: #000; }
        .row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
        .row > * { flex: 1; min-width: 150px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td {
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid rgba(0,255,255,0.2);
        }
        th { color: #0ff; font-weight: bold; }
        tr:hover { background: rgba(0,255,255,0.05); }
        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge.active { background: #4f4; color: #000; }
        .badge.banned { background: #f44; color: #fff; }
        .badge.expired { background: #888; color: #fff; }
        .device-list {
            max-height: 100px;
            overflow-y: auto;
            font-size: 12px;
            color: #8ff;
        }
        .device-item {
            padding: 3px 5px;
            background: rgba(0,255,255,0.1);
            border-radius: 4px;
            margin: 2px 0;
            display: flex;
            justify-content: space-between;
        }
        .device-item button {
            padding: 2px 8px;
            font-size: 10px;
            background: #f44;
            color: #fff;
        }
        #msg {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
            font-weight: bold;
        }
        #msg.success { background: #4f4; color: #000; display: block; }
        #msg.error { background: #f44; color: #fff; display: block; }
    </style>
</head>
<body>
<div class="container">
    <h1>🎯 لوحة تحكم Ultimate Engine</h1>

    <div id="msg"></div>

    <!-- إضافة كود جديد -->
    <div class="card">
        <h2>➕ إضافة كود جديد</h2>
        <div class="row">
            <input id="newKey" placeholder="الكود (مثلاً: ABUZAIN_NEW)" />
            <input id="newDuration" type="number" placeholder="المدة بالساعات" value="48" />
            <input id="newMaxDev" type="number" placeholder="عدد الأجهزة" value="3" />
            <input id="newNote" placeholder="ملاحظة (اختياري)" />
            <button onclick="addKey()">➕ إضافة</button>
        </div>
    </div>

    <!-- قائمة الأكواد -->
    <div class="card">
        <h2>📋 الأكواد المسجلة</h2>
        <table id="keysTable">
            <thead>
                <tr>
                    <th>الكود</th>
                    <th>الحالة</th>
                    <th>المدة</th>
                    <th>الأجهزة</th>
                    <th>ملاحظة</th>
                    <th>إجراءات</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <!-- الأجهزة المحظورة -->
    <div class="card">
        <h2>🚫 الأجهزة المحظورة</h2>
        <div class="row">
            <input id="banDevice" placeholder="معرف الجهاز" />
            <button onclick="banDevice()" class="danger">🚫 حظر</button>
        </div>
        <div id="bannedList"></div>
    </div>
</div>

<script>
let PASSWORD = prompt("🔐 أدخل كلمة السر:", "");
if (!PASSWORD) { PASSWORD = ""; }

const API = "/api";

async function apiCall(method, path, body) {
    const opts = {
        method: method,
        headers: { "X-Password": PASSWORD, "Content-Type": "application/json" }
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "فشل الطلب");
    }
    return res.json();
}

function showMsg(text, type) {
    const el = document.getElementById("msg");
    el.textContent = text;
    el.className = type;
    setTimeout(() => { el.style.display = "none"; }, 3000);
}

async function loadKeys() {
    try {
        const data = await apiCall("GET", "/keys");
        const tbody = document.querySelector("#keysTable tbody");
        tbody.innerHTML = "";
        
        for (const [key, info] of Object.entries(data.keys || {})) {
            const devices = info.devices || [];
            const maxDev = info.max_devices || 1;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${key}</strong></td>
                <td><span class="badge ${info.status}">${info.status}</span></td>
                <td>${info.duration_hours} ساعة</td>
                <td>
                    <strong>${devices.length} / ${maxDev}</strong>
                    <div class="device-list">
                        ${devices.map(d => `
                            <div class="device-item">
                                <span>${d.substring(0, 12)}...</span>
                                <button onclick="removeDevice('${key}', '${d}')">✖</button>
                            </div>
                        `).join("") || "لا يوجد"}
                    </div>
                </td>
                <td>${info.note || "-"}</td>
                <td>
                    <button onclick="toggleStatus('${key}', '${info.status}')" class="${info.status === 'active' ? 'danger' : 'success'}">
                        ${info.status === 'active' ? "🚫 حظر" : "✅ تفعيل"}
                    </button>
                    <button onclick="deleteKey('${key}')" class="danger">🗑️</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function addKey() {
    const key = document.getElementById("newKey").value.trim();
    const duration = parseInt(document.getElementById("newDuration").value) || 48;
    const maxDev = parseInt(document.getElementById("newMaxDev").value) || 3;
    const note = document.getElementById("newNote").value.trim();
    
    if (!key) return showMsg("❌ أدخل الكود", "error");
    
    try {
        await apiCall("POST", "/keys", { key, duration_hours: duration, max_devices: maxDev, note });
        showMsg("✅ تم إضافة الكود", "success");
        document.getElementById("newKey").value = "";
        document.getElementById("newNote").value = "";
        loadKeys();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function toggleStatus(key, currentStatus) {
    const newStatus = currentStatus === "active" ? "banned" : "active";
    try {
        await apiCall("PATCH", "/keys/" + key, { status: newStatus });
        showMsg("✅ تم تحديث الحالة", "success");
        loadKeys();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function deleteKey(key) {
    if (!confirm(`متأكد من حذف الكود "${key}"؟`)) return;
    try {
        await apiCall("DELETE", "/keys/" + key);
        showMsg("✅ تم حذف الكود", "success");
        loadKeys();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function removeDevice(key, device) {
    try {
        await apiCall("DELETE", `/keys/${key}/devices/${device}`);
        showMsg("✅ تم إزالة الجهاز", "success");
        loadKeys();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function banDevice() {
    const dev = document.getElementById("banDevice").value.trim();
    if (!dev) return;
    try {
        await apiCall("POST", "/banned", { device: dev });
        showMsg("✅ تم حظر الجهاز", "success");
        document.getElementById("banDevice").value = "";
        loadBanned();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

async function loadBanned() {
    try {
        const data = await apiCall("GET", "/banned");
        const el = document.getElementById("bannedList");
        el.innerHTML = (data.devices || []).map(d => `
            <div class="device-item">
                <span>${d}</span>
                <button onclick="unbanDevice('${d}')">✖ إزالة</button>
            </div>
        `).join("") || "لا يوجد";
    } catch (e) {
        console.error(e);
    }
}

async function unbanDevice(dev) {
    try {
        await apiCall("DELETE", "/banned/" + dev);
        showMsg("✅ تم إلغاء الحظر", "success");
        loadBanned();
    } catch (e) {
        showMsg("❌ " + e.message, "error");
    }
}

// تحميل أولي
loadKeys();
loadBanned();
setInterval(loadKeys, 10000);
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════
# 🔐 تحقق كلمة السر
# ═══════════════════════════════════════════════════════════════════
def check_auth():
    return request.headers.get("X-Password") == ADMIN_PASSWORD

# ═══════════════════════════════════════════════════════════════════
# 📊 API Endpoints
# ═══════════════════════════════════════════════════════════════════
@app.route("/api/keys", methods=["GET"])
def api_get_keys():
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    return jsonify(load_data())

@app.route("/api/keys", methods=["POST"])
def api_add_key():
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    body = request.get_json() or {}
    key = body.get("key", "").strip()
    if not key: return jsonify({"error": "أدخل الكود"}), 400
    
    data = load_data()
    if key in data["keys"]:
        return jsonify({"error": "الكود موجود مسبقًا"}), 400
    
    data["keys"][key] = {
        "status": "active",
        "duration_hours": int(body.get("duration_hours", 48)),
        "max_devices": int(body.get("max_devices", 3)),
        "devices": [],
        "note": body.get("note", ""),
        "created_at": int(datetime.now().timestamp())
    }
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/keys/<key>", methods=["PATCH"])
def api_update_key(key):
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    data = load_data()
    if key not in data["keys"]:
        return jsonify({"error": "الكود مش موجود"}), 404
    
    body = request.get_json() or {}
    if "status" in body: data["keys"][key]["status"] = body["status"]
    if "duration_hours" in body: data["keys"][key]["duration_hours"] = int(body["duration_hours"])
    if "max_devices" in body: data["keys"][key]["max_devices"] = int(body["max_devices"])
    if "note" in body: data["keys"][key]["note"] = body["note"]
    
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/keys/<key>", methods=["DELETE"])
def api_delete_key(key):
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    data = load_data()
    if key in data["keys"]:
        del data["keys"][key]
        save_data(data)
    return jsonify({"ok": True})

@app.route("/api/keys/<key>/devices/<device>", methods=["DELETE"])
def api_remove_device(key, device):
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    data = load_data()
    if key in data["keys"]:
        devices = data["keys"][key].get("devices", [])
        data["keys"][key]["devices"] = [d for d in devices if d != device]
        save_data(data)
    return jsonify({"ok": True})

@app.route("/api/banned", methods=["GET"])
def api_get_banned():
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    data = load_data()
    return jsonify({"devices": data.get("banned_devices", [])})

@app.route("/api/banned", methods=["POST"])
def api_ban_device():
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    body = request.get_json() or {}
    dev = body.get("device", "").strip()
    if not dev: return jsonify({"error": "أدخل معرف الجهاز"}), 400
    
    data = load_data()
    if "banned_devices" not in data: data["banned_devices"] = []
    if dev not in data["banned_devices"]:
        data["banned_devices"].append(dev)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/banned/<device>", methods=["DELETE"])
def api_unban_device(device):
    if not check_auth(): return jsonify({"error": "كلمة السر غلط"}), 401
    data = load_data()
    if "banned_devices" in data:
        data["banned_devices"] = [d for d in data["banned_devices"] if d != device]
    save_data(data)
    return jsonify({"ok": True})

# ═══════════════════════════════════════════════════════════════════
# 🚀 التشغيل
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import socket
    # اطبع عنوان الـ IP المحلي
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    print("═" * 60)
    print("🖥️  Ultimate Engine License Server")
    print("═" * 60)
    print(f"📡 عنوان LAN:   http://{local_ip}:5000")
    print(f"💻 عنوان محلي:  http://127.0.0.1:5000")
    print(f"🔑 كلمة السر:   {ADMIN_PASSWORD}")
    print("═" * 60)
    print("اضغط Ctrl+C للإيقاف")
    print("═" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
