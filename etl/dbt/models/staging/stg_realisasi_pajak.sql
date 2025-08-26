with src as (
  select * from raw.realisasi_pajak
)
select
  cast(tanggal as date) as tanggal,
  jenis_pajak,
  nilai::numeric as nilai
from src
