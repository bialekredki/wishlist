CREATE MIGRATION m1epmwayl4gumt4673yqxycokgacfyvykfzmbincu4aiypeeqbo3xa
    ONTO m1eft3hctovr4vj6xzaz5n3zrhy54w5ujwdcrk323df2rqbwc7ayfq
{
  ALTER TYPE default::ThirdPartySocialMediaUrl {
      ALTER LINK user {
          USING (.<third_party_social_media[IS default::User]);
          RESET CARDINALITY;
      };
  };
};
