select ItemDraft {
    name,
    draft,
    last_edit_at,
    created_at,
    list_draft: {name, owner}
}
filter .id = <uuid>$id
limit 1;