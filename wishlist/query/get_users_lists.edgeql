select List {
    name,
    slug
}
filter .owner.id = <uuid>$uid;