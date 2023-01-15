select (update User
filter .id = <uuid>$uid
set {
    third_party_social_media += (insert ThirdPartySocialMediaUrl {
        name := <str>$name,
        url := <str>$url
    })
}) {
    slug,
    name,
    third_party_social_media
}