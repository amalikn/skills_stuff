# Unit Economics Calculator

Use segment/cohort economics. Keep observed values separate from assumptions.

## Core formulas

- Contribution margin = revenue - variable delivery/COGS - transaction/usage costs.
- Contribution margin % = contribution margin / revenue.
- CAC = attributable acquisition spend / acquired customers. State attribution scope.
- Gross-margin LTV (simple steady-state) = ARPA × gross margin % / logo churn rate. Use only when churn is sufficiently stable; prefer cohort cash flows otherwise.
- CAC payback months = CAC / monthly contribution margin per new customer.
- NRR = (starting recurring revenue - churn - contraction + expansion) / starting recurring revenue.

## Required checks

1. Define the economic unit: customer, account, transaction, seat, job, token, order, or other value unit.
2. Separate variable COGS from fixed operating expense.
3. Include refunds, discounts, credits, support burden, third-party/API costs, payment fees, and implementation costs when material.
4. Model conservative/base/upside cases.
5. Identify the dominant sensitivity and break-even threshold.
6. Show cash timing when working capital or annual prepayment changes the decision.

Do not apply generic SaaS benchmarks as pass/fail rules without segment/stage evidence.
