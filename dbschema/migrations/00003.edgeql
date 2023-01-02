CREATE MIGRATION m1rotgzx3rtv4wclg7zvb66nucwcwo5smqa4lldhi55qir2disqjfq
    ONTO m12tivkkviz4qg7775mnz6hpkyrkjz2te3ur3yxh4kev5txx46l4vq
{
  CREATE ABSTRACT TYPE default::Slugified {
      CREATE REQUIRED PROPERTY slug -> std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(128);
      };
  };
  ALTER TYPE default::User EXTENDING default::Slugified LAST;
  ALTER TYPE default::User {
      ALTER PROPERTY slug {
          ALTER CONSTRAINT std::exclusive {
              DROP OWNED;
          };
      };
  };
  ALTER TYPE default::User {
      ALTER PROPERTY slug {
          RESET OPTIONALITY;
          ALTER CONSTRAINT std::max_len_value(128) {
              DROP OWNED;
          };
          DROP OWNED;
          RESET TYPE;
      };
  };
};
