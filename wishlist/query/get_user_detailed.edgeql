select User {
    name, slug, country_code, created_at, bio, 
    third_party_social_media: {name, url}
    }
filter .slug ilike <str>$slug;