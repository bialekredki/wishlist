select ListDraft {
    name
}
filter .owner.id = <uuid>$uid;