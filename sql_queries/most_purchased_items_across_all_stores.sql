select replace(product_code, '.0', '') as product_code, product_description, sum(qty) as qty
from sales
where sale_type = 'Sale'
and item_ring_type = 'ITEM'
and length(replace(product_code::text, '.0', '')) > 3
group by product_code, product_description
order by sum(qty) desc
limit 50
