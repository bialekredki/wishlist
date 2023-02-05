CREATE MIGRATION m1qslnlbh73vsn7ur3yuzp4pbtvuyw3lasuz6ep43hgpi3xhniptfq
    ONTO m1an6e6xnhhkmxzojj5xrnhhlpykgj7e4t2ffje7prhrizlnixe2aq
{
  ALTER TYPE default::Item {
      ALTER LINK list {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
  ALTER TYPE default::ItemDraft {
      ALTER LINK list_draft {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
};
