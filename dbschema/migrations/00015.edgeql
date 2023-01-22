CREATE MIGRATION m1tp4irux2xwsiiipinorknoi3hf2utqge3vffjy6eah2ratf6d3iq
    ONTO m1qslnlbh73vsn7ur3yuzp4pbtvuyw3lasuz6ep43hgpi3xhniptfq
{
  ALTER TYPE default::Item DROP EXTENDING default::Slugified;
  ALTER TYPE default::List {
      ALTER PROPERTY description {
          DROP CONSTRAINT std::max_len_value(1024);
      };
  };
  ALTER TYPE default::List {
      ALTER PROPERTY description {
          CREATE CONSTRAINT std::max_len_value(256);
      };
  };
};
