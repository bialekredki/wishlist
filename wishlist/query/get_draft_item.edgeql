select ItemDraft {
    name,
    draft,
    list_draft: {name, owner}
}
filter .id = <uuid>$id;