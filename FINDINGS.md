# Olist Product Analysis — Findings Memo
 
**Dataset:** Olist Brazilian E-Commerce (Kaggle) — 99,441 orders, Sep 2016 – Oct 2018  
**Role framing:** Data analyst embedded in Olist's product team, tasked with diagnosing
why growth stalled and where the customer experience broke down.

---

## Strategic Objective

Why did Olist's growth plateau, and what does the data say the team
should have done differently?

---

## Finding 1 - The Funnel Is Not the Problem

**Surface metric:** 97% of orders are successfully delivered.
By standard e-commerce benchmarks, that is strong.

**What the data actually shows:** Of delivered orders, 91.9% arrived
*early* relative to the estimated delivery date. Olist systematically
padded delivery estimates, creating an artificial "early delivery" signal
that flatters the numbers. The real late delivery rate - orders that
missed even the padded estimate was 6.8%.

**Regional note:** No state fell below 95% delivery completion,
meaning logistics execution was consistent nationally. The funnel
drop-off (the 3% of orders that stalled at approval or carrier stage)
is a payment processing and seller reliability issue, not a last-mile
problem.

**What this means for the product team:** Delivery time is not the
retention lever. Do not invest engineering resources in logistics
optimisation, the fulfilment operation is already performing well
relative to customer expectations. The problem is elsewhere.

---

## Finding 2 - Retention Is Structurally Near Zero

**The number:** Across every acquisition cohort from January 2017
to mid-2018, month-1 retention sits between 0.2% and 1%.
By month 3, it rounds to zero for most cohorts.

**What the retention curve shows:** The average retention curve
drops sharply from 0.34% at month 1 to approximately 0.20%–0.27%
for all subsequent months, where it flatlines. There is no recovery.
No cohort shows a meaningful uptick at any later month. This is not
a timing problem - customers are not returning later. They are not
returning at all.

**What the cohort heatmap confirms:** Every cohort row is uniformly
dark red after column 0. This is not one bad cohort or one bad period.
It is a platform-wide structural pattern with no exceptions across
two years of data.

**The satisfaction paradox:** 38 of 52 product categories have
average review scores above 4.0 out of 5. Customers are satisfied
with their purchases. And they do not come back. This appears
contradictory until you examine the category mix.

**The actual explanation:** Olist's highest-volume categories are
bed/bath (9,167 orders), sports/leisure (7,491), furniture/decor
(6,213), are all durable goods. A customer who buys a bed frame
is satisfied, leaves a 4-star review, and has no reason to return
for years. Satisfaction measures whether the transaction went well.
It does not create a reason to return.

**The strategic miss:** Olist's consumable categories are food (435
orders), drinks (284), pet shop (1,682), are the only ones that
generate natural repeat purchase cycles. Combined they represent
less than 2.5% of total orders. These are exactly the categories
that could have driven retention. They were never scaled.

---

## Finding 3 - The Underinvested High-Value Segment

**The number:** The `computers` category averages $1,252 per order
nearly 8x the platform average of $160 with a review score of 4.24
and only 176 total orders across two years.

**What this means:** There is demonstrated willingness to pay
for high-value electronics on the platform. The category is not
underperforming, it has too few orders to evaluate performance
fairly. It was simply never invested in.

**The contrast:** `watches_gifts` (5,472 orders, $227 avg) and
`small_appliances` (606 orders, $321 avg) both show that
above-average order value is achievable at volume. The category
mix was tilted toward low-AOV, low-frequency goods.

**The freight problem in high-value categories:** `office_furniture`
($264 avg order value, $40.71 avg freight) and
`home_appliances_2` ($510 avg, $44.61 avg freight) both carry
freight costs 2-3x the platform average. High satisfaction scores
mask a logistics cost problem that erodes margin on the exact
categories that generate the most revenue per order.
(Note: These categories require "Heavy/Bulky" shipping which likely explains the cost spike)

---

## Recommendation

If this analysis were presented to Olist's product team in 2018,
the recommendation would be:

**Stop optimising the funnel. It is not broken.**

**Run one test:** Identify the top 500 customers by order value
in the `computers` and `small_appliances` categories.
Send them a targeted campaign for complementary consumable products like
accessories, supplies, anything that creates a second purchase
reason within 60 days. Measure 60-day retention for this group
vs. the platform baseline of ~0.3%.

**The structural fix:** Actively recruit sellers in consumable
categories, food, pet supplies, personal care. Set a target of
10% of total GMV from consumables within 12 months.
Current consumable share is under 2.5%. Even reaching 5%
would meaningfully shift the retention curve.

**The underlying strategic question** the data cannot answer
but raises clearly: did Olist have the seller supply in consumable
categories to scale them, or was the category mix a reflection
of what sellers chose to list? That is the next investigation.

---

## Limitations

- `customer_unique_id` was used throughout retention analysis
  to correctly identify returning customers. `customer_id`
  changes per order and would have made every customer appear new.
- Revenue figures are based on `payment_value` which includes
  freight. True product revenue is slightly lower.
- The dataset ends October 2018. Late cohorts (2018-05 onward)
  have insufficient follow-up time to draw retention conclusions
  beyond month 2. The triangle shape in the cohort table is
  expected, it is not missing data, it is time not yet elapsed.
- Retention analysis covers delivered orders only.
  Canceled and unavailable orders (~1.5% combined) are excluded.