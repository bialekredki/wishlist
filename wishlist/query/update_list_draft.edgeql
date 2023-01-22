select(
    update ListDraft
    filter .id = <uuid>$id
    set {
        name := <str>$name,
        draft := <json>$draft,
        last_edit_at := datetime_current()
    }
){
    name,
    draft,
    created_at,
    last_edit_at
};