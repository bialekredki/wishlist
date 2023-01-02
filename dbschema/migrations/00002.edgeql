CREATE MIGRATION m12tivkkviz4qg7775mnz6hpkyrkjz2te3ur3yxh4kev5txx46l4vq
    ONTO m1poy76grq274nenpcxvfiez7b422zerhb5shquumvxepvl5rxui6q
{
  ALTER TYPE default::User {
      CREATE PROPERTY country_code -> std::str {
          CREATE CONSTRAINT std::max_len_value(4);
      };
      CREATE REQUIRED PROPERTY email -> std::str {
          SET REQUIRED USING ('test@test.test');
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(128);
      };
      CREATE REQUIRED PROPERTY password_hash -> std::str {
          SET REQUIRED USING ('xd');
          CREATE CONSTRAINT std::max_len_value(128);
      };
  };
};
