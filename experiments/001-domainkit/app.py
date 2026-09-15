"""
The interface is derived from the same schema as everything else: the
fields/actions rendered per view, and the pre-check gating each action,
both come from the domain definition -- not re-implemented here.
Run `python main.py` first to produce generated_impls.py.
"""
import importlib.util
from types import SimpleNamespace

from flask import Flask, render_template_string, redirect, url_for, abort

from domainkit.schema import load_domain
from domainkit.contracts import eval_expr

domain = load_domain("schema.yaml")

spec = importlib.util.spec_from_file_location("generated_impls", "generated_impls.py")
impls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impls)

# --- tiny in-memory sample data ---
users = {"u1": SimpleNamespace(id="u1", name="Alice"), "u2": SimpleNamespace(id="u2", name="Bob")}
tasks = {
    "t1": SimpleNamespace(id="t1", title="Write schema", done=False, owner=None),
    "t2": SimpleNamespace(id="t2", title="Verify contracts", done=False, owner=users["u1"]),
}

app = Flask(__name__)

TEMPLATE = """
<h1>{{ view.name }}</h1>
<table border=1 cellpadding=6>
<tr>{% for f in view.fields %}<th>{{ f }}</th>{% endfor %}<th>actions</th></tr>
{% for row in rows %}
<tr>
  {% for f in view.fields %}<td>{{ getattr(row, f) }}</td>{% endfor %}
  <td>
    {% for a in view.actions %}
      <form style="display:inline" method="post" action="/action/{{ a }}/{{ row.id }}">
        <button>{{ a }}</button>
      </form>
    {% endfor %}
  </td>
</tr>
{% endfor %}
</table>
"""


@app.route("/")
def index():
    view = domain.views[0]
    return render_template_string(TEMPLATE, view=view, rows=list(tasks.values()), getattr=getattr)


@app.route("/action/<keyword>/<row_id>", methods=["POST"])
def action(keyword, row_id):
    kdef = domain.keywords.get(keyword)
    if kdef is None:
        abort(404)
    subject = tasks.get(row_id)
    if subject is None:
        abort(404)
    obj = next(iter(users.values())) if kdef.object else None  # demo only: grabs a sample user

    if not eval_expr(kdef.contract.requires, subject, obj):
        return f"Rejected: '{keyword}' precondition not met for {row_id}", 400

    fn = getattr(impls, keyword)
    fn(subject, obj) if kdef.object else fn(subject)

    if not eval_expr(kdef.contract.ensures, subject, obj):
        return "Internal error: postcondition violated after a verified action ran -- this should be unreachable", 500

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
