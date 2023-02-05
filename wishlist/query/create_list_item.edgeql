select (insert Item {
    name := <str>$name,
    thumbnail := <optional str>$thumbnail,
    description := <optional str>$description,
    price := <optional float64>$price,
    max_price := <optional float64>$max_price,
    min_price := <optional float64>$min_price,
    count := <optional int32>$count,
    url := <optional str>$url,
    list := (
        select List
        filter .id = <uuid>$list_id
        )
}) {
    name,
    thumbnail,
    price,
    max_price,
    min_price,
    description,
    count,
    url,
    created_at,
    last_edit_at
};