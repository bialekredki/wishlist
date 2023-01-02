CREATE MIGRATION m15zab23tjxm3lz2f75kymowhnoispcqh7dl2fqeifgpbu5lkhia5q
    ONTO m1l6i6lvluyruulupey3twjcn2wmj6vgp7tpw3co47ta3rbtut4gzq
{
  ALTER TYPE default::User {
      ALTER LINK third_party_social_media {
          ON TARGET DELETE ALLOW;
      };
  };
};
