-- The detail list must contain exactly as many rows as the summary counts.
select d.n as detail_rows, s.n as summary_rows
from (select count(*) as n from {{ ref('dq_rejected_rows') }}) d
cross join (select sum(rejected_rows) as n from {{ ref('dq_rejections_summary') }}) s
where d.n <> s.n
