select (insert ListDraft {
    name := <str>$name,
    draft := <json>$draft,
    owner := (
        select User filter .id = <uuid>$uid
        ),
    active_list := (
        select List filter .slug = <optional str>$list_slug
    )
}) {
    name,
    draft,
    last_edit_at,
    created_at
}
limit 1;