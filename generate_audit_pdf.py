"""generate_audit_pdf.py

Reads `fairness_report.json` and writes a short PDF `fairness_audit_summary.pdf`.
Requires reportlab (already in project requirements).
"""
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

IN = 'fairness_report.json'
OUT = 'fairness_audit_summary.pdf'


def summarize_report(r):
    lines = []
    lines.append(f"Overall accuracy: {r.get('overall_accuracy')}")
    lines.append("")
    lines.append('Per-team metrics:')
    for t, m in r.get('per_team', {}).items():
        lines.append(f"  {t}: accuracy={m.get('accuracy'):.3f}, f1_macro={m.get('f1_macro'):.3f}, support={m.get('support')}")
    lines.append("")
    if 'parity' in r:
        p = r['parity']
        lines.append('Parity metrics (manual):')
        for g, v in p.get('group_positive_rate', {}).items():
            lines.append(f"  {g}: positive_rate={v:.3f}")
        lines.append(f"  statistical_parity_difference: {p.get('statistical_parity_difference'):.3f}")
        di = p.get('disparate_impact')
        lines.append(f"  disparate_impact: {di:.3f}" if di is not None else "  disparate_impact: null")

    if 'aif360' in r:
        a = r['aif360']
        lines.append("")
        lines.append('AIF360 metrics:')
        lines.append(f"  statistical_parity_difference: {a.get('statistical_parity_difference')}")
        lines.append(f"  disparate_impact: {a.get('disparate_impact')}")

    return lines


def main():
    with open(IN, 'r', encoding='utf-8') as f:
        r = json.load(f)
    lines = summarize_report(r)

    c = canvas.Canvas(OUT, pagesize=letter)
    w, h = letter
    x = 72
    y = h - 72
    c.setFont('Helvetica-Bold', 14)
    c.drawString(x, y, 'Fairness Audit Summary')
    y -= 28
    c.setFont('Helvetica', 10)
    for line in lines:
        if y < 72:
            c.showPage()
            y = h - 72
            c.setFont('Helvetica', 10)
        c.drawString(x, y, line)
        y -= 14
    c.save()
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
