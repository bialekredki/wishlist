select List {
    name,
    created_at,
    last_edit_at,
    slug,
    thumbnail,
    description,
    items,
    owner,
    active_draft
}
filter .id = <uuid>$id
limit 1;