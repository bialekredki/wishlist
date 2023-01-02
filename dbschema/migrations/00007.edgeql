CREATE MIGRATION m1gpyyd56frdk25kcssfetobozp53mzjjkwcy6ownpstzzbi7p35vq
    ONTO m1epmwayl4gumt4673yqxycokgacfyvykfzmbincu4aiypeeqbo3xa
{
  CREATE TYPE default::AllowedSocialMedia {
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(32);
      };
  };
};
