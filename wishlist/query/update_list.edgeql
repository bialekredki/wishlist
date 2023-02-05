select (update List 
filter .slug = <str>$slug
set {
    name := <str>$name,
    last_edit_at := datetime_current(),
    thumbnail := <optional str>$thumbnail,
    description := <optional str>$description
}) {
    name,
    last_edit_at,
    created_at,
    thumbnail,
    description,
    slug
}
limit 1;