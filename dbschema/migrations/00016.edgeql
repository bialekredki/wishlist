CREATE MIGRATION m1dyxpx5n2gheachkvdqsmo6pagvvhfg76hy2cpeb33qowimx3c2vq
    ONTO m1tp4irux2xwsiiipinorknoi3hf2utqge3vffjy6eah2ratf6d3iq
{
  ALTER TYPE default::ListDraft {
      CREATE SINGLE LINK active_list -> default::List {
          ON TARGET DELETE DELETE SOURCE;
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::List {
      CREATE SINGLE LINK active_draft := (.<active_list[IS default::ListDraft]);
  };
};
