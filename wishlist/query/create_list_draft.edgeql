select (insert ListDraft {
    name := <str>$name,
    draft := <json>$draft,
    owner := (
        select User filter .id = <uuid>$uid
        )
}) {
    name,
    draft,
    last_edit_at,
    created_at
}
limit 1;