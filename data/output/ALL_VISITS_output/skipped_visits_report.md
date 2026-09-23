# Skipped Visits Report — CPM-IA ALL_VISITS

**Run date:** 2026-09-23  
**Total input visits:** 997  
**Successfully processed:** 751  
**Skipped:** 246 (empty_xlsx: 169 · duplicate_marker: 77)

---

### Case 1 — xlsx with no data rows (169 visits)

The `_original.xlsx` file for these visits contains **only the Base Marker**:
```
Row 1 (header): ['Marker / Point', 'LF - 1 - c', 'LF - 1 - e', ...]
Row 2 (only):   ['Base Marker',     600,           870,           360, ...]
```
The `_percentage_variation.xlsx` file is correctly empty: the percentage variation is computed as `(marker - Base Marker) / Base Marker × 100`, but if no measurements following the baseline exist, there is nothing to compute.

**Cause:** the visit was initiated (baseline recorded) but the homeopathic markers were never measured — incomplete session.

---

### Case 2 — duplicate marker with conflicting values (77 visits)

The same marker appears **twice** in the data rows with different values, both in the original and in the percentage variation file:
```
'Rock Rose':  [260, 112.5, 316.7, ...]   ← first measurement
'Rock Rose':  [220, 50.0,  766.7, ...]   ← second measurement
```
The duplicate is already present in the source file `_original.xlsx`, so this is not a processing error.

**Cause:** the marker was administered and measured **twice within the same visit** (e.g. two vials of the same product, two different moments in the protocol). Both measurements were recorded separately. The pipeline cannot disambiguate which value to use to build the ordered sequence and raises a `SequenceError`.

---

**In summary:** both cases are **source data quality issues**, not pipeline bugs. The 169 incomplete visits and the 77 visits with double measurements require manual intervention (or a protocol decision on how to handle duplicates — e.g. mean, first value, last value).

---

## List of skipped visits

### Empty xlsx (169 visits)

| visit_id | detail |
|---|---|
| P1021_#2023m05d23-P1021_V18322_FreeProtocol | xlsx file with no data rows |
| P1021_#2023m08d01-P1021_FreeProtocol | xlsx file with no data rows |
| P1047_#2023m08d27-P1047_V18383_FreeProtocol | xlsx file with no data rows |
| P105_#2015m04d28-P105_V16300_FreeProtocol | xlsx file with no data rows |
| P1076_#2023m11d27-P1076_V18469_FreeProtocol | xlsx file with no data rows |
| P1101_#2024m03d22-P1101_V18533_FreeProtocol | xlsx file with no data rows |
| P1105_#2024m04d02-P1105_FreeProtocol | xlsx file with no data rows |
| P1116_#2024m05d24-P1116_V18585_FreeProtocol | xlsx file with no data rows |
| P1144_#2024m10d04-P1144_FreeProtocol | xlsx file with no data rows |
| P1167_#2025m01d20-P1167_FreeProtocol | xlsx file with no data rows |
| P1167_#2025m05d18-P1167_V18858_FreeProtocol | xlsx file with no data rows |
| P1167_#2025m10d05-P1167_FreeProtocol | xlsx file with no data rows |
| P117_#2014m09d05-P117_V16228_FreeProtocol | xlsx file with no data rows |
| P1183_#2025m04d06-P1183_V18832_FreeProtocol | xlsx file with no data rows |
| P1187_#2025m04d16-P1187_V18842_FreeProtocol | xlsx file with no data rows |
| P1194_#2025m04d30-P1194_V18851_FreeProtocol | xlsx file with no data rows |
| P1207_#2025m05d29-P1207_V18866_FreeProtocol | xlsx file with no data rows |
| P124_#2014m09d25-P124_V16234_FreeProtocol | xlsx file with no data rows |
| P124_#2014m12d05-P124_FreeProtocol | xlsx file with no data rows |
| P132_#2014m10d24-P132_V16241_FreeProtocol | xlsx file with no data rows |
| P132_#2015m02d20-P132_V16281_FreeProtocol | xlsx file with no data rows |
| P145_#2014m11d20-P145_V16255_FreeProtocol | xlsx file with no data rows |
| P145_#2015m03d27-P145_V16291_FreeProtocol | xlsx file with no data rows |
| P152_#2014m12d15-P152_V16265_FreeProtocol | xlsx file with no data rows |
| P164_#2015m02d04-P164_V16279_FreeProtocol | xlsx file with no data rows |
| P164_#2015m10d20-P164_V16364_FreeProtocol | xlsx file with no data rows |
| P164_#2016m01d27-P164_V16413_FreeProtocol | xlsx file with no data rows |
| P164_#2017m12d08-P164_FreeProtocol | xlsx file with no data rows |
| P164_#2018m02d13-P164_V16928_FreeProtocol | xlsx file with no data rows |
| P165_#2015m02d21-P165_V16282_FreeProtocol | xlsx file with no data rows |
| P168_#2015m03d13-P168_V16288_FreeProtocol | xlsx file with no data rows |
| P168_#2015m06d22-P168_V16317_FreeProtocol | xlsx file with no data rows |
| P170_#2015m03d17-P170_V16289_FreeProtocol | xlsx file with no data rows |
| P170_#2015m10d01-P170_V16356_FreeProtocol | xlsx file with no data rows |
| P171_#2015m04d02-P171_FreeProtocol | xlsx file with no data rows |
| P178_#2015m05d06-P178_FreeProtocol | xlsx file with no data rows |
| P180_#2015m05d10-P180_FreeProtocol | xlsx file with no data rows |
| P205_#2015m08d17-P205_FreeProtocol | xlsx file with no data rows |
| P208_#2015m09d14-P208_V16348_FreeProtocol | xlsx file with no data rows |
| P212_#2015m09d28-P212_V16354_FreeProtocol | xlsx file with no data rows |
| P212_#2015m12d21-P212_V16386_FreeProtocol | xlsx file with no data rows |
| P212_#2016m01d11-P212_V16403_FreeProtocol | xlsx file with no data rows |
| P212_#2017m05d09-P212_V16703_FreeProtocol | xlsx file with no data rows |
| P212_#2017m07d27-P212_V16756_FreeProtocol | xlsx file with no data rows |
| P212_#2018m04d10-P212_V16972_FreeProtocol | xlsx file with no data rows |
| P219_#2015m10d30-P219_V16369_FreeProtocol | xlsx file with no data rows |
| P221_#2015m11d05-P221_FreeProtocol | xlsx file with no data rows |
| P221_#2016m06d09-P221_FreeProtocol | xlsx file with no data rows |
| P233_#2016m01d05-P233_V16395_FreeProtocol | xlsx file with no data rows |
| P233_#2016m03d21-P233_V16431_FreeProtocol | xlsx file with no data rows |
| P236_#2016m01d11-P236_V16400_FreeProtocol | xlsx file with no data rows |
| P243_#2016m02d05-P243_V16417_FreeProtocol | xlsx file with no data rows |
| P251_#2021m09d19-P251_V17822_FreeProtocol | xlsx file with no data rows |
| P263_#2016m05d07-P263_FreeProtocol | xlsx file with no data rows |
| P268_#2016m05d27-P268_V16479_FreeProtocol | xlsx file with no data rows |
| P300_#2018m10d14-P300_V17147_FreeProtocol | xlsx file with no data rows |
| P300_#2019m02d16-P300_V17233_FreeProtocol | xlsx file with no data rows |
| P300_#2020m02d22-P300_V17433_FreeProtocol | xlsx file with no data rows |
| P302_#2016m09d20-P302_V16559_FreeProtocol | xlsx file with no data rows |
| P305_#2017m11d04-P305_FreeProtocol | xlsx file with no data rows |
| P305_#2018m04d14-P305_V16977_FreeProtocol | xlsx file with no data rows |
| P305_#2018m05d19-P305_FreeProtocol | xlsx file with no data rows |
| P305_#2018m06d22-P305_FreeProtocol | xlsx file with no data rows |
| P305_#2019m01d27-P305_V17214_FreeProtocol | xlsx file with no data rows |
| P305_#2019m05d03-P305_V17282_FreeProtocol | xlsx file with no data rows |
| P305_#2020m05d17-P305_V17456_FreeProtocol | xlsx file with no data rows |
| P305_#2021m07d16-P305_V17782_FreeProtocol | xlsx file with no data rows |
| P307_#2016m10d02-P307_FreeProtocol | xlsx file with no data rows |
| P307_#2016m11d24-P307_V16589_FreeProtocol | xlsx file with no data rows |
| P325_#2019m09d16-P325_V17357_FreeProtocol | xlsx file with no data rows |
| P325_#2020m08d27-P325_V17517_FreeProtocol | xlsx file with no data rows |
| P325_#2020m09d03-P325_V17526_FreeProtocol | xlsx file with no data rows |
| P325_#2020m09d10-P325_FreeProtocol | xlsx file with no data rows |
| P357_#2017m04d03-P357_FreeProtocol | xlsx file with no data rows |
| P383_#2017m08d24-P383_V16766_FreeProtocol | xlsx file with no data rows |
| P383_#2017m10d31-P383_V16827_FreeProtocol | xlsx file with no data rows |
| P408_#2017m10d20-P408_V16819_FreeProtocol | xlsx file with no data rows |
| P408_#2018m02d18-P408_V16936_FreeProtocol | xlsx file with no data rows |
| P408_#2018m04d15-P408_V16980_FreeProtocol | xlsx file with no data rows |
| P408_#2018m05d27-P408_V17015_FreeProtocol | xlsx file with no data rows |
| P408_#2018m09d09-P408_V17123_FreeProtocol | xlsx file with no data rows |
| P408_#2018m11d06-P408_V17174_FreeProtocol | xlsx file with no data rows |
| P408_#2019m02d05-P408_FreeProtocol | xlsx file with no data rows |
| P408_#2019m07d23-P408_V17323_FreeProtocol | xlsx file with no data rows |
| P421_#2017m11d28-P421_V16860_FreeProtocol | xlsx file with no data rows |
| P423_#2017m12d09-P423_V16865_FreeProtocol | xlsx file with no data rows |
| P447_#2018m02d14-P447_V16929_FreeProtocol | xlsx file with no data rows |
| P450_#2018m02d17-P450_V16933_FreeProtocol | xlsx file with no data rows |
| P450_#2018m09d01-P450_V17114_FreeProtocol | xlsx file with no data rows |
| P458_#2018m03d12-P458_V16948_FreeProtocol | xlsx file with no data rows |
| P458_#2018m06d16-P458_V17034_FreeProtocol | xlsx file with no data rows |
| P486_#2018m05d31-P486_V17020_FreeProtocol | xlsx file with no data rows |
| P487_#2018m06d10-P487_V17030_FreeProtocol | xlsx file with no data rows |
| P489_#2021m03d18-P489_V17694_FreeProtocol | xlsx file with no data rows |
| P490_#2018m06d19-P490_V17044_FreeProtocol | xlsx file with no data rows |
| P494_#2018m06d28-P494_V17055_FreeProtocol | xlsx file with no data rows |
| P499_#2018m07d06-P499_FreeProtocol | xlsx file with no data rows |
| P591_#2019m04d05-P591_V17268_FreeProtocol | xlsx file with no data rows |
| P594_#2019m04d15-P594_V17271_FreeProtocol | xlsx file with no data rows |
| P601_#2019m05d31-P601_V17293_FreeProtocol | xlsx file with no data rows |
| P624_#2019m08d16-P624_V17336_FreeProtocol | xlsx file with no data rows |
| P639_#2019m10d08-P639_V17371_FreeProtocol | xlsx file with no data rows |
| P666_#2020m01d24-P666_V17417_FreeProtocol | xlsx file with no data rows |
| P666_#2020m05d28-P666_V17468_FreeProtocol | xlsx file with no data rows |
| P668_#2020m01d27-P668_V17420_FreeProtocol | xlsx file with no data rows |
| P672_#2020m07d22-P672_V17507_FreeProtocol | xlsx file with no data rows |
| P689_#2020m06d08-P689_FreeProtocol | xlsx file with no data rows |
| P699_#2020m07d15-P699_V17504_FreeProtocol | xlsx file with no data rows |
| P700_#2020m07d18-P700_V17505_FreeProtocol | xlsx file with no data rows |
| P704_#2020m07d28-P704_V17513_FreeProtocol | xlsx file with no data rows |
| P704_#2021m11d04-P704_FreeProtocol | xlsx file with no data rows |
| P704_#2023m12d01-P704_FreeProtocol | xlsx file with no data rows |
| P707_#2020m08d26-P707_V17515_FreeProtocol | xlsx file with no data rows |
| P707_#2020m10d30-P707_V17577_FreeProtocol | xlsx file with no data rows |
| P707_#2021m01d09-P707_FreeProtocol | xlsx file with no data rows |
| P707_#2021m03d20-P707_V17696_FreeProtocol | xlsx file with no data rows |
| P731_#2020m11d09-P731_FreeProtocol | xlsx file with no data rows |
| P733_#2020m11d11-P733_V17586_FreeProtocol | xlsx file with no data rows |
| P741_#2020m11d27-P741_V17598_FreeProtocol | xlsx file with no data rows |
| P74_#2015m06d03-P74_FreeProtocol | xlsx file with no data rows |
| P74_#2016m03d15-P74_V16427_FreeProtocol | xlsx file with no data rows |
| P74_#2016m05d18-P74_V16473_FreeProtocol | xlsx file with no data rows |
| P74_#2016m08d25-P74_V16533_FreeProtocol | xlsx file with no data rows |
| P755_#2021m01d13-P755_V17635_FreeProtocol | xlsx file with no data rows |
| P758_#2021m01d21-P758_FreeProtocol | xlsx file with no data rows |
| P764_#2021m02d08-P764_FreeProtocol | xlsx file with no data rows |
| P770_#2021m02d21-P770_V17666_FreeProtocol | xlsx file with no data rows |
| P770_#2021m06d11-P770_FreeProtocol | xlsx file with no data rows |
| P770_#2021m10d29-P770_V17853_FreeProtocol | xlsx file with no data rows |
| P770_#2022m01d29-P770_V17919_FreeProtocol | xlsx file with no data rows |
| P770_#2022m03d09-P770_V17945_FreeProtocol | xlsx file with no data rows |
| P770_#2022m05d03-P770_FreeProtocol | xlsx file with no data rows |
| P770_#2022m05d12-P770_V18011_FreeProtocol | xlsx file with no data rows |
| P770_#2022m05d29-P770_FreeProtocol | xlsx file with no data rows |
| P770_#2022m06d05-P770_V18027_FreeProtocol | xlsx file with no data rows |
| P782_#2021m03d30-P782_V17705_FreeProtocol | xlsx file with no data rows |
| P787_#2021m04d19-P787_V17713_FreeProtocol | xlsx file with no data rows |
| P787_#2021m09d06-P787_FreeProtocol | xlsx file with no data rows |
| P788_#2021m04d22-P788_V17718_FreeProtocol | xlsx file with no data rows |
| P790_#2021m04d28-P790_V17724_FreeProtocol | xlsx file with no data rows |
| P799_#2021m05d23-P799_V17737_FreeProtocol | xlsx file with no data rows |
| P805_#2021m06d08-P805_FreeProtocol | xlsx file with no data rows |
| P808_#2021m06d14-P808_V17757_FreeProtocol | xlsx file with no data rows |
| P808_#2021m07d14-P808_V17781_FreeProtocol | xlsx file with no data rows |
| P808_#2021m10d15-P808_V17842_FreeProtocol | xlsx file with no data rows |
| P808_#2022m06d14-P808_V18041_FreeProtocol | xlsx file with no data rows |
| P808_#2023m04d23-P808_V18296_FreeProtocol | xlsx file with no data rows |
| P808_#2023m10d03-P808_FreeProtocol | xlsx file with no data rows |
| P80_#2014m04d08-P80_V16201_FreeProtocol | xlsx file with no data rows |
| P817_#2021m07d27-P817_V17788_FreeProtocol | xlsx file with no data rows |
| P81_#2014m04d10-P81_V16202_FreeProtocol | xlsx file with no data rows |
| P81_#2015m02d19-P81_V16280_FreeProtocol | xlsx file with no data rows |
| P81_#2015m08d18-P81_V16344_FreeProtocol | xlsx file with no data rows |
| P827_#2021m09d07-P827_FreeProtocol | xlsx file with no data rows |
| P844_#2021m10d09-P844_FreeProtocol | xlsx file with no data rows |
| P865_#2021m12d02-P865_FreeProtocol | xlsx file with no data rows |
| P865_#2021m12d10-P865_FreeProtocol | xlsx file with no data rows |
| P865_#2022m01d12-P865_V17905_FreeProtocol | xlsx file with no data rows |
| P886_#2022m07d26-P886_V18074_FreeProtocol | xlsx file with no data rows |
| P893_#2022m02d25-P893_V17929_FreeProtocol | xlsx file with no data rows |
| P894_#2022m02d27-P894_V17930_FreeProtocol | xlsx file with no data rows |
| P895_#2026m01d08-P895_FreeProtocol | xlsx file with no data rows |
| P896_#2022m03d07-P896_FreeProtocol | xlsx file with no data rows |
| P905_#2022m04d03-P905_V17976_FreeProtocol | xlsx file with no data rows |
| P90_#2014m05d19-P90_V16212_FreeProtocol | xlsx file with no data rows |
| P90_#2014m11d10-P90_V16249_FreeProtocol | xlsx file with no data rows |
| P95_#2014m06d03-P95_FreeProtocol | xlsx file with no data rows |
| P967_#2022m10d10-P967_V18138_FreeProtocol | xlsx file with no data rows |
| P987_#2025m12d04-P987_FreeProtocol | xlsx file with no data rows |

### Duplicate marker (77 visits)

| visit_id | detail |
|---|---|
| P105_#2014m03d07-P105_V9367_FreeProtocol | Duplicate marker with conflicting values (row 42) |
| P105_#2014m10d15-P105_FreeProtocol | Duplicate marker with conflicting values (row 348) |
| P105_#2015m04d28-P105_V9377_FreeProtocol | Duplicate marker with conflicting values (row 200) |
| P105_#2015m04d28-P105_V9382_FreeProtocol | Duplicate marker with conflicting values (row 172) |
| P105_#2015m04d28-P105_V9387_FreeProtocol | Duplicate marker with conflicting values (row 200) |
| P107_#2014m11d07-P107_V12451_FreeProtocol | Duplicate marker with conflicting values (row 88) |
| P1178_#2025m03d17-P1178_V10307_FreeProtocol | Duplicate marker with conflicting values (row 42) |
| P117_#2014m05d09-P117_V4501_FreeProtocol | Duplicate marker with conflicting values (row 330) |
| P124_#2014m05d12-P124_V3886_FreeProtocol | Duplicate marker with conflicting values (row 337) |
| P132_#2014m10d24-P132_V13912_FreeProtocol | Duplicate marker with conflicting values (row 321) |
| P132_#2014m10d24-P132_V13954_FreeProtocol | Duplicate marker with conflicting values (row 321) |
| P132_#2015m06d06-P132_V13923_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P132_#2015m06d06-P132_V13925_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P132_#2015m06d06-P132_V13965_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P132_#2015m06d06-P132_V13967_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P145_#2014m12d23-P145_FreeProtocol | Duplicate marker with conflicting values (row 440) |
| P145_#2015m08d05-P145_V8516_FreeProtocol | Duplicate marker with conflicting values (row 90) |
| P145_#2015m08d05-P145_V8518_FreeProtocol | Duplicate marker with conflicting values (row 105) |
| P152_#2014m12d15-P152_V8012_FreeProtocol | Duplicate marker with conflicting values (row 246) |
| P152_#2015m03d17-P152_V8021_FreeProtocol | Duplicate marker with conflicting values (row 172) |
| P164_#2015m04d02-P164_V10443_FreeProtocol | Duplicate marker with conflicting values (row 144) |
| P164_#2015m10d20-P164_V10453_FreeProtocol | Duplicate marker with conflicting values (row 113) |
| P164_#2016m01d27-P164_V10463_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P164_#2017m08d12-P164_V10475_FreeProtocol | Duplicate marker with conflicting values (row 116) |
| P168_#2015m03d13-P168_V9602_FreeProtocol | Duplicate marker with conflicting values (row 315) |
| P168_#2015m06d22-P168_V9607_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P170_#2015m03d17-P170_V12239_FreeProtocol | Duplicate marker with conflicting values (row 135) |
| P170_#2015m03d17-P170_V12242_FreeProtocol | Duplicate marker with conflicting values (row 149) |
| P178_#2015m06d05-P178_V2025_FreeProtocol | Duplicate marker with conflicting values (row 196) |
| P178_#2015m06d05-P178_V2028_FreeProtocol | Duplicate marker with conflicting values (row 148) |
| P181_#2015m09d10-P181_V13693_FreeProtocol | Duplicate marker with conflicting values (row 8) |
| P181_#2015m09d10-P181_V13695_FreeProtocol | Duplicate marker with conflicting values (row 3) |
| P208_#2015m09d14-P208_V9297_FreeProtocol | Duplicate marker with conflicting values (row 161) |
| P212_#2015m09d28-P212_V14795_FreeProtocol | Duplicate marker with conflicting values (row 125) |
| P212_#2015m09d28-P212_V14810_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P212_#2016m01d11-P212_V14792_FreeProtocol | Duplicate marker with conflicting values (row 60) |
| P212_#2016m01d11-P212_V14793_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P219_#2015m10d30-P219_V14314_FreeProtocol | Duplicate marker with conflicting values (row 145) |
| P221_#2015m05d11-P221_V12973_FreeProtocol | Duplicate marker with conflicting values (row 36) |
| P233_#2016m03d21-P233_V12133_FreeProtocol | Duplicate marker with conflicting values (row 60) |
| P233_#2016m05d01-P233_V12115_FreeProtocol | Duplicate marker with conflicting values (row 2) |
| P236_#2016m11d01-P236_V12791_FreeProtocol | Duplicate marker with conflicting values (row 100) |
| P236_#2016m11d01-P236_V12792_FreeProtocol | Duplicate marker with conflicting values (row 86) |
| P243_#2016m05d02-P243_V3950_FreeProtocol | Duplicate marker with conflicting values (row 114) |
| P263_#2016m07d05-P263_V15516_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P263_#2016m07d05-P263_V15517_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P300_#2018m10d14-P300_V3365_FreeProtocol | Duplicate marker with conflicting values (row 68) |
| P300_#2018m12d02-P300_V3357_FreeProtocol | Duplicate marker with conflicting values (row 29) |
| P302_#2016m09d20-P302_V12650_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P305_#2019m03d05-P305_V229_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P307_#2016m02d10-P307_V15296_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P325_#2020m10d09-P325_FreeProtocol | Duplicate marker with conflicting values (row 5) |
| P408_#2017m10d20-P408_V13495_FreeProtocol | Duplicate marker with conflicting values (row 85) |
| P421_#2017m11d28-P421_V852_FreeProtocol | Duplicate marker with conflicting values (row 12) |
| P421_#2017m11d28-P421_V855_FreeProtocol | Duplicate marker with conflicting values (row 12) |
| P458_#2018m12d03-P458_V11567_FreeProtocol | Duplicate marker with conflicting values (row 2) |
| P707_#2020m10d30-P707_V15461_FreeProtocol | Duplicate marker with conflicting values (row 28) |
| P707_#2021m09d01-P707_V15466_FreeProtocol | Duplicate marker with conflicting values (row 10) |
| P74_#2014m10d28-P74_V2275_FreeProtocol | Duplicate marker with conflicting values (row 450) |
| P74_#2014m10d28-P74_V2310_FreeProtocol | Duplicate marker with conflicting values (row 450) |
| P74_#2015m03d06-P74_V2324_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P74_#2015m03d06-P74_V2326_FreeProtocol | Duplicate marker with conflicting values (row 148) |
| P74_#2015m03d06-P74_V2386_FreeProtocol | Duplicate marker with conflicting values (row 0) |
| P74_#2015m03d06-P74_V2388_FreeProtocol | Duplicate marker with conflicting values (row 148) |
| P74_#2015m09d15-P74_V2342_FreeProtocol | Duplicate marker with conflicting values (row 50) |
| P74_#2015m09d15-P74_V2399_FreeProtocol | Duplicate marker with conflicting values (row 50) |
| P74_#2016m03d15-P74_V2363_FreeProtocol | Duplicate marker with conflicting values (row 6) |
| P74_#2016m03d15-P74_V2422_FreeProtocol | Duplicate marker with conflicting values (row 6) |
| P755_#2021m03d21-P755_V16082_FreeProtocol | Duplicate marker with conflicting values (row 15) |
| P755_#2021m03d21-P755_V16087_FreeProtocol | Duplicate marker with conflicting values (row 15) |
| P770_#2021m10d29-P770_V3599_FreeProtocol | Duplicate marker with conflicting values (row 35) |
| P770_#2021m10d29-P770_V3675_FreeProtocol | Duplicate marker with conflicting values (row 35) |
| P81_#2015m06d22-P81_V13193_FreeProtocol | Duplicate marker with conflicting values (row 125) |
| P81_#2015m06d22-P81_V13195_FreeProtocol | Duplicate marker with conflicting values (row 2) |
| P81_#2015m08d18-P81_V13206_FreeProtocol | Duplicate marker with conflicting values (row 1) |
| P90_#2014m10d11-P90_V5014_FreeProtocol | Duplicate marker with conflicting values (row 48) |
| P90_#2014m10d11-P90_V5026_FreeProtocol | Duplicate marker with conflicting values (row 168) |
