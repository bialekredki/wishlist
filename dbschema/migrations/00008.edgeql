CREATE MIGRATION m1l6i6lvluyruulupey3twjcn2wmj6vgp7tpw3co47ta3rbtut4gzq
    ONTO m1gpyyd56frdk25kcssfetobozp53mzjjkwcy6ownpstzzbi7p35vq
{
  ALTER TYPE default::AllowedSocialMedia {
      CREATE REQUIRED PROPERTY domain -> std::str {
          SET REQUIRED USING ('https://example.com');
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(32);
      };
  };
};
