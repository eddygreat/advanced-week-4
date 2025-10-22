from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

text = (
"AI-driven testing expands coverage by automating test generation, prioritizing scenarios, "
"and continuously exploring edge cases that human testers often miss. Machine learning models "
"can infer application behavior from code, logs, and usage telemetry to synthesize input variations, "
"data permutations, and UI interaction sequences at scale. This increases mutation and path coverage, "
"reduces human bias in test case selection, and identifies flaky or brittle behaviors earlier. "
"AI can also maintain and adapt tests when the UI or APIs evolve, minimizing manual upkeep. "
"Combined with human oversight, AI accelerates regression detection, improves risk-based prioritization, "
"and surfaces regressions across a wider input space than feasible manually — all while enabling "
"developers to focus on high-value exploratory testing and complex scenarios."
)

c = canvas.Canvas('web_app_test_summary.pdf', pagesize=letter)
width, height = letter
c.setFont('Helvetica', 11)
margin = 72
y = height - margin
for line in text.split('. '):
    if not line.strip():
        continue
    c.drawString(margin, y, line.strip() + ('.' if not line.strip().endswith('.') else ''))
    y -= 14
c.save()
print('Created web_app_test_summary.pdf')
