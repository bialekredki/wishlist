CREATE MIGRATION m1eft3hctovr4vj6xzaz5n3zrhy54w5ujwdcrk323df2rqbwc7ayfq
    ONTO m1vjjvsczgpfzild4n5g7bmpjbtdv36hqdkvs537homgxuwl6lgyya
{
  ALTER TYPE default::ThirdPartySocialMediaUrl {
      CREATE MULTI LINK user -> default::User;
  };
};
