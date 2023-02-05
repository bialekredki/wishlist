CREATE MIGRATION m1an6e6xnhhkmxzojj5xrnhhlpykgj7e4t2ffje7prhrizlnixe2aq
    ONTO m13v7up5k7z3sqgf25hemgjq2zsqxkverqqtrbircgcwr5edjchmsa
{
  ALTER TYPE default::List {
      CREATE MULTI LINK items := (.<list[IS default::Item]);
  };
  ALTER TYPE default::ListDraft {
      CREATE MULTI LINK draft_items := (.<list_draft[IS default::ItemDraft]);
  };
};
