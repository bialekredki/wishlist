select (insert ItemDraft {
    name := <str>$name,
    draft := <json>$draft,
    list_draft := (
        select ListDraft
        filter .id = <uuid>$list_id
        )
}) {
    name,
    draft,
    created_at,
    last_edit_at
}