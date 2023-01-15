select (
    insert AllowedSocialMedia {
        name := <str>$name,
        domain := <str>$domain
    }
) {
    name,
    domain
};