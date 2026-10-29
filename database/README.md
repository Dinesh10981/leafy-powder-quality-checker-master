# 🗄️ Database Layer

The database layer manages persistent structured storage, migrations, seed data, and schema definitions for the Leafy Powder Quality Checker application.

## Directory Structure

```
database/
├── models/
│   ├── __init__.py
│   └── sensor_record.py       # Data structures & schema headers (14 columns)
├── connection/
│   ├── __init__.py
│   └── excel_store.py         # Thread-safe persistent ExcelStore repository
├── queries/
│   ├── __init__.py
│   └── sensor_queries.py      # History pagination, sample numbering, counting
├── migrations/
│   ├── __init__.py
│   └── schema_migration.py    # Auto-migration of table formatting & styling
├── seeds/
│   ├── __init__.py
│   └── seed_samples.py        # Seed dataset generator for testing & dev
├── outputs/
│   └── sensor_data.xlsx       # Active persistent workbook
└── README.md
```

## Schema Overview

The records table stores 14 columns per scan:
1. `Sample No.` (Auto-incrementing integer identifier)
2. `Date` (YYYY-MM-DD)
3. `Time` (HH:MM:SS)
4. `R - 610 nm` (Reflectance / count)
5. `S - 680 nm`
6. `T - 730 nm`
7. `U - 760 nm`
8. `V - 810 nm`
9. `W - 860 nm`
10. `Red-edge avg` (`(S + T) / 2`)
11. `NIR avg` (`(U + V + W) / 3`)
12. `LPQI` (`(NIR - Red-edge) / (NIR + Red-edge)`)
13. `Quality` (`Good`, `Moderate`, or `Poor` based on ML prediction)
14. `Sensor URL` (Source scan origin)
