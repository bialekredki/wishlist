select (insert List {
    name := <str>$name,
    thumbnail := <optional str>$thumbnail,
    description := <optional str>$description,
    slug := <str>$slug,
    owner := (
        select User filter .id = <uuid>$uid
        )
}) {
    name,
    items,
    last_edit_at,
    created_at,
    thumbnail,
    description,
    slug
}
limit 1;