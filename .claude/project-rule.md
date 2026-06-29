### Project structure
```text
PdfGenerator/
├── app/
│   ├── core/           # config, database, logging, dependencies
│   ├── api/            # dependencies, schemas, responses
│   ├── routers/        # API route files (pdf.py, auth.py, etc.)
│   ├── services/       # Business logic (PDF generation logic)
│   ├── models/         # Pydantic models / schemas
│   ├── templates/      # HTML templates (for WeasyPrint)
│   ├── static/         # CSS, images, fonts
│   └── utils/          # helpers, validators, converters
├── tests/              # unit + integration tests
├── main.py
├── requirements.txt
├── .env                # (never commit)
├── .gitignore
├── README.md
└── alembic/            # (if you add database later)
```



### Response structure

```json
{
  "success": true,
  "data": {...},
  "message": "PDF generated successfully",
  "error": null
}
```