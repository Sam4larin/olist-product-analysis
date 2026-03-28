-- Segment Performance Comparison
-- Business Question: Which product category or payment type
-- performs significantly above or below platform average,
-- and what should the product team do about it?

WITH order_base AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        c.customer_state,

        -- Payment info
        p.payment_type,
        p.payment_installments,
        p.payment_value,

        -- Review score (null if no review left)
        r.review_score,

        -- Product category (translated to English)
        COALESCE(t.product_category_name_english, 'unknown') AS category_english,

        -- Item-level price and freight
        i.price,
        i.freight_value

    FROM read_csv_auto('{orders_path}') o
    LEFT JOIN read_csv_auto('{customers_path}') c
        ON o.customer_id = c.customer_id
    LEFT JOIN read_csv_auto('{payments_path}') p
        ON o.order_id = p.order_id
        AND p.payment_sequential = 1  -- take only the primary payment row
    LEFT JOIN read_csv_auto('{reviews_path}') r
        ON o.order_id = r.order_id
    LEFT JOIN read_csv_auto('{items_path}') i
        ON o.order_id = i.order_id
        AND i.order_item_id = 1       -- take only the first item per order
    LEFT JOIN read_csv_auto('{products_path}') pr
        ON i.product_id = pr.product_id
    LEFT JOIN read_csv_auto('{translations_path}') t
        ON pr.product_category_name = t.product_category_name

    WHERE o.order_status = 'delivered'
),

-- Platform-wide averages (used to flag above/below average segments)
platform_avg AS (
    SELECT
        ROUND(AVG(payment_value), 2)    AS avg_order_value,
        ROUND(AVG(review_score), 2)     AS avg_review_score,
        ROUND(AVG(freight_value), 2)    AS avg_freight_value
    FROM order_base
    WHERE payment_value IS NOT NULL
),

-- Category-level performance
category_performance AS (
    SELECT
        b.category_english,
        COUNT(DISTINCT b.order_id)              AS order_count,
        ROUND(AVG(b.payment_value), 2)          AS avg_order_value,
        ROUND(AVG(b.review_score), 2)           AS avg_review_score,
        ROUND(AVG(b.freight_value), 2)          AS avg_freight_value,
        ROUND(AVG(b.payment_installments), 1)   AS avg_installments,

        -- Flag if this category is above platform average order value
        CASE
            WHEN AVG(b.payment_value) > (SELECT avg_order_value FROM platform_avg)
            THEN 'Above Average'
            ELSE 'Below Average'
        END AS vs_platform_order_value,

        CASE
            WHEN AVG(b.review_score) >= 4.0 THEN 'High Satisfaction'
            WHEN AVG(b.review_score) >= 3.0 THEN 'Medium Satisfaction'
            ELSE                                  'Low Satisfaction'
        END AS satisfaction_tier

    FROM order_base b
    GROUP BY b.category_english
    HAVING COUNT(DISTINCT b.order_id) >= 100
),

-- Payment type performance
payment_performance AS (
    SELECT
        payment_type,
        COUNT(DISTINCT order_id)            AS order_count,
        ROUND(AVG(payment_value), 2)        AS avg_order_value,
        ROUND(AVG(review_score), 2)         AS avg_review_score,
        ROUND(AVG(payment_installments), 1) AS avg_installments,
        ROUND(AVG(freight_value), 2)        AS avg_freight_value
    FROM order_base
    WHERE payment_type IS NOT NULL
    GROUP BY payment_type
)

SELECT 'category' AS segment_type,
       category_english AS segment_value,
       order_count,
       avg_order_value,
       avg_review_score,
       avg_freight_value,
       avg_installments,
       vs_platform_order_value,
       satisfaction_tier
FROM category_performance

UNION ALL

SELECT 'payment_type' AS segment_type,
       payment_type AS segment_value,
       order_count,
       avg_order_value,
       avg_review_score,
       avg_freight_value,
       avg_installments,
       NULL AS vs_platform_order_value,
       NULL AS satisfaction_tier
FROM payment_performance

ORDER BY segment_type, order_count DESC;