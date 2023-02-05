CREATE MIGRATION m13v7up5k7z3sqgf25hemgjq2zsqxkverqqtrbircgcwr5edjchmsa
    ONTO m1sdtnf3q4wiucpjosaxvjvp74vkkjghjg5d6uvocjld4xcxthzbkq
{
  ALTER TYPE default::List {
      CREATE REQUIRED LINK owner -> default::User {
          SET REQUIRED USING (std::assert_exists(.owner));
      };
  };
  ALTER TYPE default::ListDraft {
      CREATE REQUIRED LINK owner -> default::User {
          SET REQUIRED USING (std::assert_exists(.owner));
      };
  };
};
