from database import _run_sql
updates = [("widget", 149, 39), ("starter", 299, 69), ("pro", 599, 129), ("multi", 1299, 229)]
for pid, s, m in updates:
    _run_sql("UPDATE plans SET price_setup = {}, price_monthly = {} WHERE id = '{}'".format(s, m, pid))
    print("Updated {}: ${} + ${}/mo".format(pid, s, m))
results = _run_sql("SELECT name, price_setup, price_monthly FROM plans ORDER BY price_setup")
for r in results:
    print("  {}: ${} setup + ${}/mo".format(r["name"], r["price_setup"], r["price_monthly"]))