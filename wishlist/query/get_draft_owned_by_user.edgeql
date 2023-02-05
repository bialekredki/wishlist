select ListDraft {
    name,
    draft_items: {name, draft, created_at, last_edit_at},
    draft,
    created_at,
    last_edit_at,
    active_list_slug
}
filter .owner.id = <uuid>$uid and .id = <uuid>$id
limit 1;