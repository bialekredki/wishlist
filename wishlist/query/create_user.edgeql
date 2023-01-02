select (insert User {
    name := <str>$name,
    email := <str>$email,
    password_hash := <str>$password_hash,
    slug := <str>$slug
}) {
    name,
    slug,
    created_at,
};