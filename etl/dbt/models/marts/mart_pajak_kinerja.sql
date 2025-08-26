with f as (
  select date_trunc('month', tanggal) as periode, jenis_pajak, sum(nilai) as nilai
  from analytics.stg_realisasi_pajak
  group by 1,2
)
select * from f
