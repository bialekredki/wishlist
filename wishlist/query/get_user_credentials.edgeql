select User {email, password_hash, slug}
filter .email = <str>$email;