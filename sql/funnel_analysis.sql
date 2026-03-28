-- Purchase Funnel Drop-off
-- Business Question: At which stage do orders fail to progress,
-- and is the drop-off driven by region or product category?

-- Stage definitions based on timestamp columns:
-- Stage 1: Order placed (order_purchase_timestamp always exists)
-- Stage 2: Order approved (order_approved_at)
-- Stage 3: Handed to carrier (order_delivered_carrier_date)
-- Stage 4: Delivered to customer (order_delivered_customer_date)

WITH order_stages AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        c.customer_state,

        CASE
            WHEN o.order_delivered_customer_date IS NOT NULL
                THEN 'Stage 4: Delivered'
            WHEN o.order_delivered_carrier_date IS NOT NULL
                THEN 'Stage 3: With Carrier'
            WHEN o.order_approved_at IS NOT NULL
                THEN 'Stage 2: Approved'
            ELSE
                'Stage 1: Placed Only'
        END AS furthest_stage,

        -- Was the order delivered late vs the estimate?
        CASE
            WHEN o.order_delivered_customer_date IS NOT NULL
              AND o.order_estimated_delivery_date IS NOT NULL
            THEN
                DATE_DIFF(
                    'day',
                    CAST(o.order_estimated_delivery_date AS DATE),
                    CAST(o.order_delivered_customer_date AS DATE)
                )
            ELSE NULL
        END AS days_late

    FROM read_csv_auto('{orders_path}') o
    LEFT JOIN read_csv_auto('{customers_path}') c
        ON o.customer_id = c.customer_id
),

-- Overall funnel: how many orders reached each stage
funnel_overall AS (
    SELECT
        furthest_stage,
        COUNT(*) AS order_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_orders
    FROM order_stages
    GROUP BY furthest_stage
),

-- Late delivery breakdown: how bad is the logistics problem?
late_delivery AS (
    SELECT
        CASE
            WHEN days_late < 0  THEN 'Early'
            WHEN days_late = 0  THEN 'On Time'
            WHEN days_late <= 7 THEN 'Late: 1-7 days'
            WHEN days_late <= 14 THEN 'Late: 8-14 days'
            ELSE                     'Late: 15+ days'
        END AS delivery_bucket,
        COUNT(*) AS order_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_delivered
    FROM order_stages
    WHERE furthest_stage = 'Stage 4: Delivered'
      AND days_late IS NOT NULL
    GROUP BY delivery_bucket
),

-- Regional drop-off: which states have the worst completion rates?
regional_funnel AS (
    SELECT
        customer_state,
        COUNT(*) AS total_orders,
        COUNT(CASE WHEN furthest_stage = 'Stage 4: Delivered' THEN 1 END)
            AS delivered,
        ROUND(
            100.0 * COUNT(CASE WHEN furthest_stage = 'Stage 4: Delivered' THEN 1 END)
            / COUNT(*), 1
        ) AS pct_delivered,
        ROUND(AVG(CASE WHEN days_late IS NOT NULL THEN days_late END), 1)
            AS avg_days_late
    FROM order_stages
    GROUP BY customer_state
    HAVING COUNT(*) >= 100  -- filter states with too few orders for meaningful %
)

SELECT 'funnel_overall' AS result_set,
       furthest_stage AS dimension,
       order_count,
       pct_of_all_orders AS pct,
       NULL AS avg_days_late
FROM funnel_overall

UNION ALL

SELECT 'late_delivery' AS result_set,
       delivery_bucket AS dimension,
       order_count,
       pct_of_delivered AS pct,
       NULL AS avg_days_late
FROM late_delivery

UNION ALL

SELECT 'regional' AS result_set,
       customer_state AS dimension,
       total_orders AS order_count,
       pct_delivered AS pct,
       avg_days_late
FROM regional_funnel
ORDER BY result_set, order_count DESC;