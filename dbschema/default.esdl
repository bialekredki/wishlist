module default {

    abstract type Auditable {
        required property created_at -> datetime {
            readonly := true;
            default := datetime_current();
        };
    }

    abstract type Slugified {
        required property slug -> str {
            constraint exclusive;
            constraint max_len_value(128);
        };
    }

    type User extending Auditable, Slugified {
        required property name -> str {
            constraint max_len_value(128);
        };
        required property email -> str {
            constraint exclusive;
            constraint max_len_value(128);
        };
        required property password_hash -> str {
            constraint max_len_value(128);
        };
        property country_code -> str {
            constraint max_len_value(4);
        };
        property bio -> str {
            constraint max_len_value(512);
        }

        multi link third_party_social_media -> ThirdPartySocialMediaUrl {
            on source delete delete target;
            on target delete allow;
        }
    }

    type ThirdPartySocialMediaUrl extending Auditable {
        required property name -> str {
            constraint max_len_value(32);
        }
        required property url -> str {
            constraint max_len_value(256);
        }

        link user := .<third_party_social_media[is User]
    }

    type AllowedSocialMedia {
        required property name -> str {
            constraint exclusive;
            constraint max_len_value(32);
        }
        required property domain -> str {
            constraint exclusive;
            constraint max_len_value(32);
        }
    }

}
