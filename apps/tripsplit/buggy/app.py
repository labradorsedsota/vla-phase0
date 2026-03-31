"""TripSplit — 旅行分账记账本"""
import json
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATABASE"] = "tripsplit.db"

CATEGORIES = ["交通", "住宿", "餐饮", "门票", "购物", "其他"]
SPLIT_MODES = {"equal": "均摊", "ratio": "按比例", "custom": "自定义金额"}


# ── DB helpers ──────────────────────────────────────────────


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS trip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            members TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS expense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL REFERENCES trip(id) ON DELETE CASCADE,
            category TEXT NOT NULL DEFAULT '其他',
            amount INTEGER NOT NULL DEFAULT 0,
            date TEXT NOT NULL,
            payer TEXT NOT NULL,
            participants TEXT NOT NULL DEFAULT '[]',
            split_mode TEXT NOT NULL DEFAULT 'equal',
            split_detail TEXT NOT NULL DEFAULT '{}',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        """
    )
    db.commit()


with app.app_context():
    init_db()


# ── Helpers ─────────────────────────────────────────────────


def yuan(fen: int) -> str:
    """分 → 元，保留两位"""
    return f"{fen / 100:.2f}"


def parse_yuan(s: str) -> int:
    """元字符串 → 分（整数）"""
    try:
        return round(float(s) * 100)
    except (ValueError, TypeError):
        return 0


app.jinja_env.filters["yuan"] = yuan
app.jinja_env.globals["categories"] = CATEGORIES
app.jinja_env.globals["split_modes"] = SPLIT_MODES


def get_trip_or_404(trip_id):
    row = get_db().execute("SELECT * FROM trip WHERE id=?", (trip_id,)).fetchone()
    if row is None:
        from flask import abort
        abort(404)
    return row


def trip_total(trip_id):
    row = get_db().execute(
        "SELECT COALESCE(SUM(amount),0) AS total FROM expense WHERE trip_id=?",
        (trip_id,),
    ).fetchone()
    return row["total"]


def trip_expense_count(trip_id):
    row = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM expense WHERE trip_id=?", (trip_id,)
    ).fetchone()
    return row["cnt"]


# ── Page 1: 旅行管理（首页） ────────────────────────────────


@app.route("/")
def index():
    db = get_db()
    trips = db.execute("SELECT * FROM trip ORDER BY created_at DESC").fetchall()
    enriched = []
    for t in trips:
        members = json.loads(t["members"])
        total = trip_total(t["id"])
        enriched.append(
            {
                "id": t["id"],
                "name": t["name"],
                "start_date": t["start_date"],
                "end_date": t["end_date"],
                "member_count": len(members),
                "total": total,
            }
        )
    return render_template("index.html", trips=enriched)


@app.route("/trip/create", methods=["POST"])
def create_trip():
    name = request.form.get("name", "").strip()
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    members_raw = request.form.get("members", "")
    members = [m.strip() for m in members_raw.split(",") if m.strip()]
    if not name or not members:
        return redirect(url_for("index"))
    db = get_db()
    db.execute(
        "INSERT INTO trip (name, start_date, end_date, members) VALUES (?,?,?,?)",
        (name, start_date, end_date, json.dumps(members, ensure_ascii=False)),
    )
    # BUG: 漏了 db.commit()，数据不会持久化（WAL 模式下连接关闭时丢失）
    return redirect(url_for("index"))


# ── Page 2: 记一笔 ─────────────────────────────────────────


@app.route("/trip/<int:trip_id>/add", methods=["GET", "POST"])
def add_expense(trip_id):
    trip = get_trip_or_404(trip_id)
    members = json.loads(trip["members"])

    if request.method == "POST":
        category = request.form.get("category", "其他")
        amount = parse_yuan(request.form.get("amount", "0"))
        exp_date = request.form.get("date", str(date.today()))
        payer = request.form.get("payer", "")
        participants = request.form.getlist("participants")
        split_mode = request.form.get("split_mode", "equal")
        note = request.form.get("note", "").strip()

        # Build split_detail
        split_detail = {}
        if split_mode == "ratio":
            ratios = {}
            for p in participants:
                r = request.form.get(f"ratio_{p}", "1")
                try:
                    ratios[p] = float(r)
                except ValueError:
                    ratios[p] = 1.0
            total_ratio = sum(ratios.values()) or 1
            for p in participants:
                share_fen = round(amount * ratios[p] / total_ratio)
                split_detail[p] = share_fen
            # 尾差修正
            diff = amount - sum(split_detail.values())
            if diff and participants:
                split_detail[participants[0]] += diff
        elif split_mode == "custom":
            for p in participants:
                split_detail[p] = parse_yuan(request.form.get(f"custom_{p}", "0"))
        else:
            # equal
            if participants:
                base = amount // len(participants)
                remainder = amount % len(participants)
                for i, p in enumerate(participants):
                    split_detail[p] = base + (1 if i < remainder else 0)

        if not participants:
            participants = members

        db = get_db()
        db.execute(
            """INSERT INTO expense
               (trip_id, category, amount, date, payer, participants,
                split_mode, split_detail, note)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                trip_id,
                category,
                amount,
                exp_date,
                payer,
                json.dumps(participants, ensure_ascii=False),
                split_mode,
                json.dumps(split_detail, ensure_ascii=False),
                note,
            ),
        )
        db.commit()
        return redirect(url_for("expense_list", trip_id=trip_id))

    return render_template(
        "add_expense.html",
        trip=trip,
        members=members,
        today=str(date.today()),
    )


# ── Page 3: 账单明细 ───────────────────────────────────────


@app.route("/trip/<int:trip_id>/list")
def expense_list(trip_id):
    trip = get_trip_or_404(trip_id)
    db = get_db()
    category_filter = request.args.get("category", "")

    if category_filter:
        expenses = db.execute(
            "SELECT * FROM expense WHERE trip_id=? AND category=? ORDER BY date ASC, id ASC",
            (trip_id, category_filter),
        ).fetchall()
    else:
        expenses = db.execute(
            "SELECT * FROM expense WHERE trip_id=? ORDER BY date ASC, id ASC",
            (trip_id,),
        ).fetchall()

    total = sum(e["amount"] for e in expenses)
    count = len(expenses)

    return render_template(
        "expense_list.html",
        trip=trip,
        expenses=expenses,
        total=total,
        count=count,
        category_filter=category_filter,
    )


@app.route("/trip/<int:trip_id>/expense/<int:exp_id>/edit", methods=["GET", "POST"])
def edit_expense(trip_id, exp_id):
    trip = get_trip_or_404(trip_id)
    members = json.loads(trip["members"])
    db = get_db()
    expense = db.execute("SELECT * FROM expense WHERE id=? AND trip_id=?", (exp_id, trip_id)).fetchone()
    if expense is None:
        from flask import abort
        abort(404)

    if request.method == "POST":
        category = request.form.get("category", "其他")
        amount = parse_yuan(request.form.get("amount", "0"))
        exp_date = request.form.get("date", str(date.today()))
        payer = request.form.get("payer", "")
        participants = request.form.getlist("participants")
        split_mode = request.form.get("split_mode", "equal")
        note = request.form.get("note", "").strip()

        split_detail = {}
        if split_mode == "ratio":
            ratios = {}
            for p in participants:
                r = request.form.get(f"ratio_{p}", "1")
                try:
                    ratios[p] = float(r)
                except ValueError:
                    ratios[p] = 1.0
            total_ratio = sum(ratios.values()) or 1
            for p in participants:
                share_fen = round(amount * ratios[p] / total_ratio)
                split_detail[p] = share_fen
            diff = amount - sum(split_detail.values())
            if diff and participants:
                split_detail[participants[0]] += diff
        elif split_mode == "custom":
            for p in participants:
                split_detail[p] = parse_yuan(request.form.get(f"custom_{p}", "0"))
        else:
            if participants:
                base = amount // len(participants)
                remainder = amount % len(participants)
                for i, p in enumerate(participants):
                    split_detail[p] = base + (1 if i < remainder else 0)

        db.execute(
            """UPDATE expense SET category=?, amount=?, date=?, payer=?,
               participants=?, split_mode=?, split_detail=?, note=?
               WHERE id=? AND trip_id=?""",
            (
                category, amount, exp_date, payer,
                json.dumps(participants, ensure_ascii=False),
                split_mode,
                json.dumps(split_detail, ensure_ascii=False),
                note, exp_id, trip_id,
            ),
        )
        db.commit()
        return redirect(url_for("expense_list", trip_id=trip_id))

    return render_template(
        "edit_expense.html",
        trip=trip,
        expense=expense,
        members=members,
        today=str(date.today()),
    )


@app.route("/trip/<int:trip_id>/expense/<int:exp_id>/delete", methods=["POST"])
def delete_expense(trip_id, exp_id):
    db = get_db()
    db.execute("DELETE FROM expense WHERE id=? AND trip_id=?", (exp_id, trip_id))
    db.commit()
    return redirect(url_for("expense_list", trip_id=trip_id))


# ── Page 4: 分账结算 ───────────────────────────────────────


@app.route("/trip/<int:trip_id>/settle")
def settle(trip_id):
    trip = get_trip_or_404(trip_id)
    members = json.loads(trip["members"])
    db = get_db()
    expenses = db.execute(
        "SELECT * FROM expense WHERE trip_id=?", (trip_id,)
    ).fetchall()

    # 每人实际支付 & 应承担
    paid = {m: 0 for m in members}
    owed = {m: 0 for m in members}
    category_totals = {}

    for e in expenses:
        payer = e["payer"]
        amount = e["amount"]
        cat = e["category"]
        split_detail = json.loads(e["split_detail"])

        if payer in paid:
            paid[payer] += amount

        category_totals[cat] = category_totals.get(cat, 0) + amount

        for person, share in split_detail.items():
            if person in owed:
                owed[person] += share

    # 差额：正数=应收，负数=应付（BUG: 反了，应该是 paid - owed，这里写成 owed - paid）
    balance = {m: owed[m] - paid[m] for m in members}

    # 贪心法最少转账
    settlements = _min_transfers(balance)

    grand_total = sum(e["amount"] for e in expenses)

    # 个人汇总
    person_summary = []
    for m in members:
        person_summary.append(
            {
                "name": m,
                "paid": paid[m],
                "owed": owed[m],
                "balance": balance[m],
            }
        )

    # 分类统计
    cat_stats = []
    for cat in CATEGORIES:
        amt = category_totals.get(cat, 0)
        if amt > 0:
            pct = round(amt / grand_total * 100, 1) if grand_total else 0
            cat_stats.append({"category": cat, "amount": amt, "percent": pct})

    return render_template(
        "settle.html",
        trip=trip,
        person_summary=person_summary,
        settlements=settlements,
        grand_total=grand_total,
        cat_stats=cat_stats,
    )


def _min_transfers(balance: dict) -> list:
    """贪心法：最少转账次数结算"""
    # 过滤掉零差额
    debts = []
    for name, bal in balance.items():
        if bal != 0:
            debts.append((name, bal))

    settlements = []
    while debts:
        # 找最大债务人（balance 最负）和最大债权人（balance 最正）
        debts.sort(key=lambda x: x[1])
        debtor_name, debtor_bal = debts[0]  # 最负
        creditor_name, creditor_bal = debts[-1]  # 最正

        if debtor_bal == 0 or creditor_bal == 0:
            break

        transfer = min(-debtor_bal, creditor_bal)
        settlements.append(
            {
                "from": debtor_name,
                "to": creditor_name,
                "amount": transfer,
            }
        )

        # 更新
        new_debts = []
        for name, bal in debts:
            if name == debtor_name:
                bal += transfer
            elif name == creditor_name:
                bal -= transfer
            if bal != 0:
                new_debts.append((name, bal))
        debts = new_debts

    return settlements


# ── Main ────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5555)
