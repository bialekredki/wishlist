select List {
    name,
    created_at,
    last_edit_at,
    slug,
    thumbnail,
    description,
    items: {
        thumbnail,
        description,
        name,
        price,
        max_price,
        min_price,
        count,
        url,
        created_at,
        last_edit_at
    },
    owner
}
filter .slug = <str>$slug
limit 1;