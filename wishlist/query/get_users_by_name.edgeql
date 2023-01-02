select User {name, slug, country_code, created_at}
filter contains(str_lower(.name), str_lower(<str>$name));