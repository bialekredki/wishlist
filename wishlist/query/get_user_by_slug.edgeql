select User {name, slug, country_code, created_at}
filter .slug ilike <str>$slug;