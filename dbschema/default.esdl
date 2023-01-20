module default {

    abstract type Auditable {
        required property created_at -> datetime {
            readonly := true;
            default := datetime_current();
        };
    }

    abstract type Editable {
        required property last_edit_at -> datetime {
            default := datetime_current();
        }
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

    type ListDraft extending Auditable, Editable {
        required property name -> str {
            constraint max_len_value(64);
        }

        required property draft -> json;

        required link owner -> User;

        multi link draft_items := .<list_draft[is ItemDraft];
    }

    type List extending Auditable, Slugified, Editable {
        required property name -> str {
            constraint max_len_value(64);
        }
        property thumbnail -> str {
            constraint max_len_value(4096);
        }
        property description -> str {
            constraint max_len_value(1024);
        }

        required link owner -> User;

        multi link items := .<list[is Item];
    }

    type ItemDraft extending Auditable, Editable {
        required property name -> str {
            constraint max_len_value(64);
        }

        required property draft -> json;

        required link list_draft -> ListDraft {
            on target delete delete source;
        }
    }

    type Item extending Auditable, Slugified, Editable {
        required property name -> str {
            constraint max_len_value(64);
        }

        property thumbnail -> str {
            constraint max_len_value(4096);
        }

        property description -> str {
            constraint max_len_value(256);
        }

        property price -> float64 {
            constraint min_value(0);
        }

        property max_price -> float64 {
            constraint min_value(0);
        }

        property min_price -> float64 {
            constraint min_value(0);
        }

        property count -> int32 {
            constraint min_value(0);
        }

        property url -> str {
            constraint max_len_value(4096);
        }

        required link list -> List {
            on target delete delete source;
        }

        constraint expression on (
            .min_price < .max_price
        );
        
    }

}
