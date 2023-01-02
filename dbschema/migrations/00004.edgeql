CREATE MIGRATION m1vjjvsczgpfzild4n5g7bmpjbtdv36hqdkvs537homgxuwl6lgyya
    ONTO m1rotgzx3rtv4wclg7zvb66nucwcwo5smqa4lldhi55qir2disqjfq
{
  CREATE TYPE default::ThirdPartySocialMediaUrl EXTENDING default::Auditable {
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::max_len_value(32);
      };
      CREATE REQUIRED PROPERTY url -> std::str {
          CREATE CONSTRAINT std::max_len_value(256);
      };
  };
  ALTER TYPE default::User {
      CREATE MULTI LINK third_party_social_media -> default::ThirdPartySocialMediaUrl {
          ON SOURCE DELETE DELETE TARGET;
      };
      CREATE PROPERTY bio -> std::str {
          CREATE CONSTRAINT std::max_len_value(512);
      };
  };
};
