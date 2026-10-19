Template review and suggested changes

Summary
- I inspected the templates in templates/*.html and the views that render them.
- The main template performance risk was N+1 queries when templates access related objects that were not preloaded by the view. After modifying the app to aggregate totals with grouped queries, most of that risk is reduced.

Findings
1) reports.html and dashboard.html receive model objects (Crop instances) and totals. Accessing simple attributes like crop.name is cheap, but accessing relationships (e.g., crop.activities) inside templates may trigger lazy-load queries if not preloaded.

2) records.html and other list templates iterate over lists passed from views. If the view passes ORM objects and the template accesses related collections, you can get extra queries.

Recommendations
- Prefer passing simple dicts/primitives from views into templates instead of live ORM objects when possible. This eliminates accidental lazy-loading in templates.

Suggested change (reports view)
- Instead of passing `crop` model objects to the template, pass a serializable dict for each row. Example (in app.py, view):

    # current approach (works, but may lazy-load if template accesses related properties)
    rows.append({"crop": crop, "cost": cost, "revenue": revenue, "profit": revenue-cost})

    # suggested safer approach
    rows.append({
        "id": crop.id,
        "name": crop.name,
        "status": crop.status,
        "cost": cost,
        "revenue": revenue,
        "profit": revenue - cost,
    })

- Update the template to use row.name instead of row.crop.name.

Extra tips
- If you want to keep passing ORM objects, use eager loading in the view when you know the template will access relationships:

    from sqlalchemy.orm import selectinload
    crops = Crop.query.options(selectinload(Crop.some_relationship)).filter_by(user_id=...).all()

- Add fragment caching for heavy-report pages using Flask-Caching + Redis if the data does not need to be real-time.

If you want, I can apply the safer approach and update the reports template and any other templates to use primitive row dicts instead of model objects. Reply `apply templates` to let me modify the templates and corresponding view code.
