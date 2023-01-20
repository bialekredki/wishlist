CREATE MIGRATION m1oviite3rv5e4bydyxcmgxn3f2lxgvftk4tewqrlie5mg6h6dvboq
    ONTO m15zab23tjxm3lz2f75kymowhnoispcqh7dl2fqeifgpbu5lkhia5q
{
  CREATE ABSTRACT TYPE default::Editable {
      CREATE REQUIRED PROPERTY last_edit_at -> std::datetime {
          SET default := (std::datetime_current());
      };
  };
  CREATE TYPE default::List EXTENDING default::Auditable, default::Slugified, default::Editable {
      CREATE PROPERTY description -> std::str {
          CREATE CONSTRAINT std::max_len_value(1024);
      };
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::max_len_value(64);
      };
      CREATE PROPERTY thumbnail -> std::str {
          CREATE CONSTRAINT std::max_len_value(4096);
      };
  };
  CREATE TYPE default::Item EXTENDING default::Auditable, default::Slugified, default::Editable {
      CREATE PROPERTY max_price -> std::float64 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE PROPERTY min_price -> std::float64 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE CONSTRAINT std::expression ON ((.min_price < .max_price));
      CREATE REQUIRED LINK list -> default::List;
      CREATE PROPERTY count -> std::int32 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE PROPERTY description -> std::str {
          CREATE CONSTRAINT std::max_len_value(256);
      };
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::max_len_value(64);
      };
      CREATE PROPERTY price -> std::float64 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE PROPERTY thumbnail -> std::str {
          CREATE CONSTRAINT std::max_len_value(4096);
      };
      CREATE PROPERTY url -> std::str {
          CREATE CONSTRAINT std::max_len_value(4096);
      };
  };
  CREATE TYPE default::ListDraft {
      CREATE REQUIRED PROPERTY draft -> std::json;
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::max_len_value(64);
      };
  };
  CREATE TYPE default::ItemDraft {
      CREATE REQUIRED LINK list_draft -> default::ListDraft;
      CREATE REQUIRED PROPERTY draft -> std::json;
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::max_len_value(64);
      };
  };
};
